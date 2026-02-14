## 1) Export current PostgreSQL DB to another PC (WITH ALL DATA)

### Best/cleanest way (Postgres-to-Postgres): **pg_dump → restore**

This keeps **all data**, **relations**, **IDs**, **constraints**, **indexes**, etc.

### A) On your PC (source) — create a backup file

#### Option 1 (recommended): **custom format** `.backup`

```bash
pg_dump -h 127.0.0.1 -p 5432 -U rudys_kfz_mesto -F c -b -v -f rudys_db.backup rudys_db
```

* `-F c` = custom format (best for restore)
* `-b` = includes blobs (if any)
* You will be asked for the DB password (unless you use `.pgpass`).

#### Option 2: plain SQL file `.sql`

```bash
pg_dump -h 127.0.0.1 -p 5432 -U rudys_kfz_mesto -F p -v -f rudys_db.sql rudys_db
```

✅ Copy `rudys_db.backup` (or `.sql`) to the client PC.

---

### B) On client PC — install PostgreSQL + create DB/user

In **psql** (or pgAdmin):

```sql
CREATE USER rudys_kfz_mesto WITH PASSWORD 'YOUR_PASSWORD';
CREATE DATABASE rudys_db OWNER rudys_kfz_mesto;
```

---

### C) Restore on client PC

#### If you used `.backup` (recommended)

```bash
pg_restore -h 127.0.0.1 -p 5432 -U rudys_kfz_mesto -d rudys_db -v rudys_db.backup
```

#### If you used `.sql`

```bash
psql -h 127.0.0.1 -p 5432 -U rudys_kfz_mesto -d rudys_db -f rudys_db.sql
```

✅ That’s it — your DB arrives with all invoice/customer/items data.

---

### What about JSON files?

They are **NOT** a replacement for a real Postgres dump if you want “everything”.

* `dumpdata` JSON is good for **Django models only**
* but it can cause issues with:

  * permissions/users
  * sequences/auto IDs
  * ordering dependencies
  * constraints
  * Postgres-specific objects

If you still want JSON as an optional backup:

```bash
python manage.py dumpdata \
  --natural-foreign --natural-primary \
  --exclude auth.permission --exclude contenttypes \
  --indent 2 > backup.json
```

Restore:

```bash
python manage.py loaddata backup.json
```

⚠️ Still: for “move DB to client with data” → **pg_dump is the correct solution**.

---

## 2) Create TR language (Turkish)

### A) Add Turkish to `settings.py`

```py
LANGUAGES = [
    ("en", "English"),
    ("de", "Deutsch"),
    ("ar", "العربية"),
    ("tr", "Türkçe"),
]
```

Make sure you already have:

```py
USE_I18N = True
MIDDLEWARE = [
    ...
    "django.middleware.locale.LocaleMiddleware",
    ...
]
LOCALE_PATHS = [BASE_DIR / "locale"]
```

---

### B) Create locale folder + generate TR `.po`

From project root:

```bash
django-admin makemessages -l tr
```

This creates:

```
locale/tr/LC_MESSAGES/django.po
```

---

### C) Translate Turkish strings

Edit:
`locale/tr/LC_MESSAGES/django.po`

Then compile:

```bash
django-admin compilemessages
```

---

### D) Add TR button to your language switch form

Add:

```html
<button type="submit" name="language" value="tr"
  class="btn btn-sm {% if LANGUAGE_CODE == 'tr' %}btn-light{% else %}btn-outline-light{% endif %}">
  🇹🇷 TR
</button>
```

---

If you tell me:

* database name
* db username
* whether the client OS is Windows or Linux

…I can give you the exact copy/paste commands (including pgAdmin steps if you prefer UI).
