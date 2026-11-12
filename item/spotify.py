#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SPOTIFY DOWNLOADER — SHADOWDEATH EDITION
Download lagu & playlist dari Spotify via spotyloader.com
UI: Ghost-Track Style (Blue Theme, No Cyan)
coded by denz 
"""

import os
import sys
import time
import json
import argparse
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import box
    from rich.prompt import Prompt, Confirm
except ImportError:
    os.system('pip install rich')
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import box
    from rich.prompt import Prompt, Confirm

console = Console()

VERSION = "v1.0"
CODED_BY = "denz"

BASE = "https://spotyloader.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://spotyloader.com/"
}

# ── UI HEADER (BLUE ONLY) ──
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]SPOTIFY DL[/bold blue] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]SPOTIFY DOWNLOADER[/bold white]\n'
        '    {`"\'}    [dim]Download lagu & playlist[/dim]\n'
        '    -"-"-    [dim]coded by [bold blue]denz[/bold blue][/dim][/bold blue]\n    '
    )
    return Align.center(Text.from_markup(logo))

def get_footer():
    return Panel(
        "[dim]Powered by python[/dim]",
        style="dim",
        border_style="blue",
        box=box.HEAVY
    )

def loading_animation(task_name, duration=2):
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold blue]{task.description}'),
        BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task(task_name, total=100)
        step = 100 / (duration * 10)
        while not progress.finished:
            progress.update(task, advance=step)
            time.sleep(0.1)

# ── API FUNCTIONS ──
def api_request(path, method="GET", data=None):
    url = f"{BASE}{path}"
    headers = HEADERS.copy()
    if data:
        headers["Content-Type"] = "application/json"
    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        else:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        if resp.status_code != 200 and resp.status_code != 202:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
        return resp.json()
    except Exception as e:
        raise Exception(f"API error: {str(e)}")

def get_track_info(url):
    """Ambil metadata lagu dari Spotify."""
    resp = api_request(f"/api/spotify/info?url={url}")
    return resp.get("post", {})

def get_playlist(url):
    """Ambil metadata playlist dari Spotify."""
    resp = api_request("/api/spotify/playlist", method="POST", data={"url": url})
    return resp.get("post", {})

def download_track(url, format="mp3"):
    """Download track dan return link download."""
    resp = api_request("/api/spotify/track", method="POST", data={"url": url, "format": format})
    job_id = resp.get("jobId")
    if not job_id:
        raise Exception("Gagal membuat job download")
    
    # Polling status
    max_attempts = 80
    for i in range(max_attempts):
        time.sleep(2.5)
        status_resp = api_request(f"/api/spotify/track/status/{job_id}")
        if status_resp.get("status") == "ready" and status_resp.get("downloadLink"):
            return status_resp["downloadLink"]
        if status_resp.get("status") == "error":
            raise Exception("Download gagal diproses server")
        # Print progress dots jika di CLI
        if not sys.stdout.isatty():
            sys.stdout.write(".")
            sys.stdout.flush()
    raise Exception("Timeout menunggu download")

def format_duration(ms):
    if not ms:
        return "0:00"
    s = round(ms / 1000)
    return f"{s//60}:{str(s%60).zfill(2)}"

def track_to_dict(track):
    return {
        "judul": track.get("name", "-"),
        "artis": track.get("artist") or ", ".join(track.get("artists", [])) or "-",
        "album": track.get("album", "-"),
        "durasi": format_duration(track.get("duration_ms")),
        "thumbnail": track.get("image") or track.get("thumbnail"),
        "url": track.get("external_urls", {}).get("spotify")
    }

# ── DISPLAY ──
def display_track_info(info, download_link=None):
    table = Table(title="🎵 TRACK INFO", box=box.ROUNDED, border_style='blue')
    table.add_column("Field", style="bold blue")
    table.add_column("Value", style="white")
    for k, v in info.items():
        if v:
            table.add_row(k.capitalize(), str(v))
    if download_link:
        table.add_row("Download", f"[link]{download_link}[/link]")
    console.print(table)

def display_playlist(playlist):
    table = Table(title="PLAYLIST INFO", box=box.ROUNDED, border_style='blue')
    table.add_column("Field", style="bold blue")
    table.add_column("Value", style="white")
    table.add_row("Judul", playlist.get("name", "-"))
    table.add_row("Owner", playlist.get("owner", "-"))
    table.add_row("Total Lagu", str(playlist.get("total_tracks", 0)))
    if playlist.get("image"):
        table.add_row("Thumbnail", playlist.get("image"))
    console.print(table)
    
    # Daftar lagu
    tracks = playlist.get("tracks", [])
    if tracks:
        track_table = Table(title="DAFTAR LAGU", box=box.ROUNDED, border_style='green')
        track_table.add_column("No", style="blue", width=4)
        track_table.add_column("Judul", style="white")
        track_table.add_column("Artis", style="yellow")
        track_table.add_column("Durasi", style="cyan")
        for idx, t in enumerate(tracks, 1):
            track_table.add_row(str(idx), t.get("judul", "-"), t.get("artis", "-"), t.get("durasi", "0:00"))
        console.print(track_table)

# ── CLI MODE ──
def cli_mode():
    parser = argparse.ArgumentParser(description="Spotify Downloader & Metadata")
    parser.add_argument("mode", choices=["--lagu", "--playlist"], help="Mode: --lagu or --playlist")
    parser.add_argument("url", help="Spotify URL")
    parser.add_argument("--format", default="mp3", choices=["mp3", "aac", "flac"], help="Format download (default: mp3)")
    parser.add_argument("--output", help="Simpan metadata ke file JSON")
    args = parser.parse_args()
    
    try:
        if args.mode == "--lagu":
            info = get_track_info(args.url)
            track = track_to_dict(info)
            console.print("[bold blue]⬇️  Mendownload...[/bold blue]")
            link = download_track(args.url, args.format)
            track["mp3"] = link
            track["format"] = f"{args.format} (320kbps)" if args.format == "mp3" else args.format
            display_track_info(track, link)
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(track, f, indent=2, ensure_ascii=False)
                    console.print(f"[bold green]Data disimpan ke {args.output}[/bold green]")
        elif args.mode == "--playlist":
            playlist = get_playlist(args.url)
            display_playlist(playlist)
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(playlist, f, indent=2, ensure_ascii=False)
                    console.print(f"[bold green]Data disimpan ke {args.output}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

# ── INTERACTIVE MENU ──
def interactive_menu():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())
        
        menu_table = Table(
            box=box.DOUBLE_EDGE,
            show_header=False,
            expand=True,
            border_style='blue',
            padding=(0, 1)
        )
        menu_table.add_column("No", justify="center", style="bold blue", width=4)
        menu_table.add_column("Menu", justify="left", style="white")
        menu_table.add_row("01", "[bold white]Download Lagu (Single)[/bold white]")
        menu_table.add_row("02", "[bold white]Info Playlist[/bold white]")
        menu_table.add_row("03", "[bold white]Batch Download (dari file)[/bold white]")
        menu_table.add_section()
        menu_table.add_row("00", "[bold red]Exit[/bold red]")
        
        console.print(Panel(menu_table, title="[bold blue]SPOTIFY DOWNLOADER[/bold blue]", border_style="blue"))
        console.print(get_footer())
        
        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")
        
        if choice in ["0", "00"]:
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break
        elif choice in ["1", "01"]:
            menu_single()
        elif choice in ["2", "02"]:
            menu_playlist()
        elif choice in ["3", "03"]:
            menu_batch()
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(1)

def menu_single():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    url = Prompt.ask("[bold blue]Link Spotify (lagu)")
    if not url:
        return
    loading_animation("[blue]Mengambil metadata...[/blue]", 2)
    try:
        info = get_track_info(url)
        track = track_to_dict(info)
        display_track_info(track)
        if Confirm.ask("[bold blue]Download lagu?", default=True):
            format_choice = Prompt.ask("[bold blue]Format (mp3/aac/flac)", default="mp3")
            loading_animation("[blue]Memproses download...[/blue]", 3)
            link = download_track(url, format_choice)
            track["mp3"] = link
            track["format"] = format_choice
            display_track_info(track, link)
            if Confirm.ask("[bold blue]Simpan metadata ke file?", default=True):
                filename = f"spotify_{track['judul'].replace(' ', '_')}.json"
                with open(filename, "w") as f:
                    json.dump(track, f, indent=2, ensure_ascii=False)
                console.print(f"[bold green]Disimpan ke {filename}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

def menu_playlist():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    url = Prompt.ask("[bold blue]Link Spotify (playlist)")
    if not url:
        return
    loading_animation("[blue]Mengambil data playlist...[/blue]", 3)
    try:
        playlist = get_playlist(url)
        display_playlist(playlist)
        if Confirm.ask("[bold blue]Simpan data playlist ke file?", default=True):
            filename = f"playlist_{playlist.get('name', 'unknown').replace(' ', '_')}.json"
            with open(filename, "w") as f:
                json.dump(playlist, f, indent=2, ensure_ascii=False)
            console.print(f"[bold green]Disimpan ke {filename}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

def menu_batch():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    filepath = Prompt.ask("[bold blue]File daftar link (satu per baris)")
    if not os.path.exists(filepath):
        console.print("[bold red]File tidak ditemukan.[/bold red]")
        input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        return
    with open(filepath, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    if not urls:
        console.print("[bold yellow]File kosong.[/bold yellow]")
        input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        return
    console.print(f"[blue]{len(urls)} link ditemukan.[/blue]")
    format_choice = Prompt.ask("[bold blue]Format (mp3/aac/flac)", default="mp3")
    results = []
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold blue]{task.description}'),
        BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task("[blue]Memproses...[/blue]", total=len(urls))
        for idx, url in enumerate(urls, 1):
            try:
                info = get_track_info(url)
                track = track_to_dict(info)
                link = download_track(url, format_choice)
                track["mp3"] = link
                track["format"] = format_choice
                results.append({"url": url, "status": "✅", "judul": track.get("judul")})
            except Exception as e:
                results.append({"url": url, "status": f"❌ {str(e)[:30]}"})
            progress.update(task, advance=1)
            time.sleep(0.5)
    table = Table(title="BATCH RESULTS", box=box.ROUNDED, border_style='blue')
    table.add_column("No", style="blue", width=4)
    table.add_column("URL", style="white")
    table.add_column("Status", style="green")
    for idx, res in enumerate(results, 1):
        table.add_row(str(idx), res["url"][:40], res["status"])
    console.print(table)
    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

# ── ENTRY ──
def spotify():
    if len(sys.argv) > 1:
        cli_mode()
    else:
        try:
            interactive_menu()
        except KeyboardInterrupt:
            console.print("\n[bold red]Force Exit Detected.[/bold red]")
            sys.exit(2)