import os
import sys
import time
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]TELEGRAM BOT MGR[/bold cyan] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold cyan]  ,_,\n'
        '    (o,o)    [bold white]TELEGRAM BOT MANAGER[/bold white]\n'
        '    {`"\'}    [dim]Spam, Ganti Nama, Ganti Foto[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold cyan]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== FUNGSI TELEGRAM API ======================
def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.status_code == 200
    except:
        return False

def send_photo(token, chat_id, photo_url):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    params = {"chat_id": chat_id, "photo": photo_url}
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.status_code == 200
    except:
        return False

def set_bot_name(token, new_name):
    url = f"https://api.telegram.org/bot{token}/setMyName"
    params = {"name": new_name}
    try:
        resp = requests.post(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("ok", False)
        return False
    except:
        return False

def set_bot_photo(token, photo_path):
    url = f"https://api.telegram.org/bot{token}/setMyPhoto"
    if not os.path.exists(photo_path):
        return False, "File tidak ditemukan."
    try:
        files = {"photo": open(photo_path, "rb")}
        resp = requests.post(url, files=files, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("ok", False), data.get("description", "")
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)

# ====================== MENU SPAM ======================
def spam_teks():
    token = Prompt.ask("[bold cyan]Token Bot[/bold cyan]")
    chat_id = Prompt.ask("[bold cyan]Chat ID[/bold cyan]")
    text = Prompt.ask("[bold cyan]Teks[/bold cyan]")
    jumlah = IntPrompt.ask("[bold cyan]Jumlah spam[/bold cyan]", default=5)

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='green'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Mengirim spam teks...", total=jumlah)
        success = 0
        for i in range(jumlah):
            if send_message(token, chat_id, text):
                success += 1
            progress.advance(task)
    console.print(f"[green]Berhasil {success} dari {jumlah} pesan.[/green]")

def spam_gambar():
    token = Prompt.ask("[bold cyan]Token Bot[/bold cyan]")
    chat_id = Prompt.ask("[bold cyan]Chat ID[/bold cyan]")
    photo_url = Prompt.ask("[bold cyan]URL Gambar[/bold cyan]")
    jumlah = IntPrompt.ask("[bold cyan]Jumlah spam[/bold cyan]", default=5)

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='green'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Mengirim spam gambar...", total=jumlah)
        success = 0
        for i in range(jumlah):
            if send_photo(token, chat_id, photo_url):
                success += 1
            progress.advance(task)
    console.print(f"[green]Berhasil {success} dari {jumlah} gambar.[/green]")

def spam_teks_gambar():
    token = Prompt.ask("[bold cyan]Token Bot[/bold cyan]")
    chat_id = Prompt.ask("[bold cyan]Chat ID[/bold cyan]")
    text = Prompt.ask("[bold cyan]Teks[/bold cyan]")
    photo_url = Prompt.ask("[bold cyan]URL Gambar[/bold cyan]")
    jumlah = IntPrompt.ask("[bold cyan]Jumlah spam[/bold cyan]", default=5)

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='green'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Mengirim spam teks+gambar...", total=jumlah)
        success = 0
        for i in range(jumlah):
            ok1 = send_message(token, chat_id, text)
            ok2 = send_photo(token, chat_id, photo_url)
            if ok1 and ok2:
                success += 1
            progress.advance(task)
    console.print(f"[green]Berhasil {success} dari {jumlah} kombinasi.[/green]")

# ====================== MENU HACK BOT ======================
def ganti_nama_bot():
    token = Prompt.ask("[bold cyan]Token Bot[/bold cyan]")
    new_name = Prompt.ask("[bold cyan]Nama Baru Bot[/bold cyan]")
    if not new_name:
        console.print("[red]Nama tidak boleh kosong.[/red]")
        return

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Mengganti nama bot...", total=None)
        ok = set_bot_name(token, new_name)
        progress.update(progress.tasks[0].id, completed=True)
    if ok:
        console.print(f"[green]Nama bot berhasil diubah menjadi: {new_name}[/green]")
    else:
        console.print("[red]Gagal mengganti nama. Cek token dan koneksi.[/red]")

def ganti_foto_bot():
    token = Prompt.ask("[bold cyan]Token Bot[/bold cyan]")
    photo_path = Prompt.ask("[bold cyan]Path foto lokal (contoh: /sdcard/foto.jpg)[/bold cyan]")
    if not photo_path:
        console.print("[red]Path tidak boleh kosong.[/red]")
        return

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Mengganti foto bot...", total=None)
        ok, msg = set_bot_photo(token, photo_path)
        progress.update(progress.tasks[0].id, completed=True)
    if ok:
        console.print(f"[green]Foto bot berhasil diubah![/green]")
    else:
        console.print(f"[red]Gagal: {msg}[/red]")

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")
        menu_table.add_row("01", "[bold white]Spam Teks[/bold white]")
        menu_table.add_row("02", "[bold white]Spam Gambar[/bold white]")
        menu_table.add_row("03", "[bold white]Spam Teks + Gambar[/bold white]")
        menu_table.add_section()
        menu_table.add_row("04", "[bold white]Ganti Nama Bot[/bold white]")
        menu_table.add_row("05", "[bold white]Ganti Foto Bot[/bold white]")
        menu_table.add_row("00", "[bold red]Keluar[/bold red]")
        console.print(Panel(menu_table, title="[bold blue]TELEGRAM BOT MANAGER[/bold blue]", border_style="blue"))

        choice = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]", choices=["01","02","03","04","05","00"])

        if choice == "00":
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break
        elif choice == "01":
            spam_teks()
        elif choice == "02":
            spam_gambar()
        elif choice == "03":
            spam_teks_gambar()
        elif choice == "04":
            ganti_nama_bot()
        elif choice == "05":
            ganti_foto_bot()
        else:
            console.print("[red]Pilihan tidak valid.[/red]")

        if not Confirm.ask("[bold cyan]Kembali ke menu?[/bold cyan]", default=True):
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

def tele():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
