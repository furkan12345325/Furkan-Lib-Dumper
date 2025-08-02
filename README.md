# Radare2 Dumper by Furkan

This Python script extracts C++ class and method information from `.so` (ELF) files using `readelf` and `c++filt`, then formats and dumps the data into readable `.cpp` source code.

---

## 🧩 Requirements

- Python 3
- `readelf` and `c++filt` (installed automatically if using Termux)
- A valid `.so` file (shared library)

  /storage/emulated/0/folder location/libname.so

---

## 📦 Installation

```bash
termux-setup-storage
pkg install git
pkg install python3
git clone https://github.com/furkan12345325/Furkan-Lib-Dumper.git
cd Furkan-Lib-Dumper
python3 libdump-By-Furkan.py

