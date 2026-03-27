from pathlib import Path
from datetime import datetime
import os
import subprocess

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect


def admin_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def get_backup_dir() -> Path:
    backup_dir = Path(settings.BASE_DIR) / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_pg_dump_command() -> str:
    """
    Optional custom path from settings.py:
    PG_DUMP_PATH = r"C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe"
    """
    return getattr(settings, "PG_DUMP_PATH", "pg_dump")


@login_required
@user_passes_test(admin_required)
def backup_dashboard_view(request):
    backup_dir = get_backup_dir()
    files = sorted(
        [f for f in backup_dir.iterdir() if f.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    return render(request, "invoices/backup/dashboard.html", {"files": files})


@login_required
@user_passes_test(admin_required)
def create_backup_view(request):
    if request.method != "POST":
        return redirect("backup:dashboard")

    db = settings.DATABASES["default"]
    engine = db.get("ENGINE", "")

    if "postgresql" not in engine:
        messages.error(request, "Backup is currently implemented for PostgreSQL only.")
        return redirect("backup:dashboard")

    db_name = db["NAME"]
    db_user = db["USER"]
    db_password = db["PASSWORD"]
    db_host = db.get("HOST") or "127.0.0.1"
    db_port = str(db.get("PORT") or "5432")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{db_name}_{timestamp}.backup"
    output_path = get_backup_dir() / filename

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    command = [
        get_pg_dump_command(),
        "-h", db_host,
        "-p", db_port,
        "-U", db_user,
        "-F", "c",
        "-b",
        "-v",
        "-f", str(output_path),
        db_name,
    ]

    try:
        subprocess.run(command, check=True, env=env, capture_output=True, text=True)
        messages.success(request, f"Backup created successfully: {filename}")
    except FileNotFoundError:
        messages.error(
            request,
            "pg_dump was not found. Please install PostgreSQL client tools or set PG_DUMP_PATH in settings.py."
        )
    except subprocess.CalledProcessError as e:
        error_text = e.stderr or e.stdout or str(e)
        messages.error(request, f"Backup failed: {error_text}")

    return redirect("backup:dashboard")


@login_required
@user_passes_test(admin_required)
def download_backup_view(request, filename):
    file_path = get_backup_dir() / filename

    if not file_path.exists() or not file_path.is_file():
        raise Http404("Backup file not found.")

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=file_path.name,
    )