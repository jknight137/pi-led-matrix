# pi-led-matrix


# Space Invaders Game on Raspberry Pi LED Matrix

## Setup Instructions

### 1. Install Python and Required Packages
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
pip3 install pillow
```

### 2. Install `rpi-rgb-led-matrix` Library
```bash
sudo apt-get install -y build-essential git python3-dev python3-pillow
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```

### 3. Font Files Setup
```bash
mkdir -p ~/rpi-rgb-led-matrix/fonts
cp ~/rpi-rgb-led-matrix/fonts/*.bdf ~/rpi-rgb-led-matrix/fonts/
```

### 4. Run the Game
1. Save your script as `space_invaders.py`.
2. Run it with:
```bash
python3 space_invaders.py