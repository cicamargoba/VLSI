# Instalación de Herramientas – Flujo ASIC

Este documento recoge los pasos para instalar las herramientas utilizadas para trabajar con en el flujo de diseño ASIC 
## 1. Yosys

Yosys es un framework para síntesis Verilog-RTL con soporte para Verilog‑2005 y diversas capacidades de síntesis.

### Pasos de instalación:

```bash
git clone https://github.com/YosysHQ/yosys.git
cd yosys
sudo apt install make
sudo apt-get install build-essential clang bison flex \
    libreadline-dev gawk tcl-dev libffi-dev git \
    graphviz xdot pkg-config python3 libboost-system-dev \
    libboost-python-dev libboost-filesystem-dev zlib1g-dev
make config-gcc
make
sudo make install
```

---

## 2. Icarus Verilog

Icarus Verilog es un compilador Verilog que genera netlists y soporta múltiples estándares.

### Instalación:

```bash
sudo apt-get install iverilog
```

---

## 3. GTKWave

GTKWave es un visualizador de ondas (waveform) compatible con formatos comunes como VCD.

### Instalación:

```bash
sudo apt install gtkwave
```

---

## 4. ngspice

ngspice es un simulador SPICE de código abierto para circuitos analógicos, digitales y mixtos.

### Pasos de instalación (compilación desde fuente):

```bash
# Dependencias
sudo apt-get install build-essential
sudo apt-get install libxaw7-dev

# Instalación
tar -zxvf ngspice-40.tar.gz
cd ngspice-40
mkdir release
cd release
../configure --with-x --with-readline=yes --disable-debug
make
sudo make install
```

---

## 5. OpenSTA

OpenSTA es un verificador de timing estático (Static Timing Analysis) para gates.

### Pasos de instalación:

```bash
sudo apt-get install cmake clang gcc tcl swig bison flex

git clone https://github.com/The-OpenROAD-Project/OpenSTA.git
cd OpenSTA
mkdir build
cd build
cmake ..
make
sudo make install
```

---

## 6. Magic

Magic es una herramienta de EDA para diseño físico basado en VLSI desarrollada inicialmente en UC Berkeley.

### Instalación:

```bash
sudo apt-get install m4
sudo apt-get install tcsh
sudo apt-get install csh
sudo apt-get install libx11-dev
sudo apt-get install tcl-dev tk-dev
sudo apt-get install libcairo2-dev
sudo apt-get install mesa-common-dev libglu1-mesa-dev
sudo apt-get install libncurses-dev

git clone https://github.com/RTimothyEdwards/magic
cd magic
./configure
make
sudo make install
```

---

## 7. OpenLane

OpenLane es un flujo automatizado que abarca desde RTL hasta GDSII, integrando herramientas como OpenROAD, Yosys, Magic, Netgen, KLayout, entre otras.

### Instalación de dependencias:

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt install -y build-essential python3 python3-venv python3-pip make git
```

### Instalación de Docker (requisito para algunas partes del flujo):

```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

sudo docker run hello-world
sudo groupadd docker
sudo usermod -aG docker $USER
sudo reboot
# Después del reinicio:
sudo docker run hello-world
```

### Clonar e instalar OpenLane y PDKs:

```bash
cd $HOME
git clone https://github.com/The-OpenROAD-Project/OpenLane
cd OpenLane
make
make test
```

---

## 8. Recrear el SDK de Tiny Tapeout SKY25b

El script `Docs/create_SDK_TinyTapeOut.sh` reconstruye el entorno usado para
fabricar `tt_um_femto`. Está preparado para Ubuntu o Debian Linux x86-64 y
fija las versiones históricas del proyecto, LibreLane 2.4.2, `sky130A`, Open
PDKs y `tt-support-tools`.

Sintaxis:

```bash
./Docs/create_SDK_TinyTapeOut.sh <docker|native> [setup|run|all|info]
```

Modos:

- `docker`: reproduce el flujo original de GitHub Actions usando Docker.
- `native`: ejecuta LibreLane sin Docker mediante un entorno Nix.

Acciones:

- `setup`: instala o verifica dependencias y prepara el SDK.
- `run`: ejecuta el hardening sobre un SDK preparado previamente.
- `all`: prepara el SDK y ejecuta el hardening.
- `info`: muestra rutas y versiones sin modificar el sistema.

Consultar la configuración que utilizará el script:

```bash
./Docs/create_SDK_TinyTapeOut.sh docker info
./Docs/create_SDK_TinyTapeOut.sh native info
```

Preparar el SDK y ejecutar todo el flujo:

```bash
# Flujo con Docker
./Docs/create_SDK_TinyTapeOut.sh docker all

