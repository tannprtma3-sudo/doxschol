import os
import sys
import time
import re
import json
import random
import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs

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
    from rich.syntax import Syntax
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
    from rich.syntax import Syntax

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system('pip install beautifulsoup4')
    from bs4 import BeautifulSoup

console = Console()

# ── Konfigurasi ──
API_BASE = "https://ytapi.apps.mattw.io/v3"
SCRAPE_URL = "https://tubepilot.ai/wp-admin/admin-ajax.php"

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/139.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Safari/604.1"
]

# ── Ghost-Track UI ──
def show_banner():
    logo = (
        '\n   [bold blue]  ,_,\n'
        '    (o,o)    [bold white]YOUTUBE METADATA[/bold white]\n'
        '    {`"\'}    [dim]Video info scraper & API[/dim]\n'
        '    -"-"-    [dim]coded by [bold blue]denz[/bold blue][/dim][/bold blue]\n    '
    )
    return Align.center(Text.from_markup(logo))

def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold blue]YOUTUBE METADATA[/bold blue] [bold white]v1.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

# ── Utility ──
def random_user_agent():
    return random.choice(USER_AGENTS)

def generate_quota_user():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(32))

def extract_youtube_id(input_str):
    if re.match(r'^[a-zA-Z0-9_-]{11}$', input_str):
        return input_str

    patterns = [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'v=([a-zA-Z0-9_-]{11})'
    ]
    for pat in patterns:
        match = re.search(pat, input_str)
        if match:
            return match.group(1)
    return input_str

def format_number(num):
    if num is None:
        return "0"
    try:
        n = int(num)
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M".replace(".0", "")
        if n >= 1_000:
            return f"{n/1_000:.1f}K".replace(".0", "")
        return str(n)
    except:
        return str(num)

def duration_to_str(duration):
    if not duration:
        return "N/A"
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return duration
    h, m, s = match.groups()
    parts = []
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s: parts.append(f"{s}s")
    return " ".join(parts) if parts else "0s"

# ── V1: API Method ──
def fetch_video_api(video_id, parts="snippet,statistics,contentDetails"):
    try:
        part_strategies = [
            parts,
            "snippet,statistics,contentDetails",
            "snippet,statistics"
        ]
        for p in part_strategies:
            quota_user = generate_quota_user()
            timestamp = int(time.time() * 1000)
            params = {
                "key": "foo1",
                "quotaUser": quota_user,
                "part": p,
                "id": video_id,
                "_": timestamp
            }
            url = f"{API_BASE}/videos"
            headers = {
                "User-Agent": random_user_agent(),
                "Accept": "application/json",
                "Accept-Language": "id-ID,id;q=0.9",
                "Referer": "https://www.mattw.io/",
                "Origin": "https://www.mattw.io"
            }
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("items"):
                    return data
            del params["quotaUser"]
            resp2 = requests.get(url, params=params, headers=headers, timeout=30)
            if resp2.status_code == 200:
                data = resp2.json()
                if data.get("items"):
                    return data
        return None
    except Exception:
        return None

