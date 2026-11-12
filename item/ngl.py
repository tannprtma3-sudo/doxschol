import os
import sys
import time
import re
import json
import socket
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

# ── Ghost-Track UI (Blue/Cyan) ──
def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]DIRECTORY SCANNER[/bold white]\n'
        '    {`"\'}    [dim]Find hidden directories & files[/dim]\n'
        '    -"-"-    [dim]coded by [bold blue]denz[/bold blue][/dim][/bold blue]\n    '
    )
    return Align.center(Text.from_markup(logo))

def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]DIRECTORY SCANNER[/bold blue] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

# ── Utility ──
def get_wordlist(mode='fast'):
    if mode == 'fast':
        return [
            "admin", "login", "dashboard", "config", "uploads", "images",
            "js", "css", "api", "backup", "db.php", "wp-admin",
            ".env", "robots.txt", "test", "phpinfo.php", "wp-content", "index.php"
        ]
    else:
        return [
            "admin", "login", "dashboard", "panel", "control", "manager", "webadmin", "administrator",
            "backend", "cp", "cpanel", "adminpanel", "sysadmin", "system", "management",
            "config", "configuration", "settings", "setup", "install", "update", "upgrade",
            "backup", "backups", "bak", "old", "temp", "tmp", "cache", "log", "logs",
            "uploads", "images", "img", "pictures", "photos", "media", "files", "downloads",
            "assets", "static", "public", "shared", "resources", "storage", "data", "database",
            "js", "javascript", "css", "styles", "fonts", "scripts", "include", "includes",
            "lib", "library", "vendor", "modules", "components", "plugins", "themes", "templates",
            "index.php", "index.html", "main.php", "home.php", "config.php", "config.inc.php",
            "db.php", "database.php", "settings.php", "wp-config.php", ".env", ".htaccess",
            "robots.txt", "sitemap.xml", "crossdomain.xml", "phpinfo.php", "test.php",
            "api", "rest", "json", "xml", "soap", "graphql", "oauth", "auth", "authentication",
            "user", "users", "account", "accounts", "profile", "profiles", "member", "members",
            "wp", "wordpress", "wp-admin", "wp-content", "wp-includes", "wp-login.php",
            "joomla", "administrator", "drupal", "magento", "phpmyadmin", "phpMyAdmin",
            "error.log", "access.log", "debug.log", "backup.zip", "backup.sql", "backup.tar",
            "backup.rar", "backup.db", "dump.sql", "backup_2023.zip", "old.zip", "archive.zip",
            "test", "testing", "dev", "development", "stage", "staging", "prod", "production",
            "demo", "sandbox", "secure", "private", "hidden", "secret", "confidential", "internal"
        ]

def valid_url(url):
    try:
        if not url.startswith(('http://', 'https://')):
            return False
        # Extract host
        host = url.split('/')[2] if '://' in url else url.split('/')[0]
        socket.gethostbyname(host)
        resp = requests.get(url, timeout=5)
        return resp.status_code < 500
    except:
        return False

def save_results(results, filename=None):
    os.makedirs("results", exist_ok=True)
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"results/dirb_scan_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"DIRECTORY SCAN RESULTS\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("-" * 50 + "\n")
        for path, status, size in results:
            f.write(f"{path} - Status: {status} - Size: {size} bytes\n")
    return filename

# ── Scanner ──
def dirb_scan(url, mode='fast'):
    wordlist = get_wordlist(mode)
    results = []

    with Progress(SpinnerColumn(), TextColumn("[bold blue]Scanning...[/bold blue]"), console=console, transient=True) as progress:
        task = progress.add_task(f"Checking {len(wordlist)} paths...", total=len(wordlist))
        for word in wordlist:
            target = url.rstrip("/") + "/" + word
            try:
                resp = requests.get(target, timeout=8)
                if resp.status_code in [200, 301, 302, 403, 401]:
                    results.append((target, resp.status_code, len(resp.content)))
            except:
                pass
            progress.update(task, advance=1)
            time.sleep(0.05 if mode == 'fast' else 0.1)

    return results

# ── Display ──
def display_results(results, url):
    if not results:
        console.print("[yellow]⚠️ Tidak ada direktori atau file tersembunyi ditemukan.[/yellow]")
        return

    table = Table(box=box.ROUNDED, border_style='blue', title=f"[bold white]SCAN RESULTS for {url}[/bold white]")
    table.add_column("No", style="bold cyan", width=4)
    table.add_column("Path", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Size", style="cyan")

    for i, (path, status, size) in enumerate(results, 1):
        status_str = str(status)
        if status == 200:
            status_str = f"[green]{status}[/green]"
        elif status in (301, 302):
            status_str = f"[blue]{status}[/blue]"
        elif status in (403, 401):
            status_str = f"[red]{status}[/red]"
        table.add_row(str(i), path, status_str, f"{size} bytes")
    console.print(table)

    # Save results
    filename = save_results(results)
    console.print(f"[green]Hasil disimpan di: {filename}[/green]")

# ── Menu ──
def menu_scan():
    console.print("\n[bold yellow]Masukkan URL target[/bold yellow]")
    console.print("[dim]Contoh: http://example.com atau https://target.com[/dim]")
    url = Prompt.ask("[bold blue]URL[/bold blue]").strip()
    if not url:
        console.print("[red]URL tidak boleh kosong![/red]")
        return

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    with Progress(SpinnerColumn(), TextColumn("[bold blue]Memvalidasi URL...[/bold blue]"), console=console, transient=True) as progress:
        progress.add_task("", total=None)
        time.sleep(0.5)
        if not valid_url(url):
            console.print("[red]URL tidak valid atau tidak dapat dijangkau.[/red]")
            return

    console.print("[green]URL valid.[/green]")

    mode = Prompt.ask("[bold blue]Pilih mode scan (fast/full)[/bold blue]", default="fast")
    if mode.lower() not in ['fast', 'full']:
        console.print("[yellow]Mode tidak dikenal, menggunakan 'fast'.[/yellow]")
        mode = 'fast'

    results = dirb_scan(url, mode)
    display_results(results, url)

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
            ("01", "Scan Directory"),
            ("00", "Exit")
        ]
        for no, label in menu_items:
            menu_table.add_row(no, label)

        console.print(Panel(menu_table, title="[bold blue]DIRECTORY SCANNER[/bold blue]", border_style="blue"))

        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")

        if choice in ["0", "00"]:
            console.print("[yellow]Keluar...[/yellow]")
            break
        elif choice in ["1", "01"]:
            menu_scan()
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(0.5)

def ngl_run():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
