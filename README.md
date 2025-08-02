# Radare2 Dumper by Furkan

Bu araç, ELF (.so) dosyalarındaki C++ sembollerini `readelf` ve `c++filt` kullanarak çözer ve sınıf-metot bilgilerini `.cpp` formatında dışa aktarır.

## 🧩 Gereksinimler

- Python 3
- `readelf` ve `c++filt` (Termux kullanıyorsan otomatik yüklenir)
- `.so` uzantılı ELF dosyası

## 📦 Kurulum

```bash
git clone https://github.com/kendi-repo-url/r2dumper.git
cd r2dumper
chmod +x r2dump.py
