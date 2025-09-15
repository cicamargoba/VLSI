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


## Referencias

- [Repositorio original: Introduction to ASIC Flow](https://github.com/KanishR1/Introduction-to-ASIC-Flow)
- [Pagina Web YOSYS](https://yosyshq.net/yosys/)
- [Github Icarus verilog](https://steveicarus.github.io/iverilog/)
- [Github OPENSTA](https://github.com/The-OpenROAD-Project/OpenSTA)
- [Pagina Web GTKWAVE](https://gtkwave.sourceforge.net/)
- [Github OpenLane](https://github.com/The-OpenROAD-Project/OpenLane)
- [Pagina Ngspice](https://ngspice.sourceforge.io/)
- [Github OpenPDK](https://github.com/RTimothyEdwards/open_pdks)
