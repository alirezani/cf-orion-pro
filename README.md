<div align="center">

# 🔍 CF-Orion Pro

**ابزار حرفه‌ای پیدا کردن آی‌پی تمیز کلودفلر و تست کانفیگ V2Ray**  
**پشتیبانی از اپراتورهای ایرانی: همراه اول | ایرانسل | ADSL | رایتل | شاتل**

---

[![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/alirezani/cf-orion-pro)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/alirezani/cf-orion-pro)
[![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)](https://python.org)

</div>

---

## ✨ قابلیت‌های پروژه

| قابلیت | توضیح |
|:---|:---|
| 🎯 **پارسر کانفیگ V2Ray** | پشتیبانی کامل از VLESS، VMESS، Trojan |
| 🇮🇷 **تست اپراتورهای ایرانی** | همراه اول، ایرانسل، ADSL، رایتل، شاتل |
| ⚡ **اسکن تمیز کلودفلر** | اسکن 1.5 میلیون آی‌پی در 14 رنج |
| 📊 **امتیازدهی هوشمند** | ترکیب پینگ + سرعت دانلود + TTFB |
| 🌐 **Web UI حرفه‌ای** | طراحی مدرن + حالت شب |
| 📡 **Live Logging** | نمایش لحظه‌به‌لحظه لاگ اسکن |
| 💾 **خروجی JSON** | ذخیره خودکار نتایج |

---

## 🔧 رفع خطاهای رایج
خطا	راه حل
## ModuleNotFoundError	pip install -r requirements.txt
## pip: command not found (لینوکس)	sudo apt install python3-pip -y
## git: command not found (لینوکس)	sudo apt install git -y
## address already in use	python app.py --port 5001
## Python was not found (ویندوز)	Python را با تیک "Add to PATH" 

## 🚀 نصب و اجرا

## 📝 نصب دستی (قدم به قدم)

# مرحله 1: نصب پیش‌نیازها
  sudo apt update
  
sudo apt install git python3 python3-pip -y

# مرحله 2: دانلود پروژه
git clone https://github.com/alirezani/cf-orion-pro.git

# مرحله 3: وارد پوشه شوید
cd cf-orion-pro

# مرحله 4: نصب وابستگی‌ها
pip3 install -r requirements.txt

# مرحله 5: اجرا
python3 app.py

### 📦 نصب خودکار (یک خطی)

<details>
<summary>🐧 لینوکس</summary>

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/alirezani/cf-orion-pro/main/install.sh)"


