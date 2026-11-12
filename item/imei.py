#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IMEI CHECKER v1.0 — Ghost-Track UI
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
API_URL = "http://98.142.250.139:3080/api/imei"

# ── Ghost-Track UI ──
def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]IMEI CHECKER[/bold white]\n'
        '    {`"\'}    [dim]Check IMEI device info[/dim]\n'
        '    -"-"-    [dim]coded by [bold blue]denz[/bold blue][/dim][/bold blue]\n    '
    )
    return Align.center(Text.from_markup(logo))

def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]IMEI CHECKER[/bold blue] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

# ── Utility ──
def validate_imei(imei):
    """Validasi IMEI (15 digit angka)."""
    imei = re.sub(r'[^0-9]', '', imei)
    if len(imei) == 15:
        return imei
    return None

def format_imei(imei):
    """Format IMEI menjadi 15 digit tanpa spasi."""
    return imei

# ── API Call ──
def check_imei(imei):
    """Cek IMEI via API."""
    try:
        params = {"imei": imei}
        resp = requests.get(API_URL, params=params, timeout=30)
        return resp.status_code, resp.text
    except Exception as e:
        return 0, str(e)

# ── Display ──
def display_result(status_code, raw_text, imei):
    console.print(f"[dim]Status Code: {status_code}[/dim]")
    console.print(f"[dim]IMEI: {imei}[/dim]")

    try:
        data = json.loads(raw_text)
    except:
        console.print("[red]Response bukan JSON yang valid.[/red]")
        console.print(f"[dim]Raw: {raw_text[:500]}[/dim]")
        return

    console.print(Panel(json.dumps(data, indent=2, ensure_ascii=False),
                       title="[bold red]RESPONSE[/bold red]",
                       border_style="red"))

    if isinstance(data, dict):
        # Coba ambil data device
        device_info = data.get("data", data)

        if not device_info:
            console.print("[yellow]⚠️ Tidak ada data ditemukan untuk IMEI ini.[/yellow]")
            return

        # Jika data langsung berisi field
        table = Table(box=box.ROUNDED, border_style='blue', title=f"[bold white]📱 DEVICE INFO[/bold white]\n[dim]IMEI: {imei}[/dim]")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")

        # Daftar field yang umum
        fields = [
            ("Brand", "brand"),
            ("Model", "model"),
            ("Device Name", "device_name"),
            ("Manufacturer", "manufacturer"),
            ("Model Name", "model_name"),
            ("Device Type", "device_type"),
            ("Hardware", "hardware"),
            ("Platform", "platform"),
            ("OS", "os"),
            ("Status", "status"),
            ("Message", "message"),
            ("TAC", "tac"),
            ("Serial", "serial"),
            ("Country", "country"),
            ("Network", "network"),
        ]

        found = False
        for label, key in fields:
            value = device_info.get(key)
            if value is not None and value != "":
                table.add_row(label, str(value))
                found = True

        if not found:
            # Tampilkan semua key-value
            for key, value in device_info.items():
                table.add_row(key.upper(), str(value))
            found = True

        console.print(table)

# ── Batch Check ──
def batch_check(imeis):
    results = []
    for imei in imeis:
        imei = imei.strip()
        if not imei:
            continue
        validated = validate_imei(imei)
        if not validated:
            results.append((imei, None, "Invalid IMEI"))
            continue
        status_code, raw = check_imei(validated)
        if status_code == 200:
            try:
                data = json.loads(raw)
                results.append((validated, data, None))
            except:
                results.append((validated, None, "Parse error"))
        else:
            results.append((validated, None, f"HTTP {status_code}"))
    return results

