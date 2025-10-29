# 🚀 راهنمای اجرای سرور

## اجرای API (FastAPI)

### روش 1: استفاده از فایل batch (ساده‌تر)
فقط دوبار کلیک کن روی:
```
app/run_api.bat
```

### روش 2: اجرا دستی در PowerShell
```powershell
cd app
..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### روش 3: اجرا دستی در Command Prompt
```cmd
cd app
..\venv\Scripts\uvicorn.exe main:app --reload
```

بعد از اجرا، پیام زیر رو می‌بینی:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

سپس برو به: **http://127.0.0.1:8000/docs**

---

## 🔍 عیب‌یابی

### مشکل: سرور اجرا نمی‌شه

1. **چک کن محیط مجازی فعال هست:**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

2. **چک کن پکیج‌ها نصب شدن:**
   ```powershell
   venv\Scripts\python.exe -m pip list | findstr uvicorn
   ```

3. **اگر نصب نیست، دوباره نصب کن:**
   ```powershell
   venv\Scripts\python.exe -m pip install -r app/requirements.txt
   ```

### مشکل: صفحه بارگذاری نمی‌شه

1. چک کن پورت 8000 اشغال نیست:
   ```powershell
   netstat -an | findstr :8000
   ```
   
2. اگر پورت اشغال بود، پورت دیگه استفاده کن:
   ```powershell
   cd app
   ..\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
   ```

3. فایروال رو چک کن - ممکنه مسدود کرده باشه

### مشکل: خطای لود مدل

اگر خطای "Model files not found" دیدی:
1. چک کن فایل‌های زیر وجود دارند:
   - `app/sentiment_model.pkl`
   - `app/vectorizer.pkl`

2. اگر نیستند، اسکریپت رو اجرا کن:
   ```powershell
   python setup_model.py
   ```

---

## اجرای UI (Streamlit)

### روش 1: استفاده از فایل batch
دوبار کلیک کن روی:
```
app/run_ui.bat
```

### روش 2: اجرا دستی
```powershell
cd app
..\venv\Scripts\streamlit.exe run ui_app.py
```

سپس برو به: **http://localhost:8501**