# Flujo sin Docker
./Docs/create_SDK_TinyTapeOut.sh native all
```

También se pueden ejecutar la preparación y el hardening por separado:

```bash
./Docs/create_SDK_TinyTapeOut.sh docker setup
./Docs/create_SDK_TinyTapeOut.sh docker run

./Docs/create_SDK_TinyTapeOut.sh native setup
./Docs/create_SDK_TinyTapeOut.sh native run
```

Variables opcionales:

```bash
# Cambiar el directorio de instalación del SDK
TT_SDK_ROOT=/ruta/al/sdk ./Docs/create_SDK_TinyTapeOut.sh docker all

# Ejecutar sobre un checkout existente del proyecto
TT_PROJECT_DIR=/ruta/al/proyecto ./Docs/create_SDK_TinyTapeOut.sh docker run

# No instalar automáticamente dependencias del sistema
TT_INSTALL_DEPS=0 ./Docs/create_SDK_TinyTapeOut.sh docker setup
```

Rutas de salida predeterminadas en modo Docker:

```text
~/ttsky25b-sdk/docker/femto_UN/runs/wokwi
~/ttsky25b-sdk/docker/femto_UN/tt_submission
```

En modo `native`, `docker` se reemplaza por `native` en estas rutas. Si el
script instala Docker o Nix y solicita iniciar una sesión nueva, se debe abrir
otra terminal y ejecutar nuevamente el mismo comando.

---

## 9. Simulación del netlist fabricado de `tt_um_femto`

Los archivos preparados para la simulación del netlist final se encuentran en:

- Netlist post-layout: `tinytapeout/tt_um_femto.v`
- Testbench: `tinytapeout/tt_um_femto_TB.v`
- Reglas de compilación y ejecución: `tinytapeout/Makefile`

Ejecutar desde la raíz del repositorio:

```bash
cd tinytapeout
make tt_um_femto
```

El target compila el netlist con `USE_POWER_PINS`, `FUNCTIONAL` y
`UNIT_DELAY`, ejecuta el testbench y abre `tt_um_femto_TB.vcd` en GTKWave.

---

## 10. Análisis de bugs SPI en `tt_um_femto`

El diseño fabricado presenta tres bugs en las interfaces SPI:

### Bug 1: 65 flancos de SCK y skew CS_N/SCK

`MappedSPIFlash` genera 65 flancos de SCK mientras CS_N está bajo. El modelo
`spiflash.v` muestrea en **negedge** SCK y descarta el bit 65 incompleto. La
flash física muestrea en **posedge** SCK. Cuando CS_N baja simultáneamente con
SCK (transacciones 1 y 2), el setup es casi nulo y la flash lee 0x06 (WREN) en
lugar de 0x03 (READ). Desde la transacción 3, SCK está estable y la flash lee
correctamente 0x03.

### Bug 2: Captura de 31 bits en lectura RAM

`MappedSPIRAM` termina cuando `rcv_bitcount <= 1`, ejecutando solo 31 shifts.
El bit 31 de `rcv_data` retiene el valor de la lectura anterior.

### Bug 3: WRITE sin WREN en RAM

`MappedSPIRAM` envía WRITE 0x02 sin el comando WREN 0x06 previo. El modelo
`spiram.v` fuerza WEL=1 artificialmente, ocultando el bug. La FRAM física
ignora la escritura.

### Documentación y diagramas

- Análisis detallado: `tinytapeout/bugs_MappedSPIFlash.md`
- Diagrama flash: `tinytapeout/spi_flash_vcd_findings.svg`
- Diagrama RAM: `tinytapeout/spi_ram_vcd_findings.svg`
- Comparación Tx1 vs Tx3: `tinytapeout/spi_flash_tx_comparison.svg`
- Tres lecturas en secuencia: `tinytapeout/spi_flash_3reads.svg`

---

## Referencias

- [Repositorio original: Introduction to ASIC Flow](https://github.com/KanishR1/Introduction-to-ASIC-Flow)
- [Pagina Web YOSYS](https://yosyshq.net/yosys/)
- [Github Icarus verilog](https://steveicarus.github.io/iverilog/)
- [Github OPENSTA](https://github.com/The-OpenROAD-Project/OpenSTA)
- [Pagina Web GTKWAVE](https://gtkwave.sourceforge.net/)
- [Github OpenLane](https://github.com/The-OpenROAD-Project/OpenLane)
- [Pagina Ngspice](https://ngspice.sourceforge.io/)
- [Github OpenPDK](https://github.com/RTimothyEdwards/open_pdks)