def display_batch_results(results):
    table = Table(box=box.ROUNDED, border_style='blue', title="[bold white]BATCH IMEI RESULTS[/bold white]")
    table.add_column("No", style="bold cyan", width=4)
    table.add_column("IMEI", style="white")
    table.add_column("Brand", style="white")
    table.add_column("Model", style="white")
    table.add_column("Status", style="green")

    for i, (imei, data, error) in enumerate(results, 1):
        if data:
            device = data.get("data", data)
            brand = device.get("brand", "-")
            model = device.get("model", "-")
            status = device.get("status", "OK")
            table.add_row(str(i), imei, brand[:15], model[:15], status)
        else:
            table.add_row(str(i), imei, "[red]❌[/red]", "", error or "Error")
    console.print(table)

    # Export batch results
    if Confirm.ask("[cyan]Export hasil batch ke file?[/cyan]", default=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"imei_batch_{timestamp}.json"
        try:
            os.makedirs("results", exist_ok=True)
            filepath = os.path.join("results", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ Data disimpan di: {filepath}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Gagal menyimpan: {e}[/red]")

# ── Menu ──
def menu_single():
    console.print("\n[bold yellow]Masukkan IMEI (15 digit)[/bold yellow]")
    imei_input = Prompt.ask("[bold blue]IMEI[/bold blue]").strip()
    if not imei_input:
        console.print("[red]IMEI tidak boleh kosong![/red]")
        return

    imei = validate_imei(imei_input)
    if not imei:
        console.print("[red]IMEI tidak valid! Harus 15 digit angka.[/red]")
        return

    with Progress(SpinnerColumn(), TextColumn("[bold blue]Mengecek IMEI...[/bold blue]"), console=console, transient=True) as progress:
        progress.add_task("", total=None)
        status_code, raw = check_imei(imei)

    if status_code == 0:
        console.print(f"[red]❌ Gagal terhubung ke API: {raw[:200]}[/red]")
        return

    if status_code != 200:
        console.print(f"[red]❌ HTTP Error {status_code}: {raw[:200]}[/red]")
        return

    display_result(status_code, raw, imei)

def menu_batch():
    console.print("\n[bold yellow]Masukkan daftar IMEI (pisahkan dengan koma atau spasi)[/bold yellow]")
    console.print("[dim]Maksimal 20 IMEI per batch[/dim]")
    inputs = Prompt.ask("[bold blue]Daftar IMEI[/bold blue]").strip()
    if not inputs:
        console.print("[red]Tidak ada IMEI yang dimasukkan![/red]")
        return

    imeis = re.split(r'[,\s]+', inputs)
    imeis = [validate_imei(imei) for imei in imeis if validate_imei(imei)]

    if not imeis:
        console.print("[red]Tidak ada IMEI yang valid![/red]")
        return

    if len(imeis) > 20:
        console.print("[yellow]⚠️ Maksimal 20 IMEI, hanya 20 pertama yang diproses.[/yellow]")
        imeis = imeis[:20]

    console.print(f"[dim]Memproses {len(imeis)} IMEI...[/dim]")

    with Progress(SpinnerColumn(), TextColumn("[bold blue]Mengecek IMEI...[/bold blue]"), console=console, transient=True) as progress:
        task = progress.add_task("", total=len(imeis))
        results = []
        for imei in imeis:
            status_code, raw = check_imei(imei)
            if status_code == 200:
                try:
                    data = json.loads(raw)
                    results.append((imei, data, None))
                except:
                    results.append((imei, None, "Parse error"))
            else:
                results.append((imei, None, f"HTTP {status_code}"))
            progress.update(task, advance=1)

    display_batch_results(results)

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
            ("01", "Check Single IMEI"),
            ("02", "Check Batch IMEI (max 20)"),
            ("00", "Exit")
        ]
        for no, label in menu_items:
            menu_table.add_row(no, label)

        console.print(Panel(menu_table, title="[bold blue]IMEI CHECKER[/bold blue]", border_style="blue"))

        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")

        if choice in ["0", "00"]:
            console.print("[yellow]Keluar...[/yellow]")
            break
        elif choice in ["1", "01"]:
            menu_single()
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        elif choice in ["2", "02"]:
            menu_batch()
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(0.5)

def imei2():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
