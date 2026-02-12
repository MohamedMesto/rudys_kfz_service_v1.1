Below is a **step-by-step, Windows-friendly** way to run your **Django + PostgreSQL** project on the client PC. I’ll assume your project is currently using **PostgreSQL** and `.env`/settings for DB credentials.

---

## 0) What you need on the client PC

Install these (Windows):

1. **Python 3.10+** (recommend 3.10 to match your venv)

   * During install: ✅ check “Add python.exe to PATH”
2. **PostgreSQL 14/15/16**

   * Remember the **postgres password** you set
3. **Git** (optional, if you deliver code via repo/zip you can skip)

---

## 1) Copy the project to Windows

Option A: give client a ZIP

* Extract to: `C:\rudys_kfz_service\`

Option B: clone repo (if Git installed):

```bat
cd C:\
git clone <your-repo-url> rudys_kfz_service
```

---

## 2) Create a Python virtual environment

Open **Command Prompt** (or PowerShell) inside project folder:

```bat
cd C:\rudys_kfz_service
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in the terminal.

---

## 3) Install Python requirements

If you have `requirements.txt`:

```bat
pip install --upgrade pip
pip install -r requirements.txt
```

### ⚠️ If you use WeasyPrint (PDF)

On Windows WeasyPrint needs system libraries (GTK/Pango/Cairo).
Two best options:

**Option 1 (recommended for Windows):** use **wkhtmltopdf** instead of WeasyPrint
**Option 2:** install GTK runtime for WeasyPrint (more painful)

If your client *must* use current WeasyPrint approach, tell me and I’ll give you the exact Windows GTK install steps matching your version.

---

## 4) Install & setup PostgreSQL (Windows)

Open **pgAdmin** or use `psql` (pgAdmin is easier).

### Create database + user

**In pgAdmin:**

1. Login as `postgres`
2. Create user:

   * Name: `rudys_user`
   * Password: `StrongPasswordHere`
   * Privileges: ✅ Can login
3. Create database:

   * Name: `rudys_db`
   * Owner: `rudys_user`

### Grant privileges (optional but safe)

Run in Query Tool:

```sql
GRANT ALL PRIVILEGES ON DATABASE rudys_db TO rudys_user;
```

---

## 5) Configure Django DB settings on Windows

In your `settings.py` you currently have something like:

```py
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "rudys_db",
    "USER": "...",
    "PASSWORD": "...",
    "HOST": "127.0.0.1",
    "PORT": "5432",
  }
}
```

Change to the client’s DB credentials:

* NAME: `rudys_db`
* USER: `rudys_user`
* PASSWORD: `StrongPasswordHere`
* HOST: `127.0.0.1`
* PORT: `5432`

✅ Best practice: use `.env` so you don’t hardcode passwords.

Example `.env`:

```
DB_NAME=rudys_db
DB_USER=rudys_user
DB_PASSWORD=StrongPasswordHere
DB_HOST=127.0.0.1
DB_PORT=5432
```

---

## 6) Run migrations

In terminal (venv active):

```bat
python manage.py makemigrations
python manage.py migrate
```

---

## 7) Create admin user (new PC needs new admin)

```bat
python manage.py createsuperuser
```

Example:

* username: `admin`
* email: (optional)
* password: (choose)

✅ This solves “new admin details”.

---

## 8) Collect static files (important for production-like runs)

```bat
python manage.py collectstatic
```

(Answer “yes” if prompted.)

---

## 9) Run the server

```bat
python manage.py runserver
```

Open:

* [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 10) Load initial data (Company, Diagnosis, etc.)

Your app expects a `Company` record exists (you coded: `Company.objects.first()`).

So after login:

1. Go to **Companies** (your UX) and create one
2. Add **Diagnoses**
3. Create Customers
4. Create invoices

✅ If you want a “one-click setup” for client, use fixtures (see below).

---

# Recommended delivery method (so setup is easy for client)

## A) Provide a `setup_windows.bat` script (one click)

You can automate:

* venv creation
* pip install
* migrate
* createsuperuser prompt
* runserver

## B) Provide DB fixture(s)

Export demo or production data (without passwords):

```bat
python manage.py dumpdata invoices.Company invoices.Diagnosis --indent 2 > initial_data.json
```

Then on client:

```bat
python manage.py loaddata initial_data.json
```

---

# Common Windows issues (quick fixes)

### 1) “psycopg2” fails to install

Use binary:

```bat
pip install psycopg2-binary
```

### 2) WeasyPrint errors on Windows

If you keep WeasyPrint, you may see missing DLL errors.
Tell me your exact error message and I’ll give the right GTK runtime setup.

### 3) Static files missing

Make sure:

* `STATIC_URL` set
* `collectstatic` run
* `DEBUG=True` during local use

---

# If you want: simplest for client (no Python install)

You can package as:

* **Docker** (best consistent deployment)
* or **Windows Installer** with embedded Python (possible but heavier)

If you want, tell me which delivery you prefer:

1. “Client runs it locally with Python” (steps above)
2. “Docker desktop run” (1 command)
3. “Hosted server” (client uses browser only)

And I’ll give the exact final delivery workflow.


مفهوم تمامًا — **WeasyPrint على Windows غالبًا يسبب مشاكل** لأنّه يعتمد على مكتبات نظام (GTK / Cairo / Pango) وتثبيتها على جهاز الزبون يكون مزعج وغير ثابت. لذلك القرار الصحيح: **نغيّر طريقة توليد الـ PDF** بحيث تعمل على Windows بدون صداع.

سأعطيك أفضل البدائل (مع رأيي)، ثم حلول “تسليم” (Docker / exe / سيرفر).

---

