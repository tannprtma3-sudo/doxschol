#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GETCONTACT TOOL v1.2 — Ghost-Track UI (Update API)
by denz
"""

import os
import sys
import time
import re
import json
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

# ── Konfigurasi ──
API_URL = "https://api.comiku.my.id/api/search"
API_KEY = "gtc_d29f86f5a9952ce0570d193401001c8220e14caced32ccf3"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# ── Ghost-Track UI ──
def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]GETCONTACT TOOL[/bold white]\n'
        '    {`"\'}    [dim]Phone number lookup[/dim]\n'
        '    -"-"-    [dim]coded by [bold blue]denz[/bold blue][/dim][/bold blue]\n    '
    )
    return Align.center(Text.from_markup(logo))

def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]GETCONTACT TOOL[/bold blue] [bold white]v1.2[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

# ── Utility ──
def format_phone(phone):
    phone = re.sub(r'[^0-9+]', '', phone)
    if not phone.startswith('+'):
        if phone.startswith('0'):
            phone = '+62' + phone[1:]
        else:
            phone = '+' + phone
    return phone

# ── API Call ──
def search_phone(phone, detail=False):
    # Format phone tanpa '+' untuk API
    raw_phone = phone.lstrip('+')
    payload = {
        "phone": raw_phone,
        "country_code": "ID",
        "source": "detail" if detail else "search"
    }
    try:
        resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        return resp.status_code, resp.json()
    except Exception as e:
        return 0, {"error": str(e)}

# ── Display (Table Rapi) ──
def display_result(data, phone, detail=False):
    if "error" in data:
        console.print(f"[red]❌ Error: {data['error']}[/red]")
        return

    # Cek status: ok
    if data.get("ok") is False:
        console.print(f"[yellow]{data.get('message', 'No data found')}[/yellow]")
        return

    # Ambil profile
    profile = data.get("profile", {})
    if not profile:
        console.print("[yellow]Tidak ada data ditemukan untuk nomor ini.[/yellow]")
        console.print(f"[dim]Raw: {json.dumps(data, indent=2)}[/dim]")
        return

    # ── Info utama ──
    table = Table(box=box.ROUNDED, border_style='blue', title=f"[bold white]📱 HASIL GETCONTACT[/bold white]\n[dim]{phone}[/dim]")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")

    # Isi data dari profile
    fields = [
        ("Display Name", profile.get("displayName")),
        ("Phone Number", profile.get("phoneNumber")),
        ("Display Number", profile.get("displayNumber")),
        ("Country", profile.get("country")),
        ("Country Code", profile.get("countryCode")),
        ("Name", profile.get("name")),
        ("Surname", profile.get("surname")),
        ("Tag Count", profile.get("tagCount")),
        ("Email", profile.get("email")),
        ("Trust Score", profile.get("trustScore")),
        ("Profile Image", "✅ Ada" if profile.get("profileImage") else "❌ Tidak"),
    ]

    for label, value in fields:
        if value is not None and value != "":
            table.add_row(label, str(value))

    # Tambahan info dari root
    table.add_row("[bold cyan]Source[/bold cyan]", data.get("source", "-"))
    table.add_row("[bold cyan]From Cache[/bold cyan]", "✅" if data.get("fromCache") else "❌")

    console.print(table)

    # ── Tags (jika ada) ──
    tags = data.get("tags", [])
    if tags:
        tag_table = Table(box=box.ROUNDED, border_style='cyan', title="[bold white]🏷️ TAGS[/bold white]")
        tag_table.add_column("No", style="bold cyan", width=4)
        tag_table.add_column("Tag", style="white")
        tag_table.add_column("Count", style="yellow")
        for i, tag in enumerate(tags[:20], 1):
            tag_table.add_row(str(i), tag.get("tag", "-"), str(tag.get("count", 0)))
        console.print(tag_table)
        if len(tags) > 20:
            console.print(f"[dim]... dan {len(tags)-20} tags lainnya[/dim]")

    # ── Raw JSON (opsional) ──
    if Confirm.ask("[cyan]Tampilkan raw JSON?[/cyan]", default=False):
        console.print(Panel(json.dumps(data, indent=2, ensure_ascii=False),
                           title="[bold red]RAW JSON[/bold red]",
                           border_style="red"))

# ── Menu ──
def menu_search(detail=False):
    mode = "Detail" if detail else "Basic"
    console.print(f"\n[bold yellow]{mode} Search[/bold yellow]")
    phone_input = Prompt.ask("[bold blue]Nomor HP (contoh: 62812xxxx atau +62812xxxx)[/bold blue]").strip()
    if not phone_input:
        console.print("[red]Nomor tidak boleh kosong![/red]")
        return

    phone = format_phone(phone_input)
    console.print(f"[dim]Format: {phone}[/dim]")

    with Progress(SpinnerColumn(), TextColumn("[bold blue]Mencari data...[/bold blue]"), console=console, transient=True) as progress:
        progress.add_task("", total=None)
        status, data = search_phone(phone, detail)

    if status == 0:
        console.print(f"[red]❌ Gagal terhubung ke API: {data.get('error', 'Unknown error')}[/red]")
        return
    if status != 200:
        console.print(f"[red]❌ HTTP Error {status}: {data}[/red]")
        return

    display_result(data, phone, detail)

# ── Main ──
def main():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True, border_style='blue')
        menu_table.add_column("No", justify="center", style="bold blue", width=4)
        menu_table.add_column("Menu", justify="left", style="white")

        menu_items = [
            ("01", "Search Phone (Basic)"),
            ("02", "Search Phone (Detail)"),
            ("00", "Exit")
        ]
        for no, label in menu_items:
            menu_table.add_row(no, label)

        console.print(Panel(menu_table, title="[bold blue]GETCONTACT TOOL[/bold blue]", border_style="blue"))

        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")

        if choice in ["0", "00"]:
            console.print("[yellow]Keluar...[/yellow]")
            break
        elif choice in ["1", "01"]:
            menu_search(detail=False)
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        elif choice in ["2", "02"]:
            menu_search(detail=True)
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(0.5)

def phone():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)