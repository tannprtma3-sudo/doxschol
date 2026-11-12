#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DoxSchool v5.0 — Universal Balance System
API: apisiswa.solved.my.id (with key)
Only Dump Sekolah feature
by denz
"""

import sys
sys.dont_write_bytecode = True
import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import time
import re
import json
import base64
import requests
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

# ====================== KONFIGURASI ======================
API_SISWA_KEY = "PCOAViHvKVDZgRQE_qgVXOlSN-m7CIP4"
API_SISWA = f"https://dapper-bubblegum-9590df.netlify.app/api/dump?apikey={API_SISWA_KEY}&npsn={{npsn}}"

# Timeout config (detik)
TIMEOUT_DUMP = 40
TIMEOUT_GITHUB = 15

GITHUB_USERNAME = "username github lu"
REPO_NAME       = "doxchol-keys"
KEYS_FILE       = "doxschool_keys.txt"
PENDING_FILE    = "doxschool_pending.txt"
GITHUB_TOKEN    = "token github lu"

BOT_REGISTER = "token bot lu"
ADMIN_TELE   = "id tele lu"

USER_UID = "-"
USER_NAMA = "-"
USER_STATUS = "-"

FEATURES = {
    "dumpsekolah":   {"label": "Dump Sekolah",   "cost": 2},
}

# ====================== OUTPUT DIR ======================
if os.path.exists("/sdcard"):
    OUTPUT_DIR = "/sdcard/doxschool"
elif os.path.exists(os.path.expanduser("~/storage/shared")):
    OUTPUT_DIR = os.path.expanduser("~/storage/shared/doxschool")
else:
    OUTPUT_DIR = os.path.join(os.getcwd(), "doxschool")

def ensure_output_dir():
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except:
        pass

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]DoxSchool[/bold cyan] [bold white]v5.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = r"""
   [bold cyan]  ,_,
    (o,o)    [bold white]DoxSchool[/bold white]
    {`"'}    [dim]OSINT Sekolah Indonesia[/dim]
    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold cyan]
    """
    return Align.center(Text.from_markup(logo))

# ====================== GITHUB DATABASE ======================
def github_get_file(filename):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{filename}"
    headers = {'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3.raw'}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT_GITHUB)
        if resp.status_code == 200:
            return resp.text
        return None
    except:
        return None

def github_put_file(filename, content, commit_msg="Update file"):
    encoded = base64.b64encode(content.encode()).decode()
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{filename}"
    headers = {'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    sha = None
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT_GITHUB)
        if resp.status_code == 200:
            sha = resp.json().get('sha')
    except:
        pass
    payload = {'message': commit_msg, 'content': encoded, 'branch': 'main'}
    if sha:
        payload['sha'] = sha
    try:
        resp = requests.put(url, headers=headers, json=payload, timeout=TIMEOUT_GITHUB * 2)
        return resp.status_code in [200, 201]
    except:
        return False

def load_users():
    content = github_get_file(KEYS_FILE)
    if not content:
        return []
    users = []
    for line in content.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.strip().split('|')
        if len(parts) >= 4:
            balance = 0
            if len(parts) >= 5:
                raw = parts[4].strip()
                try:
                    balance = int(raw)
                except ValueError:
                    try:
                        limits = json.loads(raw)
                        balance = 0
                        for lim in limits.values():
                            balance += max(0, lim.get('limit', 0) - lim.get('used', 0))
                    except:
                        balance = 0
            users.append({
                'device_id': parts[0],
                'role': parts[1],
                'nama': parts[2],
                'status': parts[3],
                'balance': balance
            })
    return users

def save_users(users):
    lines = []
    for u in users:
        line = f"{u.get('device_id')}|{u.get('role')}|{u.get('nama')}|{u.get('status')}|{u.get('balance', 0)}"
        lines.append(line)
    content = '\n'.join(lines)
    return github_put_file(KEYS_FILE, content, "Update users via DoxSchool")

def load_pending():
    content = github_get_file(PENDING_FILE)
    if not content:
        return []
    pendings = []
    for line in content.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.strip().split('|')
        if len(parts) >= 3:
            pendings.append({
                'device_id': parts[0],
                'nama': parts[1],
                'timestamp': parts[2]
            })
    return pendings

def save_pending(pendings):
    lines = []
    for p in pendings:
        line = f"{p.get('device_id')}|{p.get('nama')}|{p.get('timestamp')}"
        lines.append(line)
    content = '\n'.join(lines)
    return github_put_file(PENDING_FILE, content, "Update pending via DoxSchool")

def add_pending(device_id, nama):
    pendings = load_pending()
    for p in pendings:
        if p.get('device_id') == device_id:
            return False
    pendings.append({
        'device_id': device_id,
        'nama': nama,
        'timestamp': str(int(time.time()))
    })
    return save_pending(pendings)

# ====================== UTILITY ======================
def get_devid():
    try:
        import hashlib
        whoami = os.popen('whoami').read().strip()
        id_output = os.popen('id').read().strip()
        uid_match = re.search(r'uid=(\d+)', id_output)
        uid = uid_match.group(1) if uid_match else "0"
        ctx_match = re.search(r'context=([^\s]+)', id_output)
        ctx = ctx_match.group(1) if ctx_match else ""
        c_vals = re.findall(r'c(\d+)', ctx)
        c_str = ''.join(c_vals[:2]) if c_vals else ""
        mac = os.popen("ip link show 2>/dev/null | grep 'link/ether' | awk '{print $2}' | head -1").read().strip().replace(":", "")
        serial = os.popen("getprop ro.serialno 2>/dev/null").read().strip()
        android_id = os.popen("settings get secure android_id 2>/dev/null").read().strip()
        build_id = os.popen("getprop ro.build.id 2>/dev/null").read().strip()
        fingerprint = os.popen("getprop ro.build.fingerprint 2>/dev/null").read().strip()
        termux_home = os.path.expanduser("~")
        inode = str(os.stat(termux_home).st_ino) if os.path.exists(termux_home) else ""
        raw = f"{whoami}{uid}{c_str}{mac}{serial}{android_id}{build_id}{fingerprint}{inode}"
        raw = re.sub(r'[^a-zA-Z0-9]', '', raw)
        return hashlib.sha256(raw.encode()).hexdigest()[:20]
    except:
        try:
            import hashlib
            fallback = os.popen('whoami').read().strip() + str(os.getuid())
            return hashlib.md5(fallback.encode()).hexdigest()[:20]
        except:
            return "unknown"

def kirim_registrasi_telegram(device_id, username):
    pesan = f"""
📨 Pending Registrasi DoxSchool

ID PENGGUNA
`{device_id}`

NAMA AKUN
`{username}`

Approve via admin panel.
"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_REGISTER}/sendMessage",
            json={"chat_id": ADMIN_TELE, "text": pesan, "parse_mode": "Markdown"},
            timeout=15
        )
        return True
    except:
        return False

def loading_spinner(duration=1.5, text="Loading"):
    with Progress(SpinnerColumn(spinner_name='dots'),
                  TextColumn(f'[bold cyan]{text}'), console=console) as progress:
        progress.add_task("", total=None)
        time.sleep(duration)

def loading_animation(task_name, duration=2):
    with Progress(SpinnerColumn(spinner_name='dots'),
                  TextColumn('[bold cyan]{task.description}'),
                  TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
                  console=console, transient=True) as progress:
        task = progress.add_task(task_name, total=100)
        step = 100 / duration / 10
        while not progress.finished:
            progress.update(task, advance=step)
            time.sleep(0.1)

# ====================== ADMIN CHECK ======================
def is_admin(device_id):
    users = load_users()
    for u in users:
        if u['device_id'] == device_id:
            return u.get('role', 'user') == 'admin'
    return False

# ====================== UNIVERSAL BALANCE SYSTEM ======================
def check_and_use_balance(device_id, feature):
    if is_admin(device_id):
        return True, "UNLIMITED"

    cost = FEATURES[feature]["cost"]

    users = load_users()
    user = None
    for u in users:
        if u['device_id'] == device_id:
            user = u
            break
    if not user:
        return False, 0

    balance = user.get('balance', 0)

    if balance < cost:
        return False, balance

    user['balance'] = balance - cost
    save_users(users)
    return True, balance - cost

def refund_balance(device_id, feature, reason=""):
    """Kembalikan balance sesuai cost. Skip jika admin."""
    if is_admin(device_id):
        return

    cost = FEATURES[feature]["cost"]

    users = load_users()
    for u in users:
        if u['device_id'] == device_id:
            u['balance'] = u.get('balance', 0) + cost
            save_users(users)
            console.print(f"[yellow]↩ Refund {cost} limit (gagal: {reason})[/yellow]")
            return

# ====================== DISPLAY BALANCE ======================
def show_user_balance(user):
    if user.get('status') == 'banned':
        console.print(Panel(
            "[bold red]AKUN DI-BAN[/bold red]",
            title="[bold white]BALANCE ANDA[/bold white]",
            border_style="red"
        ))
        return

    if user.get('role') == 'admin':
        console.print(Panel(
            "[bold green]AKUN ADMIN — UNLIMITED[/bold green]\n"
            "[dim]Semua fitur dapat diakses tanpa batas[/dim]",
            title="[bold white]BALANCE ANDA[/bold white]",
            border_style="green"
        ))
        return

    balance = user.get('balance', 0)
    table = Table(box=box.ROUNDED, border_style='green', title="[bold white]BALANCE ANDA[/bold white]")
    table.add_column("Item", style="bold green")
    table.add_column("Value", style="cyan", justify="right")
    table.add_row("Balance", f"[bold white]{balance} limit[/bold white]")
    table.add_row("Dump Sekolah", "2 limit / request")
    console.print(table)
    if balance <= 0:
        console.print("[yellow]Balance kamu masih kosong. Hubungi admin untuk top up.[/yellow]")

# ====================== SAVE JSON ======================
def save_to_json(data, endpoint, npsn):
    if not data:
        return None
    ensure_output_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{endpoint}_{npsn}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        console.print(f"[green]Disimpan: {filepath}[/green]")
        return filepath
    except Exception as e:
        console.print(f"[red]Gagal simpan: {e}[/red]")
        return None

# ====================== FETCH SISWA ======================
def fetch_siswa(npsn):
    """Fetch data siswa. Return: (data, error)
    Semua error & timeout WAJIB di-refund oleh caller."""
    url = API_SISWA.format(npsn=npsn)
    try:
        resp = requests.get(url, timeout=TIMEOUT_DUMP)
        if resp.status_code == 401:
            return None, "API Key invalid / expired"
        if resp.status_code == 403:
            return None, "Akses ditolak — API Key salah"
        if resp.status_code == 429:
            return None, "Rate limit — coba lagi nanti"
        if resp.status_code == 404:
            return None, "NPSN tidak ditemukan"
        if resp.status_code == 500:
            return None, "Server error (500)"
        if resp.status_code == 502:
            return None, "Bad gateway (502)"
        if resp.status_code == 503:
            return None, "Service unavailable (503)"
        if resp.status_code == 504:
            return None, "Gateway timeout (504)"
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"
        return resp.json(), None
    except requests.exceptions.Timeout:
        return None, f"Timeout setelah {TIMEOUT_DUMP} detik — server tidak merespon"
    except requests.exceptions.ConnectionError:
        return None, "Gagal terhubung ke server"
    except requests.exceptions.JSONDecodeError:
        return None, "Response bukan JSON yang valid"
    except Exception as e:
        return None, f"Error tidak dikenal: {str(e)}"

def display_siswa_data(data, npsn):
    if not data:
        console.print("[red]Tidak ada data.[/red]")
        return

    sekolah_info = data.get("sekolah", {})
    siswa = data.get("data", [])
    jumlah = data.get("jumlah", len(siswa))

    info_table = Table(box=box.ROUNDED, border_style='cyan',
                       title=f"[bold white]INFO SEKOLAH[/bold white]\n[dim]NPSN: {npsn}[/dim]")
    info_table.add_column("Field", style="bold cyan")
    info_table.add_column("Value", style="white")
    for label, key in [
        ("Nama Sekolah", "nama"),
        ("Provinsi", "propinsi"),
        ("Kabupaten/Kota", "kabupaten_kota"),
        ("Kecamatan", "kecamatan"),
        ("Jenjang", "jenjang"),
        ("Status", "status"),
    ]:
        val = sekolah_info.get(key)
        if val:
            info_table.add_row(label, str(val))
    console.print(info_table)

    if not siswa:
        console.print("[yellow]Tidak ada data siswa.[/yellow]")
        return

    save_to_json(data, "dumpsekolah", npsn)

    table = Table(box=box.ROUNDED, border_style='blue',
                  title=f"[bold white]DATA SISWA[/bold white]\n[dim]Total: {jumlah} siswa[/dim]")
    table.add_column("No", style="bold cyan", width=4)
    table.add_column("Nama", style="white")
    table.add_column("JK", style="white", width=3)
    table.add_column("NISN", style="yellow")
    table.add_column("NIK", style="dim")
    table.add_column("Kelas", style="cyan")
    table.add_column("Rombel", style="white")

    for i, s in enumerate(siswa[:20], 1):
        nama = s.get("nama", s.get("nama_lengkap", "-"))
        jk = s.get("jenis_kelamin", s.get("jk", "-"))
        nisn = s.get("nisn", "-")
        nik = s.get("nik", "-")
        kelas = s.get("kelas", s.get("tingkat", "-"))
        rombel = s.get("rombel", s.get("nama_rombel", "-"))
        table.add_row(
            str(i), str(nama)[:25], str(jk)[:3],
            str(nisn), str(nik), str(kelas), str(rombel)[:15]
        )
    console.print(table)

    if len(siswa) > 20:
        console.print(f"[dim]... dan {len(siswa) - 20} siswa lainnya (lihat JSON)[/dim]")

# ====================== MENU FITUR ======================
def menu_dumpsekolah():
    global USER_UID
    cost = FEATURES["dumpsekolah"]["cost"]

    if is_admin(USER_UID):
        console.print(f"[dim green]Admin — UNLIMITED[/dim green]")
    else:
        console.print(f"[dim]Biaya: {cost} limit/request[/dim]")

    ok, remaining = check_and_use_balance(USER_UID, "dumpsekolah")
    if not ok:
        console.print(f"[red]Balance tidak cukup![/red]")
        console.print(f"[yellow]Dibutuhkan {cost} limit. Balance: {remaining}[/yellow]")
        console.print("[yellow]Hubungi admin untuk top up.[/yellow]")
        input("\n[dim]Tekan Enter...[/dim]")
        return
    if remaining != "UNLIMITED":
        console.print(f"[dim]Balance tersisa: {remaining}[/dim]")

    npsn = Prompt.ask("[bold cyan]NPSN (8 digit)[/bold cyan]").strip()
    if not npsn or not npsn.isdigit() or len(npsn) != 8:
        console.print("[red]NPSN harus 8 digit![/red]")
        refund_balance(USER_UID, "dumpsekolah", "NPSN tidak valid")
        time.sleep(1.5)
        return

    console.print(f"[dim]Timeout: {TIMEOUT_DUMP} detik — mohon tunggu...[/dim]")
    loading_animation("Mengambil data siswa...", 2)
    data, error = fetch_siswa(npsn)

    # === REFUND KALAU ERROR/TIMEOUT ===
    if error:
        console.print(f"[red]Gagal: {error}[/red]")
        refund_balance(USER_UID, "dumpsekolah", error)
        input("\n[dim]Tekan Enter...[/dim]")
        return

    # === REFUND KALAU DATA INVALID ===
    if not data or data.get("status") != "ok":
        msg = data.get("pesan", "Unknown error") if data else "Tidak ada data"
        console.print(f"[red]Gagal: {msg}[/red]")
        refund_balance(USER_UID, "dumpsekolah", msg)
        input("\n[dim]Tekan Enter...[/dim]")
        return

    # === REFUND KALAU DATA SISWA KOSONG ===
    if not data.get("data") or len(data.get("data", [])) == 0:
        console.print("[red]Gagal: Data siswa kosong[/red]")
        refund_balance(USER_UID, "dumpsekolah", "Data siswa kosong")
        input("\n[dim]Tekan Enter...[/dim]")
        return

    display_siswa_data(data, npsn)

# ====================== MAIN ======================
def main():
    global USER_UID, USER_NAMA, USER_STATUS
    ensure_output_dir()

    DEVICE_ID = get_devid()
    users = load_users()
    user_data = None
    for u in users:
        if u.get('device_id') == DEVICE_ID:
            user_data = u
            break

    if user_data is None:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())
        console.print("[bold yellow]Registrasi Akun[/bold yellow]")
        console.print("[dim]Buat username (2-7 karakter, tanpa spasi)[/dim]")
        while True:
            username_input = Prompt.ask("[bold cyan]Username[/bold cyan]").strip()
            if (len(username_input) < 2 or len(username_input) > 7 or
                " " in username_input or not re.match(r'^[a-zA-Z0-9_]+$', username_input)):
                console.print("[red]Username tidak sesuai aturan![/red]")
                continue
            break
        loading_spinner(1.5, "Mengirim data registrasi...")
        kirim_registrasi_telegram(DEVICE_ID, username_input)
        add_pending(DEVICE_ID, username_input)
        console.print("[bold green]Data terkirim! Tunggu admin approve.[/bold green]")
        console.print(f"[dim]Device ID kamu: {DEVICE_ID}[/dim]")
        console.print("[dim]Kirim Device ID ini ke admin untuk didaftarkan.[/dim]")
        sys.exit(0)

    USER_UID = user_data.get("device_id", DEVICE_ID)
    USER_NAMA = user_data.get("nama", "Unknown")
    USER_STATUS = user_data.get("role", "user")

    if user_data.get("status") == "banned":
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())
        console.print(Panel(
            "[bold red]AKUN ANDA DI-BAN[/bold red]\n\n"
            f"[white]Device ID:[/white] {USER_UID}\n"
            f"[white]Nama:[/white] {USER_NAMA}\n\n"
            "[yellow]Hubungi admin untuk info lebih lanjut:[/yellow]\n"
            "[cyan]Telegram:[/cyan] @denzkucai\n"
            "[cyan]WhatsApp:[/cyan] 6285389400823",
            title="[bold red]ACCESS DENIED[/bold red]",
            border_style="red",
            box=box.HEAVY
        ))
        sys.exit(0)

    while True:
        users = load_users()
        for u in users:
            if u.get('device_id') == USER_UID:
                user_data = u
                break

        if user_data.get("status") == "banned":
            os.system('clear' if os.name == 'posix' else 'cls')
            console.print(get_header())
            console.print(show_banner())
            console.print(Panel(
                "[bold red]AKUN ANDA DI-BAN[/bold red]\n\n"
                "[yellow]Hubungi admin:[/yellow]\n"
                "[cyan]Telegram:[/cyan] @denzkucai\n"
                "[cyan]WhatsApp:[/cyan] 6285389400823",
                title="[bold red]ACCESS DENIED[/bold red]",
                border_style="red",
                box=box.HEAVY
            ))
            sys.exit(0)

        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())

        info_table = Table(box=box.ROUNDED, border_style='blue')
        info_table.add_column("Item", style="bold cyan")
        info_table.add_column("Value", style="white")
        info_table.add_row("Device ID", USER_UID)
        info_table.add_row("Nama", USER_NAMA)
        role_display = "[bold green]ADMIN (UNLIMITED)[/bold green]" if USER_STATUS == "admin" else USER_STATUS
        info_table.add_row("Role", role_display)
        console.print(info_table)

        show_user_balance(user_data)
        console.print(f"[dim]Output: {OUTPUT_DIR}[/dim]\n")

        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")

        items = [
            ("01", "Dump Sekolah (Siswa Aktif) [2 limit]"),
            ("02", "Buka Folder Output"),
        ]
        for no, label in items:
            menu_table.add_row(no, label)

        menu_table.add_row("00", "[red]Exit[/red]")
        console.print(Panel(menu_table, title="[bold blue]DoxSchool Menu[/bold blue]", border_style="blue"))

        pilihan = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]")

        if pilihan in ["0", "00"]:
            console.print("[yellow]Keluar...[/yellow]")
            break
        elif pilihan in ["1", "01"]:
            menu_dumpsekolah()
            input("\n[dim]Tekan Enter...[/dim]")
        elif pilihan in ["2", "02"]:
            os.system(f'ls -la "{OUTPUT_DIR}"')
            input("\n[dim]Tekan Enter...[/dim]")
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(1)

def dox():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)