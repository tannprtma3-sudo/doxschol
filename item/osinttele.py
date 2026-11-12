import os
import sys
import time
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient, functions, types
from telethon.errors import SessionPasswordNeededError, FloodWaitError
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

# ====================== KONFIGURASI ======================
API_ID = 38762824
API_HASH = "3f5c1b1d56fc37b78ae2d29e9c92fe8b"
SESSION_FILE = "tg_osint.session"

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]TELEGRAM OSINT[/bold cyan] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold red]  ,_,\n'
        '    (o,o)    [bold white]TELEGRAM OSINT[/bold white]\n'
        '    {`"\'}    [dim]hanya manusia biasa makan nasi v;[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold red]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== TELEGRAM CLIENT ======================
client = None

async def init_client():
    global client
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    console.print("[green]Connected to Telegram![/green]")
    me = await client.get_me()
    console.print(f"[cyan]Logged in as: {me.first_name} (@{me.username})[/cyan]")
    return client

async def get_user_info(identifier):
    """Cari user berdasarkan username, phone, atau ID"""
    try:
        entity = await client.get_entity(identifier)
        return entity, None
    except ValueError as e:
        return None, str(e)
    except FloodWaitError as e:
        return None, f"Flood wait: {e.seconds} detik"
    except Exception as e:
        return None, str(e)

async def get_full_user(user):
    """Dapatkan data lengkap user (bio, common groups, dll)"""
    try:
        full = await client(functions.users.GetFullUserRequest(user))
        return full, None
    except Exception as e:
        return None, str(e)

async def download_photo(user, filename=None):
    """Download foto profil user"""
    try:
        if not user.photo:
            return None, "Tidak ada foto profil"
        if filename is None:
            filename = f"profile_{user.id}.jpg"
        path = await client.download_profile_photo(user, file=filename)
        return path, None
    except Exception as e:
        return None, str(e)

# ====================== TAMPILKAN HASIL ======================
def display_user_info(user, full=None):
    """Tampilkan data user dalam tabel"""
    table = Table(box=box.ROUNDED, border_style='cyan', title="[bold green]DATA USER TELEGRAM[/bold green]")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")
    
    fields = [
        ("ID", user.id),
        ("Username", f"@{user.username}" if user.username else "-"),
        ("First Name", user.first_name or "-"),
        ("Last Name", user.last_name or "-"),
        ("Phone", user.phone if hasattr(user, 'phone') else "-"),
        ("Is Bot", "Ya" if user.bot else "Tidak"),
        ("Is Verified", "Ya" if user.verified else "Tidak"),
        ("Is Scam", "Ya" if user.scam else "Tidak"),
        ("Is Fake", "Ya" if user.fake else "Tidak"),
        ("Restricted", "Ya" if user.restricted else "Tidak"),
        ("Access Hash", user.access_hash if hasattr(user, 'access_hash') else "-"),
    ]
    for label, value in fields:
        if value and value != "-":
            table.add_row(label, str(value))
    
    # Bio
    if full and full.full_user:
        bio = full.full_user.about or "-"
        table.add_row("Bio", bio[:200] + ("..." if len(bio) > 200 else ""))
        
        # Common groups count (tampilkan saja jumlahnya)
        if hasattr(full.full_user, 'common_chats_count'):
            table.add_row("Common Groups Count", str(full.full_user.common_chats_count))
    
    console.print(table)

