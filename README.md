این باکس نهایی - فقط یک باکس، فقط کپی کن
markdown

# 🔍 CF-Orion Pro

ابزار حرفه‌ای پیدا کردن آی‌پی تمیز کلودفلر و تست کانفیگ V2Ray با پشتیبانی از اپراتورهای ایرانی (همراه اول، ایرانسل، ADSL، رایتل، شاتل)

## قابلیت‌ها
پشتیبانی از VLESS، VMESS، Trojan | تست اپراتورهای ایرانی | اسکن 1.5 میلیون آی‌پی کلودفلر | سیستم امتیازدهی هوشمند | Web UI حرفه‌ای | Live Logging | خروجی JSON

## نصب روی لینوکس (خودکار)
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/alirezani/cf-orion-pro/main/install.sh)"

نصب روی لینوکس (دستی)
bash

git clone https://github.com/alirezani/cf-orion-pro.git && cd cf-orion-pro && pip3 install -r requirements.txt && python3 app.py

نصب روی ویندوز (خودکار - PowerShell)
powershell

iex (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/alirezani/cf-orion-pro/main/install.ps1" -UseBasicParsing).Content

نصب روی ویندوز (خودکار - Git Bash)
bash

git clone https://github.com/alirezani/cf-orion-pro.git && cd cf-orion-pro && pip install -r requirements.txt && python app.py

نصب روی ویندوز (دستی)
cmd

git clone https://github.com/alirezani/cf-orion-pro.git && cd cf-orion-pro && pip install -r requirements.txt && python app.py

بعد از نصب

مرورگر را باز کنید و به http://localhost:5000 بروید. کانفیگ خود را وارد کنید، اپراتورها را انتخاب کنید و روی شروع اسکن کلیک کنید.
لینک‌ها

https://github.com/alirezani/cf-orion-pro
https://raw.githubusercontent.com/alirezani/cf-orion-pro/main/install.sh
https://raw.githubusercontent.com/alirezani/cf-orion-pro/main/install.ps1
رفع خطا

ModuleNotFoundError: pip install -r requirements.txt
pip not found (لینوکس): sudo apt install python3-pip -y
git not found (لینوکس): sudo apt install git -y
پورت 5000 اشغال است: python app.py --port 5001
نکته

این ابزار فقط برای تست امنیتی و با مجوز مالک سایت قابل استفاده است.
text


---

## حالا فقط این کار رو بکن

1. فایل `README.md` رو باز کن
2. **کامل پاک کن**
3. **فقط همین باکس بالا رو کپی کن**
4. بچسبون
5. ذخیره کن
6. `git add README.md && git commit -m "final" && git push origin main`

**تموم. دیگه تکرار نمیشه 🚀**
