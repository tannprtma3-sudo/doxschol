# Nusatenggara Timur Development
# Coded By denz!

import os
import os
import sys
import time
import requests
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
        '[bold cyan]CEK PTK GTK[/bold cyan] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold green]  ,_,\n'
        '    (o,o)    [bold white]CEK PTK GTK TOOL[/bold white]\n'
        '    {`"\'}    [dim]Cek Data Guru Indonesia[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold green]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== FUNGSI CEK PTK ======================
def cek_ptk(keyword):
    """Cari data PTK dari GTK Kemdikbud"""
    console.print(f"\n[bold cyan]Mencari data untuk: [bold white]{keyword}[/bold white][/bold cyan]")

    url = f"https://gtk.belajar.kemendikdasmen.go.id/akun/ptk-solr?keyword={keyword}"
    headers = {"User-Agent": "Mozilla/5.0 (Python PTK Checker)"}

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Menghubungi server GTK...", total=None)
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json()
            progress.update(task, completed=True)
        except requests.exceptions.Timeout:
            progress.update(task, completed=True)
            console.print("[bold red]Timeout ke server GTK.[/bold red]")
            return
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]Error: {e}[/bold red]")
            return

    if not data or "data" not in data or not data["data"]:
        console.print("[bold red]Data PTK tidak ditemukan.[/bold red]")
        return

    ptk = data["data"][0]
    sekolah = ptk.get("sekolah", {})
    prov = sekolah.get("m_propinsi", {}).get("keterangan", "-")
    kota = sekolah.get("m_kota", {}).get("keterangan", "-")

    # Tampilkan hasil dalam tabel
    result_table = Table(box=box.ROUNDED, border_style='green', title="[bold green]DATA PTK GTK[/bold green]")
    result_table.add_column("Field", style="bold cyan")
    result_table.add_column("Value", style="white")

    result_table.add_row("Nama", ptk.get('nama', '-'))
    result_table.add_row("NUPTK", ptk.get('nuptk', '-'))
    result_table.add_row("NIK Masked", ptk.get('nik_masked', '-'))
    result_table.add_row("Sekolah", sekolah.get('nama', '-'))
    result_table.add_row("NPSN", sekolah.get('npsn', '-'))
    result_table.add_row("Provinsi", prov)
    result_table.add_row("Kab/Kota", kota)

    status = "Aktif" if ptk.get("status_ptk", {}).get("aktif") else "Tidak Aktif"
    status_color = "green" if "Aktif" in status else "red"
    result_table.add_row("Status PTK", f"[{status_color}]{status}[/{status_color}]")
    result_table.add_row("Update", ptk.get('tanggal_perbaharui', '-'))

    console.print(result_table)

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())

        keyword = Prompt.ask("[bold cyan]Masukkan Nama / NIK / NUPTK[/bold cyan]")
        if not keyword:
            console.print("[red]Input tidak boleh kosong.[/red]")
            continue

        cek_ptk(keyword)

        if not Confirm.ask("[bold cyan]Cek lagi?[/bold cyan]", default=True):
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

def guru():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
