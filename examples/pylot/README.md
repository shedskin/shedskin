# pylot

```bash
cd pylot
python3 -m shedskin -be SimpleGeometry && make && python3 -c "import SimpleGeometry; assert SimpleGeometry.__file__.endswith('.so')"
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