def parse_api_data(data, video_id):
    if not data or not data.get("items"):
        return None
    item = data["items"][0]
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    content = item.get("contentDetails", {})
    status = item.get("status", {})
    recording = item.get("recordingDetails", {})
    topic = item.get("topicDetails", {})
    player = item.get("player", {})
    localizations = item.get("localizations", {})

    extracted = {
        "id": item.get("id"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "channelTitle": snippet.get("channelTitle"),
        "channelId": snippet.get("channelId"),
        "publishedAt": snippet.get("publishedAt"),
        "thumbnails": snippet.get("thumbnails", {}),
        "viewCount": stats.get("viewCount"),
        "likeCount": stats.get("likeCount"),
        "commentCount": stats.get("commentCount"),
        "duration": duration_to_str(content.get("duration")),
        "definition": content.get("definition"),
        "caption": content.get("caption"),
        "isLiveContent": content.get("isLiveContent"),
        "license": content.get("licensedContent"),
        "privacyStatus": status.get("privacyStatus"),
        "embeddable": status.get("embeddable"),
        "recordingDate": recording.get("recordingDate"),
        "location": recording.get("location", {}).get("description") if recording.get("location") else None,
        "topics": topic.get("topicCategories", []),
        "playerHtml": player.get("embedHtml", ""),
        "localizations": {lang: info.get("title") for lang, info in localizations.items()}
    }
    return extracted

# ── V2: Scrape Method ──
def fetch_video_scrape(video_url):
    try:
        payload = {
            "action": "yt_data_viewer",
            "yt_url": video_url
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://tubepilot.ai",
            "Referer": "https://tubepilot.ai/tools/youtube-data-viewer/",
            "User-Agent": random_user_agent()
        }
        resp = requests.post(SCRAPE_URL, data=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            return None
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        def extract_field(label):
            for b in soup.find_all("b"):
                if b.get_text(strip=True).lower() == label.lower() + ":":
                    nxt = b.next_sibling
                    if nxt and nxt.name is None:
                        return nxt.strip()
                    else:
                        nxt = b.find_next_sibling()
                        if nxt:
                            return nxt.get_text(strip=True)
            return None

        title = extract_field("Video Title")
        uploaded_date = extract_field("Video Uploaded Date")
        category = extract_field("Video Category")
        duration = extract_field("Duration")
        views = extract_field("Views Count")
        likes = extract_field("Likes Count")
        comments = extract_field("Comments Count")
        lang = extract_field("Default Video Language")
        audio_lang = extract_field("Default Audio Language")
        tags_raw = extract_field("Video Tags")
        tags = [t.strip() for t in tags_raw.split(",")] if tags_raw else []

        desc_div = soup.select_one(".ytdesc .ytdesc-txt")
        description = desc_div.get_text(strip=True) if desc_div else None

        thumbnails = []
        for item in soup.select(".ytimg-item"):
            ql = item.select_one("span")
            quality = ql.get_text(strip=True).replace("✦", "").strip() if ql else "default"
            link = item.select_one("a")
            url = link.get("href") if link else None
            size = item.select_one(".size-link")
            resolution = size.get_text(strip=True) if size else None
            if url:
                thumbnails.append({"quality": quality, "url": url, "resolution": resolution})

        channel_name = extract_field("Channel Name")
        channel_id = extract_field("Channel ID")
        subscribers = extract_field("Subscribers Count")
        total_views = extract_field("Total Views")

        result = {
            "video": {
                "title": title,
                "uploadedDate": uploaded_date,
                "category": category,
                "duration": duration,
                "stats": {
                    "viewsCount": int(views.replace(",", "")) if views else 0,
                    "likesCount": int(likes.replace(",", "")) if likes else 0,
                    "commentsCount": int(comments.replace(",", "")) if comments else 0
                },
                "language": {
                    "defaultLanguage": lang,
                    "defaultAudioLanguage": audio_lang
                },
                "tags": tags,
                "description": description,
                "thumbnails": thumbnails
            },
            "channel": {
                "name": channel_name,
                "id": channel_id,
                "subscribersCount": subscribers,
                "totalViews": total_views
            }
        }
        return result
    except Exception:
        return None

# ── Unified Fetcher ──
def get_video_metadata(video_input, parts="snippet,statistics,contentDetails"):
    video_id = extract_youtube_id(video_input)
    if video_input.startswith("http"):
        url_for_scrape = video_input
    else:
        url_for_scrape = f"https://www.youtube.com/watch?v={video_id}"

    # Try API first
    data = fetch_video_api(video_id, parts)
    if data:
        parsed = parse_api_data(data, video_id)
        if parsed:
            return {"method": "api", "data": parsed, "raw": data}
    # Fallback to scrape
    data = fetch_video_scrape(url_for_scrape)
    if data:
        return {"method": "scrape", "data": data}
    return None

# ── Display ──
def display_api_result(parsed):
    table = Table(box=box.ROUNDED, border_style='blue', title="[bold white]📹 YOUTUBE VIDEO (API)[/bold white]")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")
    table.add_row("ID", parsed.get("id", "N/A"))
    table.add_row("Title", parsed.get("title", "N/A"))
    table.add_row("Channel", parsed.get("channelTitle", "N/A"))
    table.add_row("Channel ID", parsed.get("channelId", "N/A"))
    table.add_row("Published", parsed.get("publishedAt", "N/A"))
    table.add_row("Views", format_number(parsed.get("viewCount")))
    table.add_row("Likes", format_number(parsed.get("likeCount")))
    table.add_row("Comments", format_number(parsed.get("commentCount")))
    table.add_row("Duration", parsed.get("duration", "N/A"))
    table.add_row("Definition", parsed.get("definition", "N/A"))
    table.add_row("Caption", parsed.get("caption", "N/A"))
    table.add_row("Live", "Yes" if parsed.get("isLiveContent") else "No")
    table.add_row("Privacy", parsed.get("privacyStatus", "N/A"))
    table.add_row("Embeddable", "Yes" if parsed.get("embeddable") else "No")
    table.add_row("License", "Yes" if parsed.get("license") else "No")
    if parsed.get("topics"):
        table.add_row("Topics", ", ".join(parsed["topics"][:3]))
    console.print(table)

    if parsed.get("description"):
        console.print(Panel(parsed["description"][:500] + ("..." if len(parsed["description"]) > 500 else ""),
                           title="[bold cyan]Description[/bold cyan]", border_style="blue"))

    thumbs = parsed.get("thumbnails", {})
    if thumbs:
        thumb_table = Table(box=box.ROUNDED, border_style='cyan', title="[bold white]Thumbnails[/bold white]")
        thumb_table.add_column("Quality", style="bold cyan")
        thumb_table.add_column("URL", style="white")
        for q, info in thumbs.items():
            url = info.get("url", "")
            thumb_table.add_row(q, url[:60] + ("..." if len(url) > 60 else ""))
        console.print(thumb_table)

def display_scrape_result(data):
    video = data.get("video", {})
    channel = data.get("channel", {})
    stats = video.get("stats", {})

    table = Table(box=box.ROUNDED, border_style='blue', title="[bold white]📹 YOUTUBE VIDEO (SCRAPE)[/bold white]")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")
    table.add_row("Title", video.get("title", "N/A"))
    table.add_row("Uploaded", video.get("uploadedDate", "N/A"))
    table.add_row("Category", video.get("category", "N/A"))
    table.add_row("Duration", video.get("duration", "N/A"))
    table.add_row("Views", format_number(stats.get("viewsCount")))
    table.add_row("Likes", format_number(stats.get("likesCount")))
    table.add_row("Comments", format_number(stats.get("commentsCount")))
    table.add_row("Language", video.get("language", {}).get("defaultLanguage", "N/A"))
    table.add_row("Audio Language", video.get("language", {}).get("defaultAudioLanguage", "N/A"))
    table.add_row("Channel", channel.get("name", "N/A"))
    table.add_row("Channel ID", channel.get("id", "N/A"))
    table.add_row("Subscribers", channel.get("subscribersCount", "N/A"))
    table.add_row("Channel Views", channel.get("totalViews", "N/A"))
    table.add_row("Tags", ", ".join(video.get("tags", [])[:5]) + ("..." if len(video.get("tags", [])) > 5 else ""))
    console.print(table)

    if video.get("description"):
        console.print(Panel(video["description"][:500] + ("..." if len(video["description"]) > 500 else ""),
                           title="[bold cyan]Description[/bold cyan]", border_style="blue"))

    thumbs = video.get("thumbnails", [])
    if thumbs:
        thumb_table = Table(box=box.ROUNDED, border_style='cyan', title="[bold white]Thumbnails[/bold white]")
        thumb_table.add_column("Quality", style="bold cyan")
        thumb_table.add_column("URL", style="white")
        for t in thumbs:
            thumb_table.add_row(t.get("quality", "default"), t.get("url", "")[:60] + ("..." if len(t.get("url", "")) > 60 else ""))
        console.print(thumb_table)

def display_result(result):
    if not result:
        console.print("[red]❌ Gagal mendapatkan metadata. Coba metode lain.[/red]")
        return
    if result["method"] == "api":
        display_api_result(result["data"])
    else:
        display_scrape_result(result["data"])

# ── Batch ──
def batch_fetch(video_ids, parts="snippet,statistics,contentDetails"):
    results = []
    for vid in video_ids:
        vid = vid.strip()
        if not vid:
            continue
        res = get_video_metadata(vid, parts)
        if res:
            results.append({"input": vid, "result": res})
        else:
            results.append({"input": vid, "result": None})
    return results

def display_batch_results(results):
    table = Table(box=box.ROUNDED, border_style='blue', title="[bold white]📋 BATCH RESULTS[/bold white]")
    table.add_column("No", style="bold cyan")
    table.add_column("Video ID", style="white")
    table.add_column("Title", style="white")
    table.add_column("Channel", style="white")
    table.add_column("Views", style="white")
    for i, item in enumerate(results, 1):
        if item["result"]:
            if item["result"]["method"] == "api":
                data = item["result"]["data"]
                title = data.get("title", "N/A")
                channel = data.get("channelTitle", "N/A")
                views = format_number(data.get("viewCount"))
            else:
                data = item["result"]["data"]
                video = data.get("video", {})
                title = video.get("title", "N/A")
                channel = data.get("channel", {}).get("name", "N/A")
                views = format_number(video.get("stats", {}).get("viewsCount"))
            table.add_row(str(i), item["input"], title[:30], channel[:20], views)
        else:
            table.add_row(str(i), item["input"], "[red]FAILED[/red]", "", "")
    console.print(table)

# ── Menu ──
def menu_single(parts):
    console.print("\n[bold yellow]📌 Masukkan URL atau Video ID[/bold yellow]")
    video_input = Prompt.ask("[bold cyan]Video URL / ID[/bold cyan]").strip()
    if not video_input:
        return
    with Progress(SpinnerColumn(), TextColumn("[bold blue]Fetching metadata...[/bold blue]"), console=console, transient=True) as progress:
        progress.add_task("", total=None)
        result = get_video_metadata(video_input, parts)
    display_result(result)

def menu_batch(parts):
    console.print("\n[bold yellow]📌 Masukkan daftar URL / ID (pisahkan dengan koma atau spasi)[/bold yellow]")
    inputs = Prompt.ask("[bold cyan]Daftar video[/bold cyan]").strip()
    if not inputs:
        return
    ids = re.split(r'[,\s]+', inputs)
    ids = [i for i in ids if i]
    if not ids:
        return
    with Progress(SpinnerColumn(), TextColumn("[bold blue]Fetching batch...[/bold blue]"), console=console, transient=True) as progress:
        progress.add_task("", total=None)
        results = batch_fetch(ids, parts)
    display_batch_results(results)

# ── Main ──
def main():
    parts = "snippet,statistics,contentDetails"  # fixed
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True, border_style='blue')
        menu_table.add_column("No", justify="center", style="bold blue", width=4)
        menu_table.add_column("Menu", justify="left", style="white")

        menu_items = [
            ("01", "Get Single Video Metadata"),
            ("02", "Get Multiple Videos (Batch)"),
            ("00", "Exit")
        ]
        for no, label in menu_items:
            menu_table.add_row(no, label)

        console.print(Panel(menu_table, title="[bold blue]YOUTUBE METADATA[/bold blue]", border_style="blue"))

        choice = Prompt.ask("[bold blue]Pilih menu[/bold blue]")

        if choice in ["0", "00"]:
            console.print("[yellow]Keluar...[/yellow]")
            break
        elif choice in ["1", "01"]:
            menu_single(parts)
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        elif choice in ["2", "02"]:
            menu_batch(parts)
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(0.5)

def pesan():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
