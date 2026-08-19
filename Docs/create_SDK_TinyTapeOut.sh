#!/usr/bin/env bash
# Recreate the Tiny Tapeout SKY25b development environment used by tt_um_femto.
#
# Historical inputs recovered from the successful workflow run #33:
#   project commit:          baab83f5b7fe16083744b88fc54fe699873517e1
#   tt-gds-action snapshot:  1f1ff64b7136b7799d937303aa6855f9c66324aa
#   tt-support-tools:        690a4c847059646d8c2a5c1da263dfd7175568e3
#   LibreLane:               2.4.2 (commit 4dc53448d98f3688e0096873a88200b04d268c6c)
#   Open PDKs revision:      0fe599b2afb6708d281543108caf8310912f54af
#   PDK:                     sky130A
#
# Usage:
#   ./create_SDK_TinyTapeOut.sh docker setup
#   ./create_SDK_TinyTapeOut.sh docker run
#   ./create_SDK_TinyTapeOut.sh docker all
#   ./create_SDK_TinyTapeOut.sh native setup
#   ./create_SDK_TinyTapeOut.sh native run
#   ./create_SDK_TinyTapeOut.sh native all
#
# Optional environment variables:
#   TT_SDK_ROOT=/path       SDK destination (default: ~/ttsky25b-sdk/<mode>)
#   TT_PROJECT_DIR=/path    use an existing Tiny Tapeout project checkout
#   TT_INSTALL_DEPS=0       do not install missing OS packages/Docker/Nix
#
# Supported host for automatic installation: Ubuntu or Debian x86_64 Linux.

set -Eeuo pipefail

readonly PROJECT_REPO="https://github.com/cicamargoba/femto_UN.git"
readonly PROJECT_COMMIT="baab83f5b7fe16083744b88fc54fe699873517e1"
readonly TT_TOOLS_REPO="https://github.com/TinyTapeout/tt-support-tools.git"
readonly TT_TOOLS_COMMIT="690a4c847059646d8c2a5c1da263dfd7175568e3"
readonly LIBRELANE_REPO="https://github.com/efabless/openlane2.git"
readonly LIBRELANE_COMMIT="4dc53448d98f3688e0096873a88200b04d268c6c"
readonly LIBRELANE_VERSION="2.4.2"
readonly OPEN_PDKS_REV="0fe599b2afb6708d281543108caf8310912f54af"
readonly PDK="sky130A"

MODE="${1:-}"
ACTION="${2:-setup}"
INSTALL_DEPS="${TT_INSTALL_DEPS:-1}"

usage() {
    cat <<'EOF'
Create the Tiny Tapeout SKY25b SDK for tt_um_femto.

Usage:
  create_SDK_TinyTapeOut.sh <docker|native> [setup|run|all|info]

Modes:
  docker   Reproduces the original GitHub Action: LibreLane runs in Docker.
  native   Runs the same LibreLane flow without Docker, using a Nix shell.

Actions:
  setup    Install/check dependencies and prepare the SDK (default).
  run      Run hardening using an SDK prepared previously.
  all      Perform setup and then run hardening.
  info     Print paths and pinned versions without making changes.

Examples:
  ./create_SDK_TinyTapeOut.sh docker all
  ./create_SDK_TinyTapeOut.sh native setup
  TT_PROJECT_DIR=/work/my_project ./create_SDK_TinyTapeOut.sh native run
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

log() {
    printf '\n==> %s\n' "$*"
}

if [[ "$MODE" != "docker" && "$MODE" != "native" ]]; then
    usage
    exit 2
fi

case "$ACTION" in
    setup|run|all|info) ;;
    *) usage; exit 2 ;;
esac

SDK_ROOT="${TT_SDK_ROOT:-$HOME/ttsky25b-sdk/$MODE}"
PROJECT_DIR="${TT_PROJECT_DIR:-$SDK_ROOT/femto_UN}"
VENV_DIR="$SDK_ROOT/venv"
PDK_ROOT="$SDK_ROOT/pdk"
LIBRELANE_DIR="$SDK_ROOT/librelane-2.4.2"

print_info() {
    cat <<EOF
Mode:                 $MODE
SDK root:             $SDK_ROOT
Project:              $PROJECT_DIR
Project commit:       $PROJECT_COMMIT
tt-support-tools:     $TT_TOOLS_COMMIT
LibreLane:            $LIBRELANE_VERSION ($LIBRELANE_COMMIT)
Open PDKs revision:   $OPEN_PDKS_REV
PDK:                  $PDK
Expected run output:  $PROJECT_DIR/runs/wokwi
Expected submission:  $PROJECT_DIR/tt_submission
EOF
}

[[ "$ACTION" == "info" ]] && { print_info; exit 0; }

