# Radare2 Dumper by Furkan

This Python script extracts C++ class and method information from `.so` (ELF) files using `readelf` and `c++filt`, then formats and dumps the data into readable `.cpp` source code.

---

## 🧩 Requirements

- Python 3
- `readelf` and `c++filt` (installed automatically if using Termux)
- A valid `.so` file (shared library)

---

## 📦 Installation

```bash
pkg install git
pkg install python3
git clone https://github.com/your-repo-url/r2dumper.git
cd r2dumper
chmod +x r2dump.py
python3 libdump-By-Furkan.py
