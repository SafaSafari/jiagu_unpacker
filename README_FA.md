# Jiagu Unpacker

ابزار Python برای باز کردن و استخراج فایل‌های DEX اصلی از APKهای اندروید که توسط Jiagu (加固) پک شده‌اند. این ابزار به صورت خودکار ZIP های معمولی و محافظت شده با رمز عبور را پردازش می‌کند.

## ویژگی‌ها

- **استخراج خودکار DEX**: استخراج فایل‌های `classes.dex` اصلی از APKهای پک شده با Jiagu
- **رمزگشایی AES و XOR**: پردازش لایه‌های رمزگذاری AES-CBC و XOR
- **دور زدن رمز ZIP**: تشخیص و حذف خودکار فلگ‌های رمزگذاری جعلی ZIP
- **پشتیبانی از چند DEX**: استخراج همه فایل‌های DEX (classes.dex, classes2.dex و...)
- **بازیابی نام Application**: بازیابی نام کلاس Application اصلی
- **جداسازی Shell DEX**: جدا کردن Shell DEX پک از کد اصلی

## Jiagu چیست؟

Jiagu (加固) یک بسته‌بند محبوب اندروید است که برای محافظت از APKها در برابر مهندسی معکوس استفاده می‌شود:
- فایل‌های DEX اصلی را با AES-CBC و XOR رمزگذاری می‌کند
- برنامه را با یک Shell DEX محافظتی می‌پوشاند
- گاهی از فلگ‌های رمزگذاری جعلی ZIP برای جلوگیری از استخراج استاندارد استفاده می‌کند