check_host() {
    [[ "$(uname -s)" == "Linux" ]] || die "this script currently supports Linux only"
    [[ "$(uname -m)" == "x86_64" ]] || die "automatic setup currently requires x86_64"
    [[ -r /etc/os-release ]] || die "cannot identify the Linux distribution"
    # shellcheck disable=SC1091
    source /etc/os-release
    case "${ID:-}" in
        ubuntu|debian) ;;
        *) die "automatic dependency installation supports Ubuntu/Debian; set TT_INSTALL_DEPS=0 after installing dependencies manually" ;;
    esac
}

apt_install_common() {
    command -v sudo >/dev/null || die "sudo is required to install OS packages"
    log "Installing common host packages"
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates curl git gnupg jq make python3 python3-pip python3-venv \
        build-essential libffi-dev libssl-dev librsvg2-bin pngquant xz-utils
}

install_docker() {
    if command -v docker >/dev/null; then
        return
    fi
    [[ "$INSTALL_DEPS" == "1" ]] || die "Docker is not installed"

    # shellcheck disable=SC1091
    source /etc/os-release
    log "Installing Docker Engine from Docker's official repository"
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL "https://download.docker.com/linux/$ID/gpg" | \
        sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/%s %s stable\n' \
        "$(dpkg --print-architecture)" "$ID" "$VERSION_CODENAME" | \
        sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
        docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker "$USER"
    die "Docker was installed and $USER was added to group 'docker'. Log out and back in, then rerun this script"
}

check_docker_access() {
    docker info >/dev/null 2>&1 || die "Docker is installed but unavailable to this user. Start Docker and verify membership in group 'docker'"
}

load_nix_profile() {
    if [[ -e /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]]; then
        # shellcheck disable=SC1091
        source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
    elif [[ -e "$HOME/.nix-profile/etc/profile.d/nix.sh" ]]; then
        # shellcheck disable=SC1090
        source "$HOME/.nix-profile/etc/profile.d/nix.sh"
    fi
}

install_nix() {
    load_nix_profile
    if command -v nix-shell >/dev/null; then
        return
    fi
    [[ "$INSTALL_DEPS" == "1" ]] || die "Nix is not installed"

    log "Installing Nix for the Docker-free LibreLane toolchain"
    curl -fsSL https://nixos.org/nix/install -o "$SDK_ROOT/install-nix.sh"
    sh "$SDK_ROOT/install-nix.sh" --daemon --yes
    load_nix_profile
    command -v nix-shell >/dev/null || die "Nix was installed but is not active; open a new terminal and rerun the script"
}

configure_nix_cache() {
    local nix_conf="/etc/nix/nix.conf"
    local cache="https://nix-cache.fossi-foundation.org"
    local key="nix-cache.fossi-foundation.org:3+K59iFwXqKsL7BNu6Guy0v+uTlwsxYQxjspXzqLYQs="

    if [[ -r "$nix_conf" ]] && grep -qF "$cache" "$nix_conf"; then
        return
    fi
    [[ "$INSTALL_DEPS" == "1" ]] || return

    log "Enabling LibreLane's FOSSi Nix binary cache"
    {
        printf '\n# LibreLane/FOSSi EDA cache\n'
        printf 'extra-substituters = %s\n' "$cache"
        printf 'extra-trusted-public-keys = %s\n' "$key"
        printf 'extra-experimental-features = nix-command flakes\n'
    } | sudo tee -a "$nix_conf" >/dev/null
    sudo systemctl restart nix-daemon.service 2>/dev/null || true
}

clone_at_commit() {
    local repo="$1"
    local commit="$2"
    local destination="$3"

    if [[ -d "$destination/.git" ]]; then
        git -C "$destination" cat-file -e "$commit^{commit}" 2>/dev/null || \
            git -C "$destination" fetch --quiet origin "$commit"
        return
    fi
    [[ ! -e "$destination" ]] || die "$destination exists but is not a Git checkout"
    git clone "$repo" "$destination"
    git -C "$destination" checkout --detach "$commit"
}

