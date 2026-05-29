# 🔍 CF-Orion Pro

ابزار حرفه‌ای پیدا کردن آی‌پی تمیز کلودفلر و تست کانفیگ V2Ray با پشتیبانی از اپراتورهای ایرانی (همراه اول، ایرانسل، ADSL، رایتل، شاتل)

## قابلیت‌ها
پشتیبانی از VLESS، VMESS، Trojan | تست اپراتورهای ایرانی | اسکن 1.5 میلیون آی‌پی کلودفلر | سیستم امتیازدهی هوشمند | Web UI حرفه‌ای | Live Logging | خروجی JSON

## بعد از نصب
مرورگر را باز کنید و به http://localhost:5000 بروید. کانفیگ خود را وارد کنید، اپراتورها را انتخاب کنید و روی شروع اسکن کلیک کنید.

## رفع خطا
ModuleNotFoundError: pip install -r requirements.txt

pip not found (لینوکس): sudo apt install python3-pip -y

git not found (لینوکس): sudo apt install git -y

Port 5000 is occupied: python app.py --port 5001

## نصب دستی
git clone https://github.com/alirezani/cf-orion-pro.git

cd cf-orion-pro

pip3 install -r requirements.txt

python3 app.py


## نصب روی لینوکس (خودکار)
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/alirezani/cf-orion-pro/main/install.sh)"

