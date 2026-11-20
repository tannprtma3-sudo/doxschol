#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GHOST-CRACK OWL v5.4 — SHADOWDEATH EDITION (GitHub Database)
Main Launcher + GitHub DB + Pending Registration
coded by AlexsaEnv404
"""

import sys
sys.dont_write_bytecode = True
import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import time
import re
import json
import random
import socket
import requests
import subprocess
import threading
import concurrent.futures
import base64
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from rich.syntax import Syntax

console = Console()

# ====================== IMPORTS FROM ITEMS ======================
try:
    from item.tiktok import tiktok
except ImportError:
    tiktok = None
try:
    from item.ip import ip
except ImportError:
    ip = None
try:
    from item.ngl import ngl_run
except ImportError:
    ngl_run = None
try:
    from item.exploit import memek
except ImportError:
    memek = None
try:
    from item.web_recon import recon
except ImportError:
    recon = None
try:
    from item.server import server
except ImportError:
    server = None
try:
    from item.osintusr import osint
except ImportError:
    osint = None
try:
    from item.osinttele import teleg
except ImportError:
    teleg = None
try:
    from item.leak import leaktol
except ImportError:
    leaktol = None
try:
    from item.phone import phone
except ImportError:
    phone = None
try:
    from item.imei import imei2
except ImportError:
    imei2 = None
try:
    from item.ewalet import ewalet
except ImportError:
    ewalet = None
try:
    from item.ptkg import guru
except ImportError:
    guru = None
try:
    from item.cell import cell
except ImportError:
    cell = None
try:
    from item.craw import craw
except ImportError:
    craw = None
try:
    from item.pesan import pesan
except ImportError:
    pesan = None
try:
    from item.nik import nik
except ImportError:
    nik = None
try:
    from item.bot import tele
except ImportError:
    tele = None
try:
    from item.yt import yt
except ImportError:
    yt = None
try:
    from item.spotify import spotify
except ImportError:
    spotify = None
try:
    from item.cekpos import cekpos
except ImportError:
    cekpos = None
try:
    from item.nopol import nopol
except ImportError:
    nopol = None
try:
    from item.dox import dox
except ImportError:
    dox = None
# ====================== KONFIGURASI GITHUB ======================
GITHUB_USERNAME = "tannprtma3-sudo"
REPO_NAME       = "GhostTrack"
KEYS_FILE       = "Track.txt"
PENDING_FILE    = "pending.txt"
GITHUB_TOKEN = "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"
BOT_REGISTER = "8679925779:AAFvK8bb6dfZkaRXunyMUMrH0j8VHPeK5ps"
ADMIN_TELE   = "1737506442"

USER_UID = "-"
USER_NAMA = "-"
USER_STATUS = "-"
IP_ADDRESS = ""
IP_SENSOR = True

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]GHOST-CRACK[/bold cyan] [bold white]v5.6[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = r"""
   [bold red]  ,_,
    (o,o)    [bold white]GHOST-CRACK[/bold white]
    {`"'}    [dim]Ultimate Tool Kit Launcher[/dim]
    -"-"-    [dim]coded by [bold cyan]AlexsaEnv404[/bold cyan][/dim][/bold red]
    """
    return Align.center(Text.from_markup(logo))

# ====================== GITHUB DATABASE FUNCTIONS ======================
def github_get_file(filename):
    """Ambil isi file dari GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{filename}"
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.text
        return None
    except:
        return None

def github_put_file(filename, content, commit_msg="Update file"):
    """Simpan file ke GitHub"""
    encoded = base64.b64encode(content.encode()).decode()
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{filename}"
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }
    # Get SHA if exists
    sha = None
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            sha = resp.json().get('sha')
    except:
        pass
    payload = {
        'message': commit_msg,
        'content': encoded,
        'branch': 'main'
    }
    if sha:
        payload['sha'] = sha
    try:
        resp = requests.put(url, headers=headers, json=payload, timeout=30)
        return resp.status_code in [200, 201]
    except:
        return False

def load_users():
    try:
        content = github_get_file(KEYS_FILE)
        if not content:
            return []
        users = []
        for line in content.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.strip().split('|')
            if len(parts) >= 4:
                users.append({
                    'device_id': parts[0],
                    'role': parts[1],
                    'username': parts[2],
                    'status': parts[3],
                    'expired': parts[4] if
  len(parts) > 4 else '0'
                })
        return users
    except:
        return []
def save_users(users):
    """Save users to keys.txt"""
    lines = []
    for u in users:
        line = f"{u.get('device_id')}-{u.get('role')}-{u.get('nama')}-{u.get('status')}"
        lines.append(line)
    content = '\n'.join(lines)
    return github_put_file(KEYS_FILE, content, "Update users via Ghost-Crack")

def load_pending():
    """Load pending registrations from pending.txt"""
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
                'timestamp': parts[2] if len(parts) > 2 else str(int(time.time()))
            })
    return pendings

def save_pending(pendings):
    """Save pending to pending.txt"""
    lines = []
    for p in pendings:
        line = f"{p.get('device_id')}|{p.get('nama')}|{p.get('timestamp')}"
        lines.append(line)
    content = '\n'.join(lines)
    return github_put_file(PENDING_FILE, content, "Update pending via Ghost-Crack")

def add_pending(device_id, nama):
    """Add pending registration"""
    pendings = load_pending()
    # Cek duplikat
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
def get_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except:
        return "N/A"

def sensor_ip(ip):
    try:
        hasil = ""
        for char in str(ip):
            if char == ".":
                hasil += "."
            elif char.isdigit():
                hasil += "×"
            else:
                hasil += char
        return hasil
    except:
        return ip

def toggle_sensor_ip():
    global IP_SENSOR
    IP_SENSOR = not IP_SENSOR
    console.print(f"[green]IP Sensor {'Enabled' if IP_SENSOR else 'Disabled'}[/green]")

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
        raw = f"{whoami}{serial}{android_id}{build_id}{fingerprint}{inode}"
        raw = re.sub(r'[^a-zA-Z0-9]', '', raw)
        hashed = hashlib.sha256(raw.encode()).hexdigest()[:20]
        return hashed
    except:
        try:
            import hashlib
            fallback = os.popen('whoami').read().strip() + str(os.getuid())
            return hashlib.md5(fallback.encode()).hexdigest()[:20]
        except:
            return "unknown"

def kirim_registrasi_telegram(device_id, username):
    pesan = f"""
📨 Pending Registrasi Masuk

ID PENGGUNA
`{device_id}`

NAMA AKUN
`{username}`

Gunakan admin panel untuk approve.
"""
    try:        # Kirim data ke pending.txt GitHub
        new_entry = f"{device_id}|vip|{username}|pending|2026-12-31\n"
        existing_pending = github_get_file(PENDING_FILE) or ""
        updated_pending = existing_pending + new_entry if existing_pending else new_entry
        ok = github_put_file(PENDING_FILE, updated_pending, f"Registrasi user {username}")
        if not ok:
            return False

        requests.post(
            f"https://api.telegram.org/bot{BOT_REGISTER}/sendMessage",
            json={
                "chat_id": ADMIN_TELE,
                "text": pesan,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def loading_spinner(duration=1.5, text="Loading"):
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn(f'[bold cyan]{text}'),
        console=console,
    ) as progress:
        progress.add_task("", total=None)
        time.sleep(duration)

# ==================== MAIN ====================
def main():
    global USER_UID, USER_NAMA, USER_STATUS, IP_ADDRESS, IP_SENSOR

    DEVICE_ID = get_devid()
    with open('/data/data/com.termux/files/home/gt/ghost-track/debug_id.txt', 'w') as f:
        f.write(DEVICE_ID)
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
        console.print("[dim]Buat username (2-7 karakter, tanpa spasi, contoh: alfanumerik)[/dim]")
        while True:
            username_input = Prompt.ask("[bold cyan]Username[/bold cyan]")
            if (
                len(username_input) < 2 or
                len(username_input) > 7 or
                " " in username_input or
                not re.match(r'^[a-zA-Z0-9_]+$', username_input)
            ):
                console.print("[red]Username tidak sesuai aturan![/red]")
                continue
            break
        loading_spinner(1.5, "Mengirim data registrasi...")
        # Kirim ke Telegram dan simpan pending
        success = kirim_registrasi_telegram(DEVICE_ID, username_input)
        if success:
            console.print("[bold green]Data terkirim! Tunggu admin Alexsa approve.[/bold green]")
        else:
            console.print("[bold red]Gagal kirim data, cek token/koneksi.[/bold red]")
        sys.exit(0)

    USER_UID = user_data.get("device_id", DEVICE_ID)
    USER_NAMA = user_data.get("nama", "Unknown")
    USER_STATUS = user_data.get("role", "user")
    IP_ADDRESS = get_ip()

    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())

        # Info user
        ip_display = sensor_ip(IP_ADDRESS) if IP_SENSOR else IP_ADDRESS
        info_table = Table(box=box.ROUNDED, border_style='blue')
        info_table.add_column("Item", style="bold cyan")
        info_table.add_column("Value", style="white")
        info_table.add_row("IP", ip_display)
        info_table.add_row("ID", USER_UID)
        info_table.add_row("Nama", USER_NAMA)
        info_table.add_row("Status", USER_STATUS)
        info_table.add_row("Users", str(len(users)))
        console.print(info_table)

        # Menu
        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")

        menu_items = [
            ("01", "osint telegram"),
            ("02", "osint sekolah Indonesia"),
            ("03", "osint username"),
            ("04", "dump database sekolah"),
            ("05", "nik Checker"),
            ("06", "telegram Spam Bot"),
            ("07", "osint tiktok"),
            ("08", "web Recon (Ultra Brutal)"),
            ("09", "rat Control (Remote Ransomware)"),
            ("10", "crack IP Address"),
            ("11", "web directory scanner"),
            ("12", "Instagram stalker"),
            ("13", f"{'Tampilkan' if IP_SENSOR else 'Sembunyikan'} IP Saya"),
            ("14", "cek imei"),
            ("15", "cek data guru"),
            ("16", "cellmapper lookup"),
            ("17", "e-wallet Checker"),
            ("18", "gmail craw"),
            ("19", "YouTube video stalk details"),
            ("20", "youtube stalker"),
            ("21", "cek kode pos"),
            ("22", "cek plat kendaraan"),
            ("23", "spotify downloader"),
            ("00", "keluar")
        ]
        for no, label in menu_items:
            menu_table.add_row(no, label)

        console.print(Panel(menu_table, title="[bold blue]MENU[/bold blue]", border_style="blue"))

        pilihan = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]")

        if pilihan in ["1", "01"]:
            if teleg: teleg()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["2", "02"]:
            if leaktol: leaktol()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["3", "03"]:
            if osint: osint()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["4", "04"]:
            if dox: dox()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["5", "05"]:
            if nik: nik()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["6", "06"]:
            if tele: tele()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["7", "07"]:
            if tiktok: tiktok()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["8", "08"]:
            if recon: recon()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["9", "09"]:
            if server: server()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["10"]:
            if ip: ip()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["11"]:
            if ngl_run: ngl_run()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["12"]:
            if memek: memek()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["13"]:
            toggle_sensor_ip()
        elif pilihan in ["14"]:
            if imei2: imei2()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["15"]:
            if guru: guru()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["16"]:
            if cell: cell()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["17"]:
            if ewalet: ewalet()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["18"]:
            if craw: craw()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["19"]:
            if pesan: pesan()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["20"]:
            if yt: yt()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["21"]:
            if cekpos: cekpos()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["22"]:
            if nopol: nopol()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["23"]:
            if spotify: spotify()
            else: console.print("[red]Module not available[/red]")
        elif pilihan in ["0", "00"]:
            console.print("[yellow]Keluar...[/yellow]")
            break
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
