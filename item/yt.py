#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

VERSION = "v1.0"
CODED_BY = "denz"
API_BASE = "https://name-ai-kappa.vercel.app/api/yt-stalk"

# ── HEADER & BANNER (BLUE-CYAN) ──────────────────────────────

def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]YT-STALK OSINT[/bold cyan] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='cyan', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold cyan]  ,_,\n'
        '    (o,o)    [bold white]YOUTUBE OSINT[/bold white]\n'
        '    {`"\'}    [dim]yautube Intelligence[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold cyan]\n    '
    )
    return Align.center(Text.from_markup(logo))


# ── LOADING (BLUE-CYAN) ──────────────────────────────────────

def loading_animation(task_name, duration=2):
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task(task_name, total=100)
        step = 100 / (duration * 10)
        while not progress.finished:
            progress.update(task, advance=step)
            time.sleep(0.1)

# ── API CALL ──────────────────────────────────────────────────

def fetch_channel(query):
    """Fetch channel data from API"""
    url = f"{API_BASE}?q={requests.utils.quote(query)}"
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"status": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"status": False, "error": str(e)}

# ── DISPLAY ────────────────────────────────────────────────────

def display_channel(data):
    """Tampilkan data channel dengan rich tables"""
    channel_data = data.get('data', {})
    social = channel_data.get('social', {})
    inner = social.get('data', {})
    stats = channel_data.get('stats', {})

    title = inner.get('title', 'N/A')
    channel_id = inner.get('channel_id', 'N/A')
    desc = inner.get('description', '')[:300] + ('...' if len(inner.get('description', '')) > 300 else '')
    subscribers = inner.get('subscriber_count', 0)
    videos = inner.get('video_count', 0)
    views = inner.get('view_count', 0)
    published = inner.get('published_at', 'N/A')
    custom_url = inner.get('custom_url', '')
    country = inner.get('country', 'N/A')

    thumbnails = inner.get('thumbnails', {})
    avatar_url = thumbnails.get('high', {}).get('url', 'N/A')
    banner_url = inner.get('banner_url', 'N/A')

    # ── Profile Panel ──
    profile_panel = Panel(
        f"[dim]Channel ID: {channel_id}[/dim]\n"
        f"[dim]Custom URL: {custom_url if custom_url else '-'}[/dim]\n"
        f"[dim]Country: {country}[/dim]\n"
        f"[dim]Published: {published}[/dim]\n\n"
        f"[white]{desc}[/white]",
        title="CHANNEL PROFILE",
        border_style="cyan",
        box=box.HEAVY
    )
    console.print(profile_panel)

    # ── Stats ──
    stats_table = Table(title="STATISTIK", box=box.ROUNDED, border_style='green')
    stats_table.add_column("Stat", style="bold cyan")
    stats_table.add_column("Value", style="white", justify="right")
    stats_table.add_row("Subscribers", f"{subscribers:,}")
    stats_table.add_row("Videos", f"{videos:,}")
    stats_table.add_row("Views", f"{views:,}")
    console.print(stats_table)

    # ── Media ──
    console.print(Panel(
        f"[dim]Avatar: {avatar_url}[/dim]\n"
        f"[dim]Banner: {banner_url}[/dim]",
        title="MEDIA",
        border_style="yellow",
        box=box.ROUNDED
    ))

    # ── Recent Videos ──
    recent_videos = inner.get('recent_videos', [])
    if recent_videos:
        video_table = Table(
            title=f"RECENT VIDEOS ({len(recent_videos)})",
            box=box.ROUNDED,
            border_style='magenta'
        )
        video_table.add_column("No", style="cyan", width=4)
        video_table.add_column("Title", style="white")
        video_table.add_column("Published", style="yellow")
        video_table.add_column("Link", style="blue")

        for idx, vid in enumerate(recent_videos[:10], 1):
            title_vid = vid.get('title', 'N/A')[:50] + ('...' if len(vid.get('title', '')) > 50 else '')
            pub = vid.get('published_at', 'N/A')[:10]
            url = vid.get('watch_url', '#')
            video_table.add_row(str(idx), title_vid, pub, f"[link]{url}[/link]")
        console.print(video_table)
    else:
        console.print("[dim]Tidak ada recent videos.[/dim]")

    # ── Thumbnail variants ──
    if thumbnails:
        console.print("\n[bold cyan]Thumbnail Variants:[/bold cyan]")
        for size, info in thumbnails.items():
            console.print(f"  [dim]{size}: {info.get('url', 'N/A')}[/dim]")

