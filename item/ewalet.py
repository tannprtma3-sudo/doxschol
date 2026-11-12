#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
E-WALLET CHECKER v2.0 — Ghost-Track UI (Dual API)
by denz
"""

import os
import sys
import time
import json
import re
import requests
from datetime import datetime

# ── Install dependencies if missing ──
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
except ImportError:
    os.system('pip install rich')
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box

console = Console()

# ── Konfigurasi API ──
API_PRIMARY = "https://lambent-lebkuchen-e109a8.netlify.app/api/ewallet"
API_BACKUP = "https://lambent-lebkuchen-e109a8.netlify.app/api/ewallet"

# ── Ghost-Track UI ──
def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]E-WALLET CHECKER[/bold white]\n'
        '    {`"\'}    [dim]Check e-wallet from phone number[/dim]\n'
        '    -"-"-    [dim]coded by [bold blue]denz[/bold blue][/dim][/bold blue]\n    '
    )
    return Align.center(Text.from_markup(logo))

def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]E-WALLET CHECKER[/bold blue] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

# ── Utility ──
def format_phone(phone):
    phone = phone.strip()
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('62'):
        phone = '0' + phone[2:]
    elif not phone.startswith('0'):
        phone = '0' + phone
    if len(phone) < 10:
        return None
    return phone

def check_ewallet(phone, api_url):
    try:
        resp = requests.get(api_url, params={"phone_number": phone}, timeout=30)
        return resp.status_code, resp.text
    except Exception as e:
        return 0, str(e)

def fetch_ewallet(phone):
    # Coba primary
    status, raw = check_ewallet(phone, API_PRIMARY)
    if status == 200:
        return status, raw, "Primary"
    # Coba backup
    status, raw = check_ewallet(phone, API_BACKUP)
    if status == 200:
        return status, raw, "Backup"
    return status, raw, "Failed"

# ── Display ──
def display_result(status_code, raw_text, phone, source):
    console.print(f"[dim]Status Code: {status_code} | Source: {source}[/dim]")
    console.print(f"[dim]Nomor: {phone}[/dim]")
    
    try:
        data = json.loads(raw_text)
    except:
        console.print("[red]Response bukan JSON yang valid.[/red]")
        console.print(f"[dim]Raw: {raw_text[:500]}[/dim]")
        return

    console.print(Panel(json.dumps(data, indent=2, ensure_ascii=False),
                        title="[bold red]RAW JSON[/bold red]",
                        border_style="red"))

    if isinstance(data, dict):
        if data.get("status") == "error" or data.get("success") == False:
            console.print(f"[red]API Error: {data.get('message', 'Unknown error')}[/red]")
            return

        results = data.get("data", data.get("result", data))
        if not results:
            console.print("[yellow]⚠️ Tidak ada data ditemukan untuk nomor ini.[/yellow]")
            return

        if isinstance(results, dict):
            table = Table(box=box.ROUNDED, border_style='blue',
                         title=f"[bold white]HASIL CEK E-WALLET[/bold white]\n[dim]Nomor: {phone}[/dim]")
            table.add_column("E-Wallet", style="bold cyan")
            table.add_column("Status", style="white")
            table.add_column("Detail", style="dim")

            for wallet, info in results.items():
                if isinstance(info, dict):
                    status = info.get("status", "-")
                    detail = info.get("detail", "-") or info.get("message", "-")
                    if status == "registered":
                        status_display = "[green]Terdaftar[/green]"
                    elif status == "unregistered":
                        status_display = "[red]Tidak terdaftar[/red]"
                    else:
                        status_display = f"[yellow]{status}[/yellow]"
                    table.add_row(wallet.upper(), status_display, str(detail)[:50])
                else:
                    table.add_row(wallet.upper(), "[yellow]Unknown[/yellow]", str(info)[:50])
            console.print(table)
        else:
            console.print("[yellow]Format data tidak dikenali.[/yellow]")
            console.print(f"[dim]{results}[/dim]")

# ─── Main ──
def main():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True, border_style='blue')
        menu_table.add_column("No", justify="center", style="bold blue", width=4)
        menu_table.add_column("Menu", justify="left", style="white")

        menu_items = [
            ("01", "Cek E-Wallet"),
            ("00", "Exit")
        ]
        for no, label in menu_items:
            menu_table.add_row(no, label)

        console.print(Panel(menu_table, title="[bold blue]E-WALLET CHECKER[/bold blue]", border_style="blue"))

        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")

        if choice in ["0", "00"]:
            console.print("[yellow]Keluar...[/yellow]")
            break
        elif choice in ["1", "01"]:
            phone_input = Prompt.ask("[bold blue]Masukkan nomor HP (08xx atau 628xx)[/bold blue]").strip()
            if not phone_input:
                console.print("[red]Nomor tidak boleh kosong![/red]")
                time.sleep(1)
                continue

            phone = format_phone(phone_input)
            if not phone:
                console.print("[red]Format nomor tidak valid! Minimal 10 digit.[/red]")
                time.sleep(1)
                continue

            with Progress(SpinnerColumn(), TextColumn("[bold blue]Mengecek e-wallet...[/bold blue]"), console=console, transient=True) as progress:
                progress.add_task("", total=None)
                status_code, raw, source = fetch_ewallet(phone)

            if status_code == 0:
                console.print(f"[red]Gagal terhubung ke API (Primary & Backup).[/red]")
                console.print(f"[dim]{raw[:200]}[/dim]")
            else:
                display_result(status_code, raw, phone, source)

            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(0.5)

def ewalet():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
