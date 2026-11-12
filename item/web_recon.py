#!/usr/bin/env python3
import os
import sys
import socket
import requests
import json
import re
import concurrent.futures
import threading
import ssl
import http.client
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

# ====================== BANNER & HEADER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]GHOST-TRACK Ω[/bold cyan] [bold white]v5.1[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold red]  ,_,\n'
        '    (o,o)    [bold white]GHOST-TRACK Ω - WEB RECON[/bold white]\n'
        '    {`"\'}    [dim]ULTRA BRUTAL SHIT![/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan] & [bold red]petrus[/bold red][/dim][/bold red]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== RECON ENGINE ======================
def run_recon(target_input):
    console.print(f"\n[bold cyan]Locking → [bold white]{target_input}[/bold white][/bold cyan]")
    domain = target_input.replace("http://","").replace("https://","").split("/")[0]

    try:
        ip = socket.gethostbyname(domain)
        console.print(f"[green]IP → {ip}[/green]")
    except:
        console.print("[red]Domain ga ketemu bro![/red]")
        return

    found = {"subs":[], "leaks":[], "git":[], "env":[], "backup":[], "phpinfo":[], "emails":[], "keys":[], "ports":[], "tech":[], "headers":[]}
    lock = threading.Lock()

    # ==================== SUBDOMAIN BRUTEFORCE ====================
    def subdomain_bruteforce():
        console.print("\n[bold yellow][+] SUBDOMAIN BRUTEFORCE - GAS POL![/bold yellow]")
        subs_brute = [
            "admin", "api", "dev", "test", "staging", "beta", "vpn", "mail", "ftp", 
            "cpanel", "git", "jenkins", "kibana", "blog", "shop", "store", "app",
            "dashboard", "portal", "secure", "auth", "login", "adminpanel",
            "backend", "phpmyadmin", "mysql", "db", "database", "old", "new",
            "temp", "tmp", "backup", "archive", "legacy", "classic", "v1", "v2",
            "api1", "api2", "mobile", "m", "wap", "www1", "www2", "cdn", "static",
            "media", "images", "img", "video", "cdn1", "cdn2", "assets", "files",
            "download", "upload", "secure", "ssl", "webmail", "email", "smtp",
            "pop", "imap", "ns1", "ns2", "dns", "ssh", "ftp", "sftp", "crm", "erp"
        ]
        
        apis = [
            f"https://api.hackertarget.com/hostsearch/?q={domain}",
            f"https://crt.sh/?q=%.{domain}&output=json",
        ]
        
        for api in apis:
            try:
                r = requests.get(api, timeout=10)
                if r.status_code == 200:
                    if "hackertarget" in api:
                        for line in r.text.splitlines():
                            sub = line.split(",")[0].strip()
                            if sub and domain in sub:
                                found["subs"].append(sub)
                    elif "crt.sh" in api:
                        try:
                            data = json.loads(r.text)
                            for cert in data:
                                name = cert.get('name_value', '')
                                if domain in name:
                                    found["subs"].extend(name.splitlines())
                        except: pass
            except: pass
        
        def check_subdomain(sub):
            try:
                socket.gethostbyname(sub)
                with lock:
                    if sub not in found["subs"]:
                        found["subs"].append(sub)
                        console.print(f"[green][+] Subdomain → {sub}[/green]")
            except: pass
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as exe:
            futures = []
            for word in subs_brute:
                for prefix in ["", "api-", "dev-", "test-", "staging-", "admin-"]:
                    sub = f"{prefix}{word}.{domain}"
                    futures.append(exe.submit(check_subdomain, sub))
            for f in futures:
                f.result()

    # ==================== PORT SCANNING ====================
    def port_scan():
        console.print("\n[bold yellow][+] PORT SCANNING - NYARI BACKDOOR![/bold yellow]")
        common_ports = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 2082, 2083, 2086, 2087, 2095, 2096, 3306, 3389, 5432, 8080, 8443]
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    with lock:
                        found["ports"].append(port)
                        console.print(f"[green][+] Port {port} → OPEN[/green]")
                sock.close()
            except: pass
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as exe:
            exe.map(scan_port, common_ports)

    # ==================== TECHNOLOGY DETECTION ====================
    def tech_detection(host):
        try:
            ctx = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection(host, timeout=10, context=ctx)
            conn.request("GET", "/", headers={"User-Agent": "Mozilla/5.0"})
            r = conn.getresponse()
            headers = dict(r.getheaders())
            body = r.read(50000).decode(errors='ignore')
            
            tech_stack = []
            if "server" in headers:
                tech_stack.append(headers["server"])
                console.print(f"[cyan][+] Server → {headers['server']}[/cyan]")
            if "x-powered-by" in headers:
                tech_stack.append(headers["x-powered-by"])
                console.print(f"[cyan][+] Powered By → {headers['x-powered-by']}[/cyan]")
            if "wp-content" in body or "wordpress" in body:
                tech_stack.append("WordPress")
                console.print(f"[magenta][+] Tech → WordPress[/magenta]")
            elif "laravel" in body.lower():
                tech_stack.append("Laravel")
                console.print(f"[magenta][+] Tech → Laravel[/magenta]")
            elif "react" in body or "next" in body:
                tech_stack.append("React/Next.js")
                console.print(f"[magenta][+] Tech → React/Next.js[/magenta]")
            
            with lock:
                found["tech"].extend(tech_stack)
                found["headers"].append({host: headers})
        except: pass

    # ==================== REAL LEAK PATHS ====================
    real_paths = [
        "/.env", "/.env.bak", "/.env.prod", "/.env.local", "/.env.dev",
        "/.git/HEAD", "/.git/config", "/.git/logs/HEAD", "/.git/description",
        "/backup.sql", "/db_backup.sql", "/database.sql", "/dump.sql", "/backup.zip",
        "/phpinfo.php", "/info.php", "/test.php", "/debug.php", "/admin.php",
        "/admin/.env", "/laravel/.env", "/config/.env", "/app/.env",
        "/wp-config.php.bak", "/backup/wp-config.php", "/wp-config.php",
        "/robots.txt", "/sitemap.xml", "/web.config", "/.htaccess",
        "/config.json", "/config.js", "/settings.py", "/.dockerignore",
        "/docker-compose.yml", "/.travis.yml", "/.github/workflows",
        "/.aws/credentials", "/.npmrc", "/.yarnrc", "/composer.json",
        "/package.json", "/.bash_history", "/.ssh/id_rsa", "/.ssh/config"
    ]

    def deep_probe(host, path):
        try:
            ctx = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection(host, timeout=10, context=ctx)
            conn.request("GET", path, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            r = conn.getresponse()
            if r.status in [200,301,302,403]:
                data = r.read(1024000).decode(errors="ignore")
                url = f"https://{host}{path}"

                if ".env" in path and any(x in data for x in ["DB_PASSWORD", "APP_KEY", "JWT_SECRET", "API_KEY", "SECRET_KEY"]):
                    with lock:
                        found["env"].append(url)
                        console.print(f"[red][!] ENV LEAKED → {url}[/red]")
                        for line in data.splitlines()[:20]:
                            if "=" in line and not line.startswith("#"):
                                key, val = line.split("=",1)
                                if any(x in key.upper() for x in ["PASS","KEY","SECRET","TOKEN","API","AUTH"]):
                                    console.print(f"   [magenta]{key.strip()} = {val.strip()}[/magenta]")
                elif ".git" in path and ("ref:" in data or "[core]" in data):
                    with lock:
                        found["git"].append(url)
                        console.print(f"[red][!] GIT EXPOSED → {url}[/red]")
                        if "ref:" in data:
                            console.print(f"   [yellow]Branch → {data.split('ref:')[1].strip()[:60]}[/yellow]")
                elif any(x in path for x in ["sql","dump","backup","zip","tar"]):
                    if "INSERT INTO" in data or "CREATE TABLE" in data or "PK" in data[:100]:
                        with lock:
                            found["backup"].append(url)
                            console.print(f"[red][!] DATABASE DUMP → {url}[/red]")
                    elif len(data) > 1000:
                        with lock:
                            found["backup"].append(url)
                            console.print(f"[blue][!] LARGE FILE → {url} ({len(data)} bytes)[/blue]")
                elif "phpinfo" in path or "PHP Version" in data:
                    with lock:
                        found["phpinfo"].append(url)
                        console.print(f"[red][!] PHPINFO → {url}[/red]")
                elif any(x in path for x in ["config.json","settings.py","wp-config"]):
                    with lock:
                        found["leaks"].append(url)
                        console.print(f"[red][!] CONFIG FILE → {url}[/red]")

                emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", data)
                keys = re.findall(r"sk_live_[a-zA-Z0-9]{20,50}|[A-Za-z0-9+/]{40,}={0,2}", data)
                if emails:
                    with lock:
                        found["emails"].extend(emails)
                        for email in emails[:3]:
                            console.print(f"[cyan][+] Email → {email}[/cyan]")
                if keys:
                    with lock:
                        found["keys"].extend(keys)
                        for key in keys[:2]:
                            console.print(f"[magenta][!] Potential Key → {key[:50]}...[/magenta]")
        except: pass

    # ==================== WAYBACK MACHINE ====================
    def wayback_urls():
        console.print("\n[bold yellow][+] CHECKING WAYBACK MACHINE - ARCHIVE MODE![/bold yellow]")
        try:
            url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                urls = json.loads(r.text)
                for url in urls[1:20]:
                    console.print(f"[blue][+] Archive → {url[0][:80]}...[/blue]")
        except: pass

    # ==================== EKSEKUSI ====================
    console.print("\n[bold red]RECON DIMULAI - BRUTAL MODE ON![/bold red]")

    subdomain_bruteforce()
    port_scan()
    tech_detection(domain)
    wayback_urls()

    console.print("\n[bold red][+] LEAK HUNTING DIMULAI[/bold red]\n")

    all_hosts = list(set(found["subs"]))[:80]
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as exe:
        for host in all_hosts:
            for path in real_paths:
                exe.submit(deep_probe, host, path)
            exe.submit(tech_detection, host)

    # ==================== FINAL REPORT (FIXED) ====================
    console.print("\n[bold red]╔══════════════════════════════════════════════════════╗")
    console.print("[bold red]║                       RECON SELESAI                  ║")
    console.print("[bold red]╚══════════════════════════════════════════════════════╝[/bold red]")

    summary_table = Table(box=box.ROUNDED, border_style='cyan')
    summary_table.add_column("Item", style="bold cyan")
    summary_table.add_column("Count", style="bold white")
    summary_table.add_column("Detail", style="white")

    summary_table.add_row("Subdomains", str(len(set(found['subs']))), ", ".join(list(set(found['subs']))[:5]) + ("..." if len(found['subs'])>5 else ""))
    summary_table.add_row("Open Ports", str(len(found['ports'])), str(found['ports']))
    summary_table.add_row("ENV Leaked", str(len(found['env'])), "\n".join(found['env'][:3]))
    summary_table.add_row("Git Exposed", str(len(found['git'])), "\n".join(found['git'][:3]))
    summary_table.add_row("SQL Dump", str(len(found['backup'])), "\n".join(found['backup'][:3]))
    summary_table.add_row("PHPInfo", str(len(found['phpinfo'])), "\n".join(found['phpinfo'][:3]))
    summary_table.add_row("Emails Found", str(len(set(found['emails']))), "\n".join(list(set(found['emails']))[:3]))
    summary_table.add_row("API Keys", str(len(set(found['keys']))), "\n".join(list(set(found['keys']))[:3]))
    summary_table.add_row("Tech Stack", str(len(set(found['tech']))), ", ".join(list(set(found['tech']))[:5]))

    console.print(summary_table)

    if found["env"] or found["git"] or found["backup"]:
        console.print("\n[bold magenta]LANGSUNG GAS BRO![/bold magenta]")
        for leak in found["env"][:3]:
            console.print(f"   [red]ENV → {leak}[/red]")
        for leak in found["git"][:3]:
            console.print(f"   [red]GIT → {leak}[/red]")
        for leak in found["backup"][:3]:
            console.print(f"   [red]SQL → {leak}[/red]")
        console.print("\n[bold yellow]d3nz — recon,[/bold yellow]")

    console.print("[bold red]3113 OUT ULTRA BRUTAL MODE![/bold red]\n")

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())
        
        target = Prompt.ask("[bold cyan]Target (contoh: tesla.com)[/bold cyan]")
        if not target:
            console.print("[red]Target tidak boleh kosong.[/red]")
            continue
        
        run_recon(target)
        
        if not Confirm.ask("[bold cyan]Lanjut ke target lain?[/bold cyan]", default=True):
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

def recon():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
