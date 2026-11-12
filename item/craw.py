import os
import sys
import re
import time
import json
import random
import socket
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
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

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]EMAIL CRAWL[/bold cyan] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold green]  ,_,\n'
        '    (o,o)    [bold white]EMAIL CRAWL[/bold white]\n'
        '    {`"\'}    [dim]Crawl Website & Extract Email[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold green]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== FUNGSI BANTUAN ======================
def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return random.choice(agents)

def valid_url(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        parsed = urlparse(url)
        host = parsed.netloc or parsed.path
        socket.gethostbyname(host)
        requests.get(url, timeout=3)
        return True
    except:
        return False

# ====================== CRAWL ENGINE ======================
def crawl_recursive(url, depth=2, visited=None):
    if visited is None:
        visited = set()
    if depth == 0 or url in visited:
        return ''
    visited.add(url)
    content = ''
    try:
        headers = {'User-Agent': random_user_agent()}
        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content += soup.get_text()
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if urlparse(full_url).netloc == urlparse(url).netloc:
                content += crawl_recursive(full_url, depth-1, visited)
    except:
        pass
    return content

def extract_emails(text):
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return list(set(re.findall(pattern, text)))

def email_stats(emails):
    domain_count = {}
    for email in emails:
        domain = email.split('@')[-1]
        domain_count[domain] = domain_count.get(domain, 0) + 1
    return domain_count

def simpan_hasil(emails):
    os.makedirs("results", exist_ok=True)
    path = "results/emails.txt"
    with open(path, "w") as f:
        for email in emails:
            f.write(email + "\n")
    return path

# ====================== FUNGSI UTAMA ======================
def crawl_url(url, depth):
    console.print(f"\n[bold cyan]Target: [bold white]{url}[/bold white]")
    console.print(f"[bold cyan]Kedalaman: [bold white]{depth}[/bold white]")

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='green'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Crawling & ekstraksi...", total=None)
        text = crawl_recursive(url, depth=depth)
        emails = extract_emails(text)
        progress.update(task, completed=True)

    console.print(f"[bold green]Ditemukan {len(emails)} email[/bold green]")

    if emails:
        # Tampilkan email dalam tabel
        email_table = Table(box=box.ROUNDED, border_style='cyan', title="[bold cyan]MAIL DITEMUKAN[/bold cyan]")
        email_table.add_column("No", style="bold cyan")
        email_table.add_column("Email", style="white")
        for i, email in enumerate(emails, 1):
            email_table.add_row(str(i), email)
        console.print(email_table)

        # Statistik per domain
        stats = email_stats(emails)
        stats_table = Table(box=box.ROUNDED, border_style='green', title="[bold green]STATISTIK PER DOMAIN[/bold green]")
        stats_table.add_column("Domain", style="bold green")
        stats_table.add_column("Jumlah", style="white")
        for domain, count in sorted(stats.items(), key=lambda x: -x[1]):
            stats_table.add_row(domain, str(count))
        console.print(stats_table)

        # Simpan
        file_path = simpan_hasil(emails)
        console.print(f"[green]Hasil disimpan ke: {file_path}[/green]")

        # Tampilkan JSON
        json_output = json.dumps({"emails": emails, "stats": stats}, indent=2, ensure_ascii=False)
        syntax = Syntax(json_output, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="[bold red]JSON OUTPUT[/bold red]", border_style="red"))

    else:
        console.print("[yellow]⚠️ Tidak ada email ditemukan.[/yellow]")

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())

        url = Prompt.ask("[bold cyan]Masukkan URL target (contoh: example.com)[/bold cyan]")
        if not url:
            console.print("[red]URL tidak boleh kosong.[/red]")
            continue

        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        console.print("[cyan]Memvalidasi URL...[/cyan]")
        if not valid_url(url):
            console.print("[red]URL tidak valid atau tidak dapat dijangkau.[/red]")
            continue

        while True:
            try:
                depth = int(Prompt.ask("[bold cyan]Masukkan kedalaman halaman (contoh: 2)[/bold cyan]", default="2"))
                if depth <= 0:
                    console.print("[red]Kedalaman harus lebih dari 0.[/red]")
                    continue
                break
            except ValueError:
                console.print("[red]Masukkan angka yang valid.[/red]")

        console.print("[yellow]⚠️ Semakin besar kedalaman, semakin lama prosesnya.[/yellow]")

        crawl_url(url, depth)

        if not Confirm.ask("[bold cyan]Crawling lagi?[/bold cyan]", default=True):
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

def craw():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