# ====================== ASYNC MAIN ======================
async def async_main():
    global client
    
    console.print(get_header())
    console.print(show_banner())
    
    # Disclaimer
    console.print("\n[bold yellow]DISCLAIMER:[/bold yellow]")
    console.print("[dim]Tools ini hanya untuk EDUKASI dan TESTING pada akun sendiri.[/dim]")
    console.print("[dim]Dilarang untuk doxing / stalking / melanggar privasi orang lain![/dim]")
    console.print("[dim]Gunakan dengan bijak dan bertanggung jawab![/dim]")
    
    if not Confirm.ask("[bold cyan]Lanjutkan?[/bold cyan]", default=False):
        console.print("[dim]Dibatalkan.[/dim]")
        return
    
    # Init client
    await init_client()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())
        
        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")
        menu_table.add_row("01", "[bold white]Cari Username[/bold white]")
        menu_table.add_row("02", "[bold white]Cari Nomor Telepon[/bold white]")
        menu_table.add_row("03", "[bold white]Cari User ID[/bold white]")
        menu_table.add_row("04", "[bold white]Download Foto Profil[/bold white]")
        menu_table.add_row("00", "[bold red]Keluar[/bold red]")
        
        console.print(Panel(menu_table, title="[bold blue]TELEGRAM OSINT[/bold blue]", border_style="blue"))
        
        choice = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]", choices=["01","02","03","04","00"])
        
        if choice == "00":
            console.print("[bold yellow]Keluar...[/bold yellow]")
            await client.disconnect()
            break
        
        elif choice == "01":
            username = Prompt.ask("[bold cyan]Masukkan username (tanpa @)[/bold cyan]")
            if not username:
                console.print("[red]Username tidak boleh kosong.[/red]")
                input("\n[dim]Tekan Enter...[/dim]")
                continue
            
            with Progress(SpinnerColumn(), TextColumn("[cyan]Mencari user...[/cyan]"), console=console) as p:
                p.add_task("", total=None)
                user, err = await get_user_info(f"@{username}")
            
            if user:
                full, _ = await get_full_user(user)
                display_user_info(user, full)
            else:
                console.print(f"[red]{err}[/red]")
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        
        elif choice == "02":
            phone = Prompt.ask("[bold cyan]Masukkan nomor (format: +628123456789)[/bold cyan]")
            if not phone:
                console.print("[red]Nomor tidak boleh kosong.[/red]")
                input("\n[dim]Tekan Enter...[/dim]")
                continue
            
            with Progress(SpinnerColumn(), TextColumn("[cyan]Mencari user...[/cyan]"), console=console) as p:
                p.add_task("", total=None)
                user, err = await get_user_info(phone)
            
            if user:
                full, _ = await get_full_user(user)
                display_user_info(user, full)
            else:
                console.print(f"[red]❌ {err}[/red]")
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        
        elif choice == "03":
            user_id = Prompt.ask("[bold cyan]Masukkan User ID (angka)[/bold cyan]")
            if not user_id or not user_id.isdigit():
                console.print("[red]ID harus angka.[/red]")
                input("\n[dim]Tekan Enter...[/dim]")
                continue
            
            with Progress(SpinnerColumn(), TextColumn("[cyan]Mencari user...[/cyan]"), console=console) as p:
                p.add_task("", total=None)
                user, err = await get_user_info(int(user_id))
            
            if user:
                full, _ = await get_full_user(user)
                display_user_info(user, full)
            else:
                console.print(f"[red]❌ {err}[/red]")
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        
        elif choice == "04":
            username = Prompt.ask("[bold cyan]Masukkan username (tanpa @)[/bold cyan]")
            if not username:
                console.print("[red]Username tidak boleh kosong.[/red]")
                input("\n[dim]Tekan Enter...[/dim]")
                continue
            
            with Progress(SpinnerColumn(), TextColumn("[cyan]Mengambil foto...[/cyan]"), console=console) as p:
                p.add_task("", total=None)
                user, err = await get_user_info(f"@{username}")
                if user:
                    path, err2 = await download_photo(user)
                    if path:
                        console.print(f"[green]Foto disimpan ke: {path}[/green]")
                    else:
                        console.print(f"[red]❌ {err2}[/red]")
                else:
                    console.print(f"[red]❌ {err}[/red]")
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")

# ====================== MAIN ====================
def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

def teleg():
    main()