prepare_project() {
    if [[ -n "${TT_PROJECT_DIR:-}" ]]; then
        [[ -d "$PROJECT_DIR/.git" ]] || die "TT_PROJECT_DIR must point to a Git checkout"
        [[ -f "$PROJECT_DIR/info.yaml" ]] || die "$PROJECT_DIR is not a Tiny Tapeout project"
        log "Using existing project without changing its branch or files: $PROJECT_DIR"
    else
        clone_at_commit "$PROJECT_REPO" "$PROJECT_COMMIT" "$PROJECT_DIR"
        git -C "$PROJECT_DIR" checkout --detach "$PROJECT_COMMIT"
    fi

    if [[ ! -d "$PROJECT_DIR/tt/.git" ]]; then
        [[ ! -e "$PROJECT_DIR/tt" ]] || die "$PROJECT_DIR/tt exists but is not a Git checkout"
        clone_at_commit "$TT_TOOLS_REPO" "$TT_TOOLS_COMMIT" "$PROJECT_DIR/tt"
    else
        git -C "$PROJECT_DIR/tt" cat-file -e "$TT_TOOLS_COMMIT^{commit}" 2>/dev/null || \
            git -C "$PROJECT_DIR/tt" fetch --quiet origin "$TT_TOOLS_COMMIT"
        git -C "$PROJECT_DIR/tt" checkout --detach "$TT_TOOLS_COMMIT"
    fi
}

prepare_python() {
    log "Creating Python virtual environment"
    python3 -m venv "$VENV_DIR"
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    python -m pip install --upgrade pip wheel
    python -m pip install -r "$PROJECT_DIR/tt/requirements.txt"
    python -m pip install "librelane==$LIBRELANE_VERSION"
    python -m librelane --version
}

prepare_native_librelane() {
    clone_at_commit "$LIBRELANE_REPO" "$LIBRELANE_COMMIT" "$LIBRELANE_DIR"
    git -C "$LIBRELANE_DIR" checkout --detach "$LIBRELANE_COMMIT"

    # tt-support-tools 690a4c8 always adds --dockerized. Remove only that
    # execution switch in this isolated native SDK copy; flow configuration,
    # metadata generation and output handling remain unchanged.
    python3 - "$PROJECT_DIR/tt/project.py" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text()
old = "--docker-no-tty --dockerized "
count = text.count(old)
if count not in (0, 2):
    raise SystemExit(f"unexpected tt-support-tools format: found {count} Docker switches")
if count:
    path.with_suffix(".py.docker-original").write_text(text)
    path.write_text(text.replace(old, ""))
PY
}

setup_sdk() {
    check_host
    mkdir -p "$SDK_ROOT"
    if [[ "$INSTALL_DEPS" == "1" ]]; then
        apt_install_common
    else
        for command_name in git curl python3; do
            command -v "$command_name" >/dev/null || die "missing command: $command_name"
        done
    fi

    prepare_project
    prepare_python

    if [[ "$MODE" == "docker" ]]; then
        install_docker
        check_docker_access
    else
        install_nix
        configure_nix_cache
        prepare_native_librelane
    fi

    log "SDK setup complete"
    print_info
}

run_docker_flow() {
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    export PDK_ROOT PDK
    check_docker_access
    cd "$PROJECT_DIR"
    ./tt/tt_tool.py --create-user-config
    ./tt/tt_tool.py --harden
}

run_native_flow() {
    load_nix_profile
    command -v nix-shell >/dev/null || die "Nix is unavailable; run '$0 native setup' first"
    [[ -f "$LIBRELANE_DIR/shell.nix" ]] || die "LibreLane Nix environment is missing; run setup first"

    local native_command
    printf -v native_command \
        'source %q && export PDK_ROOT=%q PDK=%q && ciel enable --pdk sky130 --pdk-root "$PDK_ROOT" %q && cd %q && ./tt/tt_tool.py --create-user-config && ./tt/tt_tool.py --harden' \
        "$VENV_DIR/bin/activate" "$PDK_ROOT" "$PDK" "$OPEN_PDKS_REV" "$PROJECT_DIR"

    nix-shell "$LIBRELANE_DIR/shell.nix" --run "$native_command"
}

postprocess_run() {
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    export PDK_ROOT PDK
    cd "$PROJECT_DIR"
    ./tt/tt_tool.py --print-warnings || true
    ./tt/tt_tool.py --print-stats || true
    ./tt/tt_tool.py --create-tt-submission

    log "Hardening complete"
    printf 'Run directory: %s\n' "$PROJECT_DIR/runs/wokwi"
    printf 'Final GDS:     %s\n' "$PROJECT_DIR/runs/wokwi/final/gds/tt_um_femto.gds"
    printf 'Submission:    %s\n' "$PROJECT_DIR/tt_submission"
}

run_flow() {
    [[ -x "$VENV_DIR/bin/python" ]] || die "SDK is not prepared; run '$0 $MODE setup' first"
    [[ -x "$PROJECT_DIR/tt/tt_tool.py" ]] || die "tt-support-tools is missing; run setup first"

    log "Running Tiny Tapeout hardening in $MODE mode"
    if [[ "$MODE" == "docker" ]]; then
        run_docker_flow
    else
        run_native_flow
    fi
    postprocess_run
}

case "$ACTION" in
    setup) setup_sdk ;;
    run)   run_flow ;;
    all)   setup_sdk; run_flow ;;
esac
