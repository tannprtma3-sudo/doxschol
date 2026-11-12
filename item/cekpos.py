#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CEK KODE POS — SHADOWDEATH EDITION
Cari kode pos Indonesia via API
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
API_URL = "https://api-danxy-tools-satu-dua-tiga-api-y.vercel.app/api/osint/kodepos"

# ── UI HEADER ──
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]KODE POS[/bold blue] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]CEK KODE POS[/bold white]\n'
        '    {`"\'}    [dim]Cari kode pos Indonesia[/dim]\n'
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
def cari_kodepos(kodepos):
    """Cari kode pos berdasarkan kode pos (5 digit)"""
    try:
        resp = requests.get(f"{API_URL}?kodepos={kodepos}", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success') == True and data.get('data'):
                return data['data']
        return []
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return []

# ── DISPLAY ──
def display_results(results, kodepos):
    if not results:
        console.print(f"[yellow]Kode pos {kodepos} tidak ditemukan.[/yellow]")
        return
    
    # Ambil data pertama (biasanya cuma 1)
    item = results[0] if isinstance(results, list) else results
    
    # ── Tampilan Panel ──
    content = (
        f"[bold blue]Kode Pos:[/bold blue] [white]{item.get('kodepos', '-')}[/white]\n"
        f"[bold blue]Desa/Kelurahan:[/bold blue] [white]{item.get('desa', '-')}[/white]\n"
        f"[bold blue]Kecamatan:[/bold blue] [white]{item.get('kecamatan', '-')}[/white]\n"
        f"[bold blue]Kabupaten/Kota:[/bold blue] [white]{item.get('kabupaten', '-')}[/white]\n"
        f"[bold blue]Provinsi:[/bold blue] [white]{item.get('provinsi', '-')}[/white]\n"
        f"[dim]No: {item.get('no', '-')}[/dim]"
    )
    
    console.print(Panel(
        content,
        title="HASIL CEK KODE POS",
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
        menu_table.add_row("01", "[bold white]Cari Kode Pos[/bold white]")
        menu_table.add_row("02", "[bold white]Batch Cari (from file)[/bold white]")
        menu_table.add_section()
        menu_table.add_row("00", "[bold red]Exit[/bold red]")
        
        console.print(Panel(menu_table, title="[bold blue]CEK KODE POS[/bold blue]", border_style="blue"))
        console.print(get_footer())
        
        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")
        
        if choice in ["0", "00"]:
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break
        elif choice in ["1", "01"]:
            menu_cari()
        elif choice in ["2", "02"]:
            menu_batch()
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(1)

def menu_cari():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    
    kodepos = Prompt.ask("[bold blue]Masukkan kode pos (5 digit)")
    if not kodepos:
        return
    
    # Bersihkan input (hanya angka)
    kodepos = re.sub(r'[^0-9]', '', kodepos)
    
    if len(kodepos) != 5:
        console.print("[red]Kode pos harus 5 digit angka![/red]")
        input("\n[dim]Tekan Enter...[/dim]")
        return
    
    loading_animation(f"[blue]Mencari kode pos {kodepos}...[/blue]", 2)
    results = cari_kodepos(kodepos)
    display_results(results, kodepos)
    
    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

def menu_batch():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    
    filepath = Prompt.ask("[bold blue]Path file (satu kode pos per baris)")
    if not os.path.exists(filepath):
        console.print("[bold red]File tidak ditemukan.[/bold red]")
        input("\n[dim]Tekan Enter...[/dim]")
        return
    
    with open(filepath, 'r') as f:
        kodepos_list = [line.strip() for line in f if line.strip()]
    
    if not kodepos_list:
        console.print("[bold yellow]File kosong.[/bold yellow]")
        input("\n[dim]Tekan Enter...[/dim]")
        return
    
    console.print(f"[blue]{len(kodepos_list)} kode pos ditemukan.[/blue]")
    
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
        task = progress.add_task("[blue]Mencari...", total=len(kodepos_list))
        for kp in kodepos_list:
            kp = re.sub(r'[^0-9]', '', kp)
            if len(kp) == 5:
                res = cari_kodepos(kp)
                results.append({'kodepos': kp, 'results': res, 'found': len(res) > 0})
            else:
                results.append({'kodepos': kp, 'results': [], 'found': False})
            progress.update(task, advance=1)
            time.sleep(0.3)
    
    # Summary
    table = Table(title="BATCH RESULTS", box=box.ROUNDED, border_style='blue')
    table.add_column("No", style="blue", width=4)
    table.add_column("Kode Pos", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Desa", style="white")
    
    for idx, res in enumerate(results, 1):
        status = "✅" if res['found'] else "❌"
        desa = res['results'][0].get('desa', '-') if res['found'] else '-'
        table.add_row(str(idx), res['kodepos'], status, desa)
    console.print(table)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    outfile = f"kodepos_batch_{timestamp}.json"
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    console.print(f"[dim]Saved: {outfile}[/dim]")
    
    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

def cekpos():
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Force Exit Detected.[/bold red]")
        sys.exit(2)