## 1) رأيي المختصر

إذا العميل على **Windows** وتريد حل **ثابت وسهل التسليم**:

✅ **أفضل خيار عملي**:

### **ReportLab** (توليد PDF من بايثون مباشرة)

* يعمل على Windows 100% بدون مكتبات خارجية معقّدة
* سريع وثابت
* مناسب للفواتير + QR + جدول + تنسيق A4
* لا يعتمد على HTML/CSS (وهذا ميزته هنا)

⚠️ العيب الوحيد:
التصميم ليس “HTML/CSS” بل عبر Canvas/Paragraph/Table في ReportLab — لكنه للفواتير ممتاز.

---

## 2) بدائل ممتازة (اختر حسب الأولوية)

### ✅ A) ReportLab (أنصح به)

**متى؟** إذا تريد PDF ثابت على Windows + بدون مشاكل تثبيت.
**يدعم:** جداول، خطوط، صور، QR، RTL بالعربية ممكن لكن يحتاج خط عربي + reshaping (أشرح بعد شوي).

---

### ✅ B) wkhtmltopdf (HTML → PDF) (حل قوي جدًا)

**الفكرة:** تستخدم Django template HTML لكن التحويل يتم عبر برنامج جاهز `wkhtmltopdf.exe`

* مشهور جدًا في أنظمة الفواتير
* يعمل على Windows بسهولة (تثبت exe مرة واحدة)
* يعطيك نفس شكل HTML تقريبًا

**عيوب:**

* لازم تثبيت wkhtmltopdf على جهاز العميل
* أحيانًا RTL / خطوط عربية تحتاج ضبط

إذا تريد “نفس HTML/CSS” → هذا خيار ممتاز.

مكتبة Django:

* `pdfkit` أو `django-wkhtmltopdf`

---

### ✅ C) Playwright / Chromium print-to-pdf

تفتح الصفحة في Chromium headless وتعمل print PDF.

* جودة عالية جدًا + CSS كامل
* RTL ممتاز
* لكن: يعتمد على chromium ووزنه أكبر
* تشغيله على Windows ممكن، لكنه أثقل من wkhtmltopdf

---

### ✅ D) LibreOffice / DOCX → PDF

تصمم الفاتورة DOCX (قالب) وتملأ البيانات ثم تحويل PDF.

* Arabic/RTL غالبًا ممتاز
* لكن يحتاج LibreOffice installed أو تحويل عبر خدمة

---

## 3) ماذا عن Docker؟

Docker يحل المشكلة بالكامل لأنك تشغل نفس Ubuntu environment عند العميل.

✅ إيجابيات:

* نفس بيئة Ubuntu = WeasyPrint يشتغل بدون اختلاف
* تسليم سريع، كل شيء داخل container

❌ سلبيات:

* العميل لازم يثبت Docker Desktop (ثقيل)
* بعض الشركات تمنعه
* تشغيله كـ “برنامج” أقل سلاسة للمستخدم العادي

**متى أنصح به؟**

* إذا العميل تقني أو عنده IT
* أو تريد تجنب أي اختلاف بيئة

---

## 4) ماذا عن برنامج تنفيذي EXE؟

ممكن، لكن لازم تنتبه:

* Django + Postgres + PDF engine داخل exe = معقد جدًا
* تحديثات/صيانة أصعب
* حجم كبير
* غالبًا ستحتاج حزمة كاملة “installer” وليس exe واحد.

✅ ممكن نسوي EXE لجزء الـ PDF فقط (microservice)
لكن كحل شامل… غالبًا Docker أسهل من exe.

---

# ✅ أفضل حلين واقعيين لك الآن (بالترتيب)

## الحل رقم 1 (أنصح به): **ReportLab**

* ما في “HTML to PDF” إطلاقًا
* تولّد PDF من بايثون مباشرة
* QR سهل جدًا
* Windows مضمون

**وأنت أصلاً عندك QR جاهز بالبايثون** → ممتاز.

---

## الحل رقم 2: **wkhtmltopdf**

إذا تريد تظل على HTML template مثل اللي عملته:

* ثبّت wkhtmltopdf على Windows
* استخدم pdfkit لتحويل template إلى PDF

---

# 💡 ملاحظة مهمة عن العربية (RTL)

سواء ReportLab أو wkhtmltopdf:

* لازم **خط عربي** (مثل Noto Naskh Arabic أو Amiri)
* بعض المحركات تحتاج “Arabic shaping”
  (ReportLab يحتاج `arabic_reshaper` + `python-bidi` غالبًا)

أنا أقدر أعطيك إعداد جاهز للعربية بأي خيار تختاره.

---

# ✅ سؤالك: “ماذا تقترح برمجياً؟”

أقترح أحد مسارين حسب رغبتك:

### (A) تريد PDF “نظيف وثابت” بسرعة؟

➡️ **ReportLab**

### (B) تريد الاحتفاظ بالتصميم HTML/CSS الحالي؟

➡️ **wkhtmltopdf**

---

# الخطوة التالية (بدون أسئلة كثيرة)

قل لي فقط:
**هل تريد أن نحول مشروعك إلى ReportLab؟ أم تبقى HTML وتستخدم wkhtmltopdf؟**

إذا قلت “ReportLab” سأرسل لك مباشرة:

* ملف `views_invoice_pdf.py` جديد كامل
* دعم QR
* Footer كما طلبت
* Arabic/Deutsch RTL/LTR مع خط عربي

وإذا قلت “wkhtmltopdf” سأرسل:

* إعداد Windows
* كود التحويل داخل Django
* طريقة تضمين wkhtmltopdf في installer

(اختر واحدة وسأعطيك الكود النهائي مباشرة.)
