# denz
import os
import sys
import json
import time
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.syntax import Syntax

console = Console()

# ====================== KONFIGURASI ======================
API_URL = "https://api.cellmapper.net/v6/getTowerInformation"

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]CELLMAPPER BTS[/bold cyan] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold green]  ,_,\n'
        '    (o,o)    [bold white]BTS / TOWER LOOKUP[/bold white]\n'
        '    {`"\'}    [dim]Cari Informasi Tower Seluler[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold green]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== FUNGSI BANTUAN ======================
def format_timestamp(ts):
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime("%d-%m-%Y %H:%M:%S UTC")
    except:
        return "Tidak diketahui"

def format_list(data):
    if isinstance(data, list) and data:
        return ", ".join(str(x) for x in data)
    return "-"

def status_text(v):
    if v is True:
        return "[green]Ya[/green]"
    elif v is False:
        return "[red]Tidak[/red]"
    return "-"

def status_available(v):
    if v is True:
        return "[green]Tersedia[/green]"
    elif v is False:
        return "[red]Tidak[/red]"
    return "-"

def buat_link_maps(lat, lon):
    if lat in [None, "-", ""] or lon in [None, "-", ""]:
        return "Tidak tersedia"
    return f"https://www.google.com/maps?q={lat},{lon}"

def simpan_json(site_id, region_id, data):
    folder = "hasil_bts"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"site_{site_id}_region_{region_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return file_path

# ====================== AMBIL DATA API ======================
def ambil_data_api(mcc, mnc, offset):
    url = f"{API_URL}?MCC={mcc}&MNC={mnc}&offset={offset}"
    
    cmd = [
        "curl",
        "-s",
        "--max-time", "35",
        "-H", "Accept: application/json",
        url
    ]
    
    try:
        hasil = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        text = hasil.decode("utf-8", errors="ignore").strip()
        
        if not text:
            return None
        
        try:
            return json.loads(text)
        except:
            return None
            
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None

# ====================== TAMPILKAN HASIL ======================
def tampilkan_hasil(tower, mcc, mnc):
    lat = tower.get("latitude")
    lon = tower.get("longitude")
    maps = buat_link_maps(lat, lon)
    
    # ===== INFO DASAR =====
    table_dasar = Table(box=box.ROUNDED, border_style='cyan', title="[bold cyan]INFORMASI DASAR[/bold cyan]")
    table_dasar.add_column("Field", style="bold cyan")
    table_dasar.add_column("Value", style="white")
    
    table_dasar.add_row("Site ID", str(tower.get('siteID', '-')))
    table_dasar.add_row("Region ID", str(tower.get('regionID', '-')))
    table_dasar.add_row("MCC", str(mcc))
    table_dasar.add_row("MNC", str(mnc))
    table_dasar.add_row("Jenis Jaringan (RAT)", str(tower.get('RAT', '-')))
    table_dasar.add_row("Sub Jenis Jaringan", str(tower.get('RATSubType', '-')))
    table_dasar.add_row("Tower Terlihat", status_text(tower.get('visible')))
    table_dasar.add_row("Tower Mover ID", str(tower.get('towerMover', '-')))
    
    console.print(table_dasar)
    
    # ===== KOORDINAT =====
    table_koordinat = Table(box=box.ROUNDED, border_style='green', title="[bold green]📍 KOORDINAT & LOKASI[/bold green]")
    table_koordinat.add_column("Field", style="bold green")
    table_koordinat.add_column("Value", style="white")
    
    table_koordinat.add_row("Latitude", str(lat) if lat else "-")
    table_koordinat.add_row("Longitude", str(lon) if lon else "-")
    table_koordinat.add_row("Google Maps", f"[blue][link={maps}]{maps}[/link][/blue]" if maps != "Tidak tersedia" else maps)
    
    console.print(table_koordinat)
    
    # ===== FREKUENSI =====
    table_frekuensi = Table(box=box.ROUNDED, border_style='yellow', title="[bold yellow]FREKUENSI & JARINGAN[/bold yellow]")
    table_frekuensi.add_column("Field", style="bold yellow")
    table_frekuensi.add_column("Value", style="white")
    
    table_frekuensi.add_row("Channel / EARFCN", format_list(tower.get('channels')))
    table_frekuensi.add_row("Bandwidth", format_list(tower.get('bandwidths')))
    table_frekuensi.add_row("Nomor Band", format_list(tower.get('bandNumbers')))
    table_frekuensi.add_row("Estimasi Data Band", format_list(tower.get('estimatedBandData')))
    table_frekuensi.add_row("Data Bandwidth", status_available(tower.get('bandwidthData')))
    table_frekuensi.add_row("Data Frekuensi", status_available(tower.get('frequencyData')))
    
    console.print(table_frekuensi)
    
    # ===== WAKTU =====
    table_waktu = Table(box=box.ROUNDED, border_style='magenta', title="[bold magenta]WAKTU TERDETEKSI[/bold magenta]")
    table_waktu.add_column("Field", style="bold magenta")
    table_waktu.add_column("Value", style="white")
    
    table_waktu.add_row("Pertama Kali", format_timestamp(tower.get('firstseendate')))
    table_waktu.add_row("Terakhir Kali", format_timestamp(tower.get('lastseendate')))
    
    console.print(table_waktu)
    
    # ===== DATA TAMBAHAN =====
    console.print("\n[bold cyan]DATA TAMBAHAN[/bold cyan]")
    
    cells = tower.get('cells', {})
    if cells:
        cells_json = json.dumps(cells, indent=2, ensure_ascii=False)
        syntax_cells = Syntax(cells_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax_cells, title="[bold cyan]Cells[/bold cyan]", border_style="cyan"))
    
    tower_attrs = tower.get('towerAttributes', {})
    if tower_attrs:
        attrs_json = json.dumps(tower_attrs, indent=2, ensure_ascii=False)
        syntax_attrs = Syntax(attrs_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax_attrs, title="[bold cyan]Tower Attributes[/bold cyan]", border_style="cyan"))
    
    # ===== JSON MENTAH =====
    raw_json = json.dumps(tower, indent=2, ensure_ascii=False)
    syntax_raw = Syntax(raw_json, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax_raw, title="[bold red]RAW JSON[/bold red]", border_style="red"))

