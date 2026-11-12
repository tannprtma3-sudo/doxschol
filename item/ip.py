import os
import sys
import json
import time
import webbrowser
import urllib.request
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]IP LOCATOR[/bold cyan] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold cyan]  ,_,\n'
        '    (o,o)    [bold white]IP ADDRESS LOCATOR[/bold white]\n'
        '    {`"\'}    [dim]Cek Informasi IP Address[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold cyan]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== FUNGSI CEK IP ======================
def cek_ip(ip_target=None):
    """Cek informasi IP dari ip-api.com"""
    if ip_target:
        url = f'http://ip-api.com/json/{ip_target}'
        console.print(f"\n[bold cyan]Mencari IP: [bold white]{ip_target}[/bold white][/bold cyan]")
    else:
        url = 'http://ip-api.com/json/'
        console.print("\n[bold cyan]Mencari IP sendiri...[/bold cyan]")
    
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Menghubungi server...", total=None)
        try:
            response = urllib.request.urlopen(url, timeout=10)
            data = json.load(response)
            progress.update(task, completed=True)
        except urllib.error.URLError:
            progress.update(task, completed=True)
            console.print("[bold red]Error! Periksa koneksi internet.[/bold red]")
            return
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]Error: {e}[/bold red]")
            return
    
    # Cek apakah data valid
    if data.get('status') == 'fail':
        console.print("[bold red]IP tidak valid atau tidak ditemukan.[/bold red]")
        return
    
    # ===== Tampilkan hasil dalam tabel =====
    # Info Dasar
    table_info = Table(box=box.ROUNDED, border_style='cyan', title="[bold cyan]INFORMASI IP[/bold cyan]")
    table_info.add_column("Field", style="bold cyan")
    table_info.add_column("Value", style="white")
    
    table_info.add_row("IP Address", data.get('query', '-'))
    table_info.add_row("ISP / Org", data.get('org', '-'))
    table_info.add_row("City", data.get('city', '-'))
    table_info.add_row("Region", data.get('regionName', '-'))
    table_info.add_row("Country", data.get('country', '-'))
    table_info.add_row("Postal Code", data.get('zip', '-'))
    table_info.add_row("Timezone", data.get('timezone', '-'))
    table_info.add_row("ISP", data.get('isp', '-'))
    
    console.print(table_info)
    
    # ===== Koordinat =====
    lat = data.get('lat')
    lon = data.get('lon')
    
    if lat and lon:
        maps_link = f'https://www.google.com/maps/place/{lat}+{lon}'
        
        table_coord = Table(box=box.ROUNDED, border_style='green', title="[bold green]📍 LOKASI[/bold green]")
        table_coord.add_column("Field", style="bold green")
        table_coord.add_column("Value", style="white")
        
        table_coord.add_row("Latitude", str(lat))
        table_coord.add_row("Longitude", str(lon))
        table_coord.add_row("Google Maps", f"[blue][link={maps_link}]{maps_link}[/link][/blue]")
        
        console.print(table_coord)
        
        # ===== Tanya buka browser =====
        if Confirm.ask("[bold cyan]Buka Google Maps di browser?[/bold cyan]", default=False):
            # Cek apakah di Termux
            if os.path.exists('/data/data/com.termux/files/usr/bin/bash'):
                os.system(f'am start -a android.intent.action.VIEW -d "{maps_link}" > /dev/null 2>&1')
            else:
                webbrowser.open(maps_link, new=0)
            console.print("[green]Membuka Google Maps...[/green]")
    else:
        console.print("[yellow]⚠️ Koordinat tidak tersedia.[/yellow]")
    
    # ===== JSON Mentah =====
    raw_json = json.dumps(data, indent=2, ensure_ascii=False)
    console.print(Panel(
        raw_json,
        title="[bold red]RAW JSON[/bold red]",
        border_style="red"
    ))

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())
        
        # Menu
        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")
        
        menu_table.add_row("01", "[bold white]Cek IP Sendiri[/bold white]")
        menu_table.add_row("02", "[bold white]Cek IP Target[/bold white]")
        menu_table.add_row("00", "[bold red]Keluar[/bold red]")
        
        console.print(Panel(menu_table, title="[bold blue]IP LOCATOR[/bold blue]", border_style="blue"))
        
        choice = Prompt.ask("[bold cyan]Pilih [01-02/00][/bold cyan]", choices=["01", "02", "00"])
        
        if choice == "00":
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break
        
        elif choice == "01":
            cek_ip()
            if not Confirm.ask("[bold cyan]Kembali ke menu?[/bold cyan]", default=True):
                console.print("[bold yellow]Keluar...[/bold yellow]")
                break
        
        elif choice == "02":
            target = Prompt.ask("[bold cyan]Masukkan IP Address atau Website (contoh: 8.8.8.8 atau google.com)[/bold cyan]")
            if not target:
                console.print("[red]Input tidak boleh kosong.[/red]")
                continue
            cek_ip(target)
            if not Confirm.ask("[bold cyan]Kembali ke menu?[/bold cyan]", default=True):
                console.print("[bold yellow]Keluar...[/bold yellow]")
                break

def ip():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)