**این آنپکر برای APKهایی که با [بسته‌بند Jiagu](https://github.com/Frezrik/Jiagu) پک شده‌اند، طراحی شده است.**

این ابزار فرآیند پک را معکوس کرده و کد اصلی برنامه را بازیابی می‌کند.

## نصب

### نیازمندی‌ها

- Python 3.6+
- کتابخانه `pycryptodome`

### راه‌اندازی

```bash
# کلون کردن مخزن
git clone https://github.com/yourusername/Jiagu-unpacker.git
cd Jiagu-unpacker

# نصب وابستگی‌ها
pip3 install pycryptodome
```

## استفاده

### استفاده پایه

```bash
python3 jiagu_unpacker.py -apk packed.apk
```

این دستور یک پوشه `unpacked` ایجاد می‌کند که شامل موارد زیر است:
- `classes.dex` - فایل(های) DEX اصلی
- `classes2.dex`, `classes3.dex` و... - فایل‌های DEX اضافی (در صورت multidex)
- `shell.dex` - Shell DEX بسته‌بند Jiagu
- `original_application.txt` - نام کلاس Application اصلی

### پوشه خروجی سفارشی

```bash
python3 jiagu_unpacker.py -apk packed.apk -out extracted
```

### کار با ZIP های محافظت شده با رمز

ابزار **به صورت خودکار** تشخیص می‌دهد که آیا APK دارای فلگ‌های رمزگذاری جعلی ZIP است و روش رمزگشایی را اعمال می‌کند. نیازی به دخالت دستی نیست!

```bash
# این برای هر دو نوع APK معمولی و "محافظت شده با رمز" کار می‌کند
python3 jiagu_unpacker.py -apk protected.apk
```

نمونه خروجی:
```
[*] Extracting classes.dex from protected.apk...
[!] ZIP encryption detected: File is encrypted
[*] Attempting to extract using ZIP decryption method...
[+] Successfully extracted classes.dex using decryption, size: 1234567 bytes
```

## نحوه کار

### فرآیند باز کردن بسته

1. **استخراج DEX**:
   - ابتدا استخراج استاندارد ZIP را امتحان می‌کند
   - در صورت خطای رمز عبور، به صورت خودکار از `zip_decrypt.py` برای حذف فلگ‌های جعلی استفاده می‌کند

2. **تجزیه ساختار**:
   - طول Shell DEX را از 4 بایت آخر می‌خواند
   - Shell DEX را از محموله رمزشده جدا می‌کند

3. **رمزگشایی AES**:
   - 512 بایت اول با AES-CBC و کلید از پیش تعریف شده رمزگذاری شده‌اند
   - از حذف padding PKCS5 استفاده می‌کند

4. **بازیابی نام Application**:
   - بایت اول = طول نام کلاس Application اصلی
   - نام کدگذاری شده UTF-8 را استخراج می‌کند

5. **استخراج فایل‌های DEX**:
   - هر DEX دارای header اندازه 4 بایتی (big-endian) است
   - اولین DEX (classes.dex) بدون تغییر است
   - فایل‌های DEX اضافی دارای رمزگذاری XOR روی 112 بایت اول هستند

6. **رمزگشایی XOR** (برای classes2.dex به بعد):
   - کلید XOR: `0x66`
   - روی 112 بایت اول اعمال می‌شود

### ثابت‌های رمزگذاری

```python
AES_KEY = b"bajk3b4j3bvuoa3h"
AES_IV = b"mers46ha35ga23hn"
XOR_KEY = 0x66
XOR_LENGTH = 112
```

### روش رمزگشایی ZIP

ماژول `zip_decrypt.py` به این صورت کار می‌کند:
1. اسکن برای یافتن امضاهای Central Directory File Header (`PK\x01\x02`)
2. پاک کردن بیت رمزگذاری (بیت 0) در general purpose bit flag
3. ایجاد فایل موقت پاک شده که قابل استخراج عادی است

## ساختار فایل‌ها

```
Jiagu-unpacker/
├── jiagu_unpacker.py      # اسکریپت اصلی باز کننده بسته
├── zip_decrypt.py         # حذف فلگ رمزگذاری ZIP
├── README.md              # مستندات انگلیسی
├── README_FA.md           # مستندات فارسی
├── requirements.txt       # وابستگی‌های Python
├── LICENSE                # مجوز MIT
└── examples/              # اسکریپت‌های نمونه
    └── batch_unpack.sh    # اسکریپت پردازش دسته‌ای
```

## فایل‌های خروجی

پس از باز کردن بسته، این فایل‌ها را دریافت می‌کنید:

- **`classes.dex`**: فایل DEX اصلی اولیه
- **`classes2.dex`, `classes3.dex`, ...**: فایل‌های DEX اضافی (برنامه‌های multidex)
- **`shell.dex`**: Shell DEX بسته‌بند Jiagu (قابل حذف)
- **`original_application.txt`**: نام کلاس Application اصلی برای AndroidManifest.xml

## بازسازی APK اصلی

برای بازسازی یک APK کارآمد:

1. **استخراج APK پک شده**:
   ```bash
   apktool d packed.apk -o unpacked_apk
   ```

2. **جایگزینی فایل‌های DEX**:
   ```bash
   cp unpacked/classes*.dex unpacked_apk/
   ```

3. **بازیابی نام Application**:
   ویرایش `AndroidManifest.xml`:
   ```xml
   <application android:name="com.example.OriginalApplication" ...>
   ```
   از نام موجود در `original_application.txt` استفاده کنید

4. **حذف کتابخانه‌های Jiagu**:
   ```bash
   rm -rf unpacked_apk/assets/libjiagu*.so
   rm -rf unpacked_apk/lib/*/libjiagu*.so
   ```

5. **پک مجدد و امضا**:
   ```bash
   apktool b unpacked_apk -o rebuilt.apk
   jarsigner -keystore my.keystore rebuilt.apk mykey
   zipalign -v 4 rebuilt.apk final.apk
   ```

## استفاده پیشرفته

### پردازش دسته‌ای

```bash
#!/bin/bash
# پردازش همه APKها در یک پوشه
for apk in *.apk; do
    echo "Processing: $apk"
    python3 jiagu_unpacker.py -apk "$apk" -out "extracted_$(basename "$apk" .apk)"
done
```

### استفاده به عنوان ماژول

```python
from jiagu_unpacker import JiaguUnpacker

# ایجاد نمونه unpacker
unpacker = JiaguUnpacker("packed.apk", "output_dir")

# اجرای باز کردن بسته
success = unpacker.unpack()

if success:
    print("باز کردن بسته با موفقیت انجام شد!")
```

## رفع مشکلات

### "pycryptodome is required"
```bash
pip3 install pycryptodome
```

### "classes.dex not found in APK"
- APK ممکن است با Jiagu پک نشده باشد
- استخراج دستی با `unzip` یا `apktool` را امتحان کنید

### "Invalid DEX magic"
- باز کردن بسته ممکن است به صورت جزئی شکست خورده باشد
- بررسی کنید که آیا APK از نسخه متفاوت Jiagu استفاده می‌کند
- در صورت امکان، یک issue با جزئیات APK باز کنید

### "ZIP encryption detected" اما هنوز شکست می‌خورد
- APK ممکن است محافظت واقعی با رمز داشته باشد (نه فلگ‌های جعلی)
- استفاده مستقل از `zip_decrypt.py` را امتحان کنید:
  ```bash
  python3 zip_decrypt.py packed.apk
  ```

## محدودیت‌ها

- فقط با نسخه‌های Jiagu که از این کلیدهای رمزگذاری خاص استفاده می‌کنند، تست شده
- ممکن است با نسخه‌های جدیدتر Jiagu که از طرح‌های رمزگذاری متفاوتی استفاده می‌کنند، کار نکند
- نیاز به ساختار فایل ZIP معتبر در APK دارد

## اطلاعیه امنیتی و قانونی

**این ابزار فقط برای اهداف آموزشی و تحقیقات امنیتی است.**

- فقط روی برنامه‌هایی که مالک آن هستید یا مجوز تحلیل دارید استفاده کنید
- به حقوق مالکیت معنوی و قوانین محلی احترام بگذارید
- برای دزدی نرم‌افزار یا اهداف مخرب استفاده نکنید
- نویسندگان مسئولیتی در قبال سوء استفاده ندارند

## مشارکت

مشارکت‌ها خوش آمدید هستند! لطفاً:

1. مخزن را Fork کنید
2. یک شاخه ویژگی ایجاد کنید (`git checkout -b feature/improvement`)
3. تغییرات خود را commit کنید (`git commit -am 'Add new feature'`)
4. به شاخه push کنید (`git push origin feature/improvement`)
5. یک Pull Request باز کنید

## مجوز

این پروژه تحت مجوز MIT منتشر شده است - فایل [LICENSE](LICENSE) را برای جزئیات مشاهده کنید.

## منابع

- [فرمت DEX اندروید](https://source.android.com/docs/core/runtime/dex-format)
- [مشخصات فرمت فایل ZIP](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)
- [تحلیل بسته‌بند Jiagu](https://github.com/topics/jiagu)

## تغییرات

### نسخه 1.0.0 (2024)
- انتشار اولیه
- پشتیبانی از رمزگشایی AES-CBC و XOR
- دور زدن خودکار رمز ZIP
- استخراج چند فایل DEX
- بازیابی نام Application

## نویسنده

ایجاد شده برای محققان امنیتی و توسعه‌دهندگان اندروید که نیاز به تحلیل برنامه‌های پک شده دارند.

## قدردانی‌ها

- با تشکر از جامعه تحقیقات امنیتی اندروید
- الهام گرفته از ابزارهای مختلف باز کننده Jiagu و مقالات تحقیقاتی

---

**اگر این مخزن را مفید یافتید، ستاره دهید!** ⭐