# ── MAIN MENU ──────────────────────────────────────────────────

def main_menu():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(
            box=box.DOUBLE_EDGE,
            show_header=False,
            expand=True,
            border_style='cyan',
            padding=(0, 1)
        )
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")

        menu_table.add_row("01", "[bold white]Stalk YouTube Channel[/bold white]")
        menu_table.add_row("02", "[bold white]Batch Stalk (multiple queries)[/bold white]")
        menu_table.add_section()
        menu_table.add_row("00", "[bold red]Exit[/bold red]")

        console.print(Panel(menu_table, title="[bold cyan]YT-STALK OSINT[/bold cyan]", border_style="cyan"))
       
        choice = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]")

        if choice in ["0", "00"]:
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

        elif choice in ["1", "01"]:
            menu_stalk()
        elif choice in ["2", "02"]:
            menu_batch()
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(1)

def menu_stalk():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())

    console.print(Panel(
        "[bold white]OSINT YOUTUBE CHANNEL[/bold white]\n"
        "[dim]osint channel berdasarkan nama, username, atau ID[/dim]",
        border_style="cyan"
    ))

    query = Prompt.ask("[bold cyan]Masukkan nama channel / ID")
    if not query:
        return

    loading_animation(f"[cyan]Mencari {query}...[/cyan]", 2)

    result = fetch_channel(query)

    if result.get('status') == True and 'data' in result:
        display_channel(result)
    else:
        error = result.get('error', 'Unknown error')
        console.print(f"[bold red]Gagal: {error}[/bold red]")

    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

def menu_batch():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(get_header())
    console.print(show_banner())
    console.print("[dim]Batch Stalk: Baca file dengan satu query per baris[/dim]")

    filepath = Prompt.ask("[bold cyan]Path file queries")
    if not os.path.exists(filepath):
        console.print("[bold red]File tidak ditemukan.[/bold red]")
        input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        return

    with open(filepath, 'r') as f:
        queries = [line.strip() for line in f if line.strip()]

    if not queries:
        console.print("[bold yellow]File kosong.[/bold yellow]")
        input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        return

    console.print(f"[cyan]{len(queries)} query ditemukan.[/cyan]")

    if not Confirm.ask("[bold yellow]Lanjutkan stalk?", default=True):
        return

    results = []
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Stalking...[/cyan]", total=len(queries))

        for q in queries:
            result = fetch_channel(q)
            if result.get('status') == True and 'data' in result:
                inner = result['data'].get('social', {}).get('data', {})
                results.append({
                    'query': q,
                    'title': inner.get('title', 'N/A'),
                    'channel_id': inner.get('channel_id', 'N/A'),
                    'subscribers': inner.get('subscriber_count', 0),
                    'videos': inner.get('video_count', 0),
                    'views': inner.get('view_count', 0),
                    'published': inner.get('published_at', 'N/A')
                })
            else:
                results.append({'query': q, 'error': result.get('error', 'Unknown')})
            progress.update(task, advance=1)
            time.sleep(0.3)

    # ── Summary Table ──
    table = Table(title="BATCH RESULTS", box=box.ROUNDED, border_style='cyan')
    table.add_column("No", style="cyan", width=4)
    table.add_column("Query", style="white")
    table.add_column("Channel", style="yellow")
    table.add_column("Subscribers", style="green")
    table.add_column("Videos", style="magenta")
    table.add_column("Views", style="blue")
    table.add_column("Published", style="dim")

    for idx, res in enumerate(results, 1):
        if 'error' in res:
            table.add_row(str(idx), res['query'], '❌', '❌', '❌', '❌', '❌')
        else:
            table.add_row(
                str(idx),
                res['query'],
                res['title'][:25] + ('...' if len(res['title']) > 25 else ''),
                f"{res['subscribers']:,}",
                f"{res['videos']:,}",
                f"{res['views']:,}",
                res['published'][:10] if res['published'] != 'N/A' else 'N/A'
            )
    console.print(table)

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    outfile = f"yt_stalk_batch_{timestamp}.json"
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    console.print(f"[dim]Results saved to: {outfile}[/dim]")

    input("\n[dim]Tekan Enter untuk kembali...[/dim]")

# ── ENTRY ──────────────────────────────────────────────────────

def yt():
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Force Exit Detected.[/bold red]")
        sys.exit(2)