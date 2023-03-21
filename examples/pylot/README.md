# pylot

```bash
cd pylot
shedskin build -e SimpleGeometry
cp build/SimpleGeometry.so .
cd ..
python pylot_main.py
```

## Linux

requires 

```bash
sudo apt install python3-tk 
pip install Pillow
```

## macOS

requires (for example)

```bash
# assuming python version == 3.10.x
brew install python-tk@3.10
pip install Pillow
```