# ====================== PROSES PENCARIAN ======================
def cari_tower(site_id, region_id, mcc, mnc):
    offset = 0
    total_dicek = 0
    
    console.print(f"\n[bold cyan]Target Site ID: [bold white]{site_id}[/bold white]")
    console.print(f"[bold cyan]Target Region ID: [bold white]{region_id}[/bold white]")
    console.print(f"[bold cyan]MCC: [bold white]{mcc}[/bold white] | MNC: [bold white]{mnc}[/bold white]")
    
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Memindai data tower...", total=None)
        
        while True:
            progress.update(task, description=f"[cyan]Memindai offset {offset}...")
            data = ambil_data_api(mcc, mnc, offset)
            
            if not data:
                progress.update(task, completed=True)
                console.print("[bold red]Gagal mendapatkan data dari API.[/bold red]")
                return
            
            towers = data.get("responseData", [])
            if not isinstance(towers, list):
                progress.update(task, completed=True)
                console.print("[bold red]Format data dari API tidak valid.[/bold red]")
                return
            
            if not towers:
                if offset == 0:
                    progress.update(task, completed=True)
                    console.print("[bold yellow]⚠️ Tidak ada data tower.[/bold yellow]")
                    return
            
            for tower in towers:
                if not isinstance(tower, dict):
                    continue
                
                total_dicek += 1
                tower_site = str(tower.get("siteID", "")).strip()
                tower_region = str(tower.get("regionID", "")).strip()
                
                if tower_site == str(site_id).strip() and tower_region == str(region_id).strip():
                    progress.update(task, completed=True)
                    console.print(f"\n[bold green]Tower ditemukan setelah memeriksa {total_dicek} data.[/bold green]")
                    
                    tampilkan_hasil(tower, mcc, mnc)
                    
                    file_hasil = simpan_json(site_id, region_id, tower)
                    console.print(f"[green]Data disimpan ke: {file_hasil}[/green]")
                    return
            
            if not data.get("hasMore", False):
                break
            
            offset += 100
            time.sleep(0.5)
        
        progress.update(task, completed=True)
    
    console.print("\n[bold red]Tower tidak ditemukan.[/bold red]")
    console.print(f"[dim]Total data yang diperiksa: {total_dicek}[/dim]")

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())
        
        # Input data
        console.print("\n[bold cyan]MASUKKAN DATA TOWER[/bold cyan]")
        site_id = Prompt.ask("[bold cyan]Site ID[/bold cyan]")
        if not site_id:
            console.print("[red]Site ID tidak boleh kosong.[/red]")
            continue
        
        region_id = Prompt.ask("[bold cyan]Region ID[/bold cyan]")
        if not region_id:
            console.print("[red]Region ID tidak boleh kosong.[/red]")
            continue
        
        mcc = Prompt.ask("[bold cyan]MCC[/bold cyan]", default="510")
        mnc = Prompt.ask("[bold cyan]MNC[/bold cyan]", default="1")
        
        cari_tower(site_id, region_id, mcc, mnc)
        
        if not Confirm.ask("[bold cyan]Cari lagi?[/bold cyan]", default=True):
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

def cell():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
