#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CEK NOPOL — SHADOWDEATH EDITION
Cek data plat nomor kendaraan via Firestore Samsat
UI: Ghost-Track Style (Blue Theme)
coded by denz
"""

import os
import sys
import time
import json
import re
import requests
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import box
    from rich.syntax import Syntax
except ImportError:
    os.system('pip install rich')
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

VERSION = "v1.0"
CODED_BY = "denz"

# ── API ──
FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/informasisamsat/databases/(default)/documents/nopol"

# ── UI HEADER ──
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]CEK NOPOL[/bold blue] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]CEK NOPOL[/bold white]\n'
        '    {`"\'}    [dim]Cek data plat nomor kendaraan[/dim]\n'
        '    -"-"-    [dim]coded by [bold blue]denz[/bold blue][/dim][/bold blue]\n    '
    )
    return Align.center(Text.from_markup(logo))

def get_footer():
    return Panel(
        "[dim]Powered by python[/dim]",
        style="dim",
        border_style="blue",
        box=box.HEAVY
    )

def loading_animation(task_name, duration=2):
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold blue]{task.description}'),
        BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task(task_name, total=100)
        step = 100 / (duration * 10)
        while not progress.finished:
            progress.update(task, advance=step)
            time.sleep(0.1)

# ── API FUNCTIONS ──
def cek_nopol(plat):
    """Cek data plat nomor kendaraan"""
    # Format: KH 1234 AB
    plat = plat.strip().upper()
    plat = re.sub(r'\s+', ' ', plat)
    
    # Ekstrak kode provinsi dan huruf belakang
    match = re.match(r'^([A-Z]{1,2})\s+.*?([A-Z]{1})$', plat)
    if not match:
        return {'success': False, 'error': 'Format plat tidak valid'}
    
    kode_provinsi = match.group(1)
    huruf_belakang = match.group(2)
    
    try:
        url = f"{FIRESTORE_URL}/{kode_provinsi}/belakang/{huruf_belakang}"
        resp = requests.get(url, timeout=15)
        
        if resp.status_code != 200:
            return {'success': False, 'error': f'HTTP {resp.status_code}'}
        
        data = resp.json()
        fields = data.get('fields', {})
        
        if not fields:
            return {'success': False, 'error': 'Data tidak ditemukan'}
        
        result = {
            'success': True,
            'plat': plat,
            'kode_provinsi': kode_provinsi,
            'huruf_belakang': fields.get('Huruf', {}).get('stringValue', '-'),
            'provinsi': fields.get('Provinsi', {}).get('stringValue', '-'),
            'daerah': fields.get('Daerah', {}).get('stringValue', '-'),
            'samsat': fields.get('Samsat', {}).get('stringValue', '-'),
            'alamat': fields.get('Alamat', {}).get('stringValue', '-')
        }
        return result
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ── DISPLAY ──
def display_result(result):
    if not result.get('success'):
        console.print(f"[bold red]Error: {result.get('error', 'Unknown error')}[/bold red]")
        return
    
    console.print(Panel(
        f"[bold blue]Plat Nomor:[/bold blue] [white]{result['plat']}[/white]\n"
        f"[bold blue]Kode Provinsi:[/bold blue] [white]{result['kode_provinsi']}[/white]\n"
        f"[bold blue]Huruf Belakang:[/bold blue] [white]{result['huruf_belakang']}[/white]\n"
        f"[bold blue]Provinsi:[/bold blue] [white]{result['provinsi']}[/white]\n"
        f"[bold blue]Kota/Kab:[/bold blue] [white]{result['daerah']}[/white]\n"
        f"[bold blue]Samsat:[/bold blue] [white]{result['samsat']}[/white]\n"
        f"[bold blue]Alamat:[/bold blue] [white]{result['alamat']}[/white]",
        title="HASIL CEK NOPOL",
        border_style="blue",
        box=box.HEAVY
    ))

# ── MAIN MENU ──
def main_menu():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())
        
        menu_table = Table(
            box=box.DOUBLE_EDGE,
            show_header=False,
            expand=True,
            border_style='blue',
            padding=(0, 1)
        )
        menu_table.add_column("No", justify="center", style="bold blue", width=4)
        menu_table.add_column("Menu", justify="left", style="white")
        menu_table.add_row("01", "[bold white]Cek Plat Nomor[/bold white]")
        menu_table.add_row("02", "[bold white]Batch Cek (from file)[/bold white]")
        menu_table.add_section()
        menu_table.add_row("00", "[bold red]Exit[/bold red]")
        
        console.print(Panel(menu_table, title="[bold blue]CEK NOPOL[/bold blue]", border_style="blue"))
        console.print(get_footer())
        
        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")
        
        if choice in ["0", "00"]:
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break
        elif choice in ["1", "01"]:
            menu_cek()
        elif choice in ["2", "02"]:
            menu_batch()
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(1)

def menu_cek():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    
    plat = Prompt.ask("[bold blue]Masukkan plat nomor (contoh: KH 1234 AB)")
    if not plat:
        return
    
    loading_animation(f"[blue]Mencari data plat {plat}...[/blue]", 2)
    result = cek_nopol(plat)
    display_result(result)
    
    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

def menu_batch():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    
    filepath = Prompt.ask("[bold blue]Path file (satu plat per baris)")
    if not os.path.exists(filepath):
        console.print("[bold red]File tidak ditemukan.[/bold red]")
        input("\n[dim]Tekan Enter...[/dim]")
        return
    
    with open(filepath, 'r') as f:
        plats = [line.strip() for line in f if line.strip()]
    
    if not plats:
        console.print("[bold yellow]File kosong.[/bold yellow]")
        input("\n[dim]Tekan Enter...[/dim]")
        return
    
    console.print(f"[blue]{len(plats)} plat ditemukan.[/blue]")
    
    if not Confirm.ask("[bold blue]Lanjutkan?", default=True):
        return
    
    results = []
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold blue]{task.description}'),
        BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task("[blue]Mencari...", total=len(plats))
        for plat in plats:
            result = cek_nopol(plat)
            results.append({'plat': plat, 'result': result})
            progress.update(task, advance=1)
            time.sleep(0.3)
    
    # Summary
    table = Table(title="BATCH RESULTS", box=box.ROUNDED, border_style='blue')
    table.add_column("No", style="blue", width=4)
    table.add_column("Plat", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Provinsi", style="white")
    
    for idx, res in enumerate(results, 1):
        status = "✅" if res['result'].get('success') else "❌"
        prov = res['result'].get('provinsi', '-') if res['result'].get('success') else '-'
        table.add_row(str(idx), res['plat'], status, prov)
    console.print(table)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    outfile = f"nopol_batch_{timestamp}.json"
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    console.print(f"[dim]Saved: {outfile}[/dim]")
    
    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

def nopol():
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Force Exit Detected.[/bold red]")
        sys.exit(2)
