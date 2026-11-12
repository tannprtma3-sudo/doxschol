import os
import sys
import time
import re
import json
import requests
from datetime import datetime  # <--- FIX: tambahin ini
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.syntax import Syntax
from rich.layout import Layout
from rich.live import Live
from rich.columns import Columns
from rich.console import Group

console = Console()

# ====================== KONFIGURASI ======================
NIK_API_URL = "https://danxyofficial-api.vercel.app/tools/nik"

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]NIK CHECKER[/bold cyan] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = r"""
   [bold yellow]███╗   ██╗██╗██╗  ██╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
   ████╗  ██║██║██║ ██╔╝     ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
   ██╔██╗ ██║██║█████╔╝█████╗██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
   ██║╚██╗██║██║██╔═██╗╚════╝██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
   ██║ ╚████║██║██║  ██╗     ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
   ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝[/bold yellow]
   [dim]coded by [bold cyan]denz[/bold cyan][/dim]
    """
    return Align.center(Text.from_markup(logo))

# ====================== FUNGSI CEK NIK ======================
def validate_nik(nik):
    """Validasi format NIK (16 digit angka)"""
    return bool(re.match(r'^\d{16}$', nik))

def format_nik(nik):
    """Format NIK dengan spasi untuk tampilan"""
    if len(nik) == 16:
        return f"{nik[:4]} {nik[4:8]} {nik[8:12]} {nik[12:16]}"
    return nik

def check_nik(nik: str):
    """Cek NIK menggunakan API"""
    console.print(f"\n[bold cyan]Mengecek NIK: [bold white]{format_nik(nik)}[/bold white][/bold cyan]")

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Menghubungi server...", total=None)
        try:
            response = requests.get(
                f"{NIK_API_URL}?nik={nik}",
                timeout=15
            )
            progress.update(task, completed=True)
        except requests.exceptions.Timeout:
            progress.update(task, completed=True)
            console.print("[bold red]Request timeout ke API.[/bold red]")
            return
        except requests.exceptions.ConnectionError:
            progress.update(task, completed=True)
            console.print("[bold red]Gagal terhubung ke server![/bold red]")
            return
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]Error: {e}[/bold red]")
            return

    if response.status_code != 200:
        console.print(f"[bold red]HTTP Error: {response.status_code}[/bold red]")
        return

    try:
        data = response.json()
    except:
        console.print("[bold red]Gagal parse JSON.[/bold red]")
        return

    status = data.get('status', False)
    if status != True:
        console.print(f"[bold red]Gagal: NIK tidak ditemukan[/bold red]")
        return

    result = data.get('result', {})

    # Tampilkan hasil dalam tabel seperti Ghost-Track
    table = Table(box=box.ROUNDED, border_style='cyan', title="[bold cyan]DATA NIK[/bold cyan]")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")

    # Data dari API
    fields = [
        ("NIK", result.get('nik', '-')),
        ("Jenis Kelamin", result.get('kelamin', '-')),
        ("Tanggal Lahir", result.get('lahir', '-')),
        ("Lahir Lengkap", result.get('lahir_lengkap', '-')),
        ("Provinsi", result.get('provinsi', {}).get('nama', '-')),
        ("Kota/Kabupaten", result.get('kotakab', {}).get('nama', '-')),
        ("Kecamatan", result.get('kecamatan', {}).get('nama', '-')),
        ("Kode Wilayah", result.get('kode_wilayah', '-')),
        ("Nomor Urut", result.get('nomor_urut', '-')),
    ]
    for label, value in fields:
        table.add_row(label, str(value))

    console.print(table)

    # Tampilkan data tambahan
    tambahan = result.get('tambahan', {})
    if tambahan:
        extra_table = Table(box=box.ROUNDED, border_style='green', title="[bold green]INFORMASI TAMBAHAN[/bold green]")
        extra_table.add_column("Field", style="bold green")
        extra_table.add_column("Value", style="white")
        
        extra_fields = [
            ("Pasaran", tambahan.get('pasaran', '-')),
            ("Usia", f"{tambahan.get('usia', '-')} tahun"),
            ("Kategori Usia", tambahan.get('kategori_usia', '-')),
            ("Ultah", tambahan.get('ultah', '-')),
            ("Zodiak", tambahan.get('zodiak', '-')),
        ]
        for label, value in extra_fields:
            extra_table.add_row(label, str(value))
        
        console.print(extra_table)

    # Tampilkan raw JSON
    raw_json = json.dumps(data, indent=2, ensure_ascii=False)
    syntax = Syntax(raw_json, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="[bold red]RAW JSON[/bold red]", border_style="red"))

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())

        # Menu sederhana seperti Ghost-Track
        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")
        
        menu_items = [
            ("01", "Cek NIK"),
            ("00", "Keluar")
        ]
        for no, label in menu_items:
            menu_table.add_row(no, label)
        
        console.print(Panel(menu_table, title="[bold blue]MENU[/bold blue]", border_style="blue"))

        pilihan = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]")
        
        if pilihan in ["1", "01"]:
            # Cek NIK
            nik_input = Prompt.ask("[bold cyan]Masukkan NIK (16 digit)[/bold cyan]")
            if not nik_input:
                console.print("[red]NIK tidak boleh kosong.[/red]")
                time.sleep(1)
                continue

            # Validasi: harus 16 digit angka
            if not validate_nik(nik_input):
                console.print("[red]NIK harus 16 digit angka![/red]")
                time.sleep(1)
                continue

            check_nik(nik_input)

            if not Confirm.ask("[bold cyan]Cek lagi?[/bold cyan]", default=True):
                console.print("[bold yellow]Keluar...[/bold yellow]")
                break
                
        elif pilihan in ["0", "00"]:
            console.print("\n[bold yellow]Keluar dari NIK Checker...[/bold yellow]")
            time.sleep(0.5)
            break
            
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(0.5)

def nik():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)