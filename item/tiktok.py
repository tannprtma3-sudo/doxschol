#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import time
import json
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

# ── Rich UI ────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.align import Align
    from rich import box
    from rich.layout import Layout
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
except ImportError:
    os.system('pip install rich')
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.align import Align
    from rich import box
    from rich.layout import Layout
    from rich.live import Live
    from rich.prompt import Prompt, Confirm

console = Console()

# ── UTF-8 Setup ────────────────────────────────────────────────
def _setup_utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
_setup_utf8_stdout()

# ── UI Helpers ──────────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]TIKTOK OSINT[/bold cyan] [bold white]v1.0[/bold white]',
        f'[dim white]SYSTEM TIME: {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold cyan]  ,_,\n'
        '    (o,o)    [bold white]TIKTOK OSINT[/bold white]\n'
        '    {`"\'}    [dim]ghost-track Intelligence osint[/dim]\n'
        '    -"-"-    [dim]Created by denz[/dim][/bold cyan]\n    '
    )
    return Align.center(Text.from_markup(logo))

def loading_animation(task_name, duration):
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='blue', finished_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task(task_name, total=100)
        step = 100 / duration / 10
        while not progress.finished:
            progress.update(task, advance=step)
            time.sleep(0.1)

def format_number(num) -> str:
    if num is None:
        return '0'
    try:
        n = int(num)
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}".replace('.0', '') + 'M'
        if n >= 1_000:
            return f"{n/1_000:.1f}".replace('.0', '') + 'K'
        return str(n)
    except:
        return str(num)

def format_timestamp(ts) -> str:
    if not ts or ts == 0:
        return 'Unknown'
    try:
        return datetime.fromtimestamp(ts).strftime('%d %B %Y')
    except:
        return str(ts)

# ── FLAG ICON — FULL COUNTRY SUPPORT ──────────────────────────

def flag_icon(code: str) -> str:
    if not code:
        return '🌍'
    code = code.upper()
    if len(code) != 2 or not code.isalpha():
        return '🌍'
    try:
        return chr(0x1F1E6 + ord(code[0]) - ord('A')) + chr(0x1F1E6 + ord(code[1]) - ord('A'))
    except:
        return '🌍'

# ── COUNTRY DATABASE ───────────────────────────────────────────

COUNTRIES = {
    'ID': 'Indonesia', 'US': 'United States', 'GB': 'United Kingdom',
    'JP': 'Japan', 'KR': 'South Korea', 'IN': 'India', 'BR': 'Brazil',
    'RU': 'Russia', 'DE': 'Germany', 'FR': 'France', 'IT': 'Italy',
    'ES': 'Spain', 'CA': 'Canada', 'AU': 'Australia', 'MY': 'Malaysia',
    'SG': 'Singapore', 'PH': 'Philippines', 'TH': 'Thailand', 'VN': 'Vietnam',
    'TR': 'Turkey', 'SA': 'Saudi Arabia', 'AE': 'UAE', 'EG': 'Egypt',
    'NG': 'Nigeria', 'ZA': 'South Africa', 'MX': 'Mexico', 'AR': 'Argentina',
    'CL': 'Chile', 'CO': 'Colombia', 'PE': 'Peru', 'NZ': 'New Zealand',
    'PK': 'Pakistan', 'BD': 'Bangladesh', 'LK': 'Sri Lanka', 'NP': 'Nepal',
    'KH': 'Cambodia', 'LA': 'Laos', 'MM': 'Myanmar', 'BN': 'Brunei',
    'TW': 'Taiwan', 'HK': 'Hong Kong', 'MO': 'Macau', 'CN': 'China',
    'IL': 'Israel', 'JO': 'Jordan', 'KW': 'Kuwait', 'QA': 'Qatar',
    'BH': 'Bahrain', 'OM': 'Oman', 'YE': 'Yemen', 'SY': 'Syria',
    'LB': 'Lebanon', 'PS': 'Palestine', 'IQ': 'Iraq', 'IR': 'Iran',
    'AF': 'Afghanistan', 'KZ': 'Kazakhstan', 'UZ': 'Uzbekistan',
    'UA': 'Ukraine', 'PL': 'Poland', 'RO': 'Romania', 'BG': 'Bulgaria',
    'GR': 'Greece', 'AL': 'Albania', 'HR': 'Croatia', 'RS': 'Serbia',
    'BA': 'Bosnia', 'SI': 'Slovenia', 'SK': 'Slovakia', 'CZ': 'Czech',
    'HU': 'Hungary', 'AT': 'Austria', 'CH': 'Switzerland', 'BE': 'Belgium',
    'NL': 'Netherlands', 'LU': 'Luxembourg', 'DK': 'Denmark', 'NO': 'Norway',
    'SE': 'Sweden', 'FI': 'Finland', 'IS': 'Iceland', 'IE': 'Ireland',
    'PT': 'Portugal', 'MA': 'Morocco', 'DZ': 'Algeria', 'TN': 'Tunisia',
    'LY': 'Libya', 'SD': 'Sudan', 'ET': 'Ethiopia', 'KE': 'Kenya',
    'TZ': 'Tanzania', 'UG': 'Uganda', 'GH': 'Ghana', 'CI': 'Ivory Coast',
    'SN': 'Senegal', 'CM': 'Cameroon', 'ZW': 'Zimbabwe', 'ZM': 'Zambia',
    'AO': 'Angola', 'MZ': 'Mozambique', 'MG': 'Madagascar',
}

def get_country_name(code: str) -> str:
    if not code:
        return None
    return COUNTRIES.get(code.upper())

# ── COUNTRY DETECTION FALLBACK ─────────────────────────────────

def detect_country_from_ip() -> str:
    """Deteksi negara dari IP menggunakan API gratis."""
    try:
        resp = requests.get('http://ip-api.com/json/', timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                return data.get('countryCode')
    except:
        pass
    return None

def detect_country_from_tiktok_bio(bio: str) -> str:
    """Deteksi negara dari bio TikTok (keyword)."""
    if not bio:
        return None
    
    bio_lower = bio.lower()
    
    # Keyword mapping
    keywords = {
        'ID': ['indonesia', 'indonesian', 'jakarta', 'bandung', 'surabaya', 'medan', 'balikpapan', 'makassar'],
        'MY': ['malaysia', 'malaysian', 'kuala lumpur', 'kl', 'penang', 'johor'],
        'SG': ['singapore', 'sg', 's' 'pore'],
        'PH': ['philippines', 'filipino', 'manila', 'cebu'],
        'TH': ['thailand', 'thai', 'bangkok', 'phuket'],
        'VN': ['vietnam', 'vietnamese', 'hanoi', 'ho chi minh', 'saigon'],
        'US': ['usa', 'united states', 'america', 'american', 'new york', 'la', 'california', 'texas'],
        'GB': ['uk', 'united kingdom', 'england', 'british', 'london', 'manchester'],
        'JP': ['japan', 'japanese', 'tokyo', 'osaka', 'kyoto'],
        'KR': ['korea', 'south korea', 'seoul', 'busan'],
        'IN': ['india', 'indian', 'mumbai', 'delhi', 'bangalore', 'chennai'],
        'BR': ['brazil', 'brazilian', 'sao paulo', 'rio'],
        'RU': ['russia', 'russian', 'moscow', 'st petersburg'],
        'DE': ['germany', 'german', 'berlin', 'munich'],
        'FR': ['france', 'french', 'paris', 'lyon'],
        'IT': ['italy', 'italian', 'rome', 'milan', 'venice'],
        'ES': ['spain', 'spanish', 'madrid', 'barcelona'],
        'TR': ['turkey', 'turkish', 'istanbul', 'ankara'],
        'SA': ['saudi', 'riyadh', 'jeddah', 'mecca'],
        'AE': ['uae', 'dubai', 'abu dhabi', 'sharjah'],
        'AU': ['australia', 'australian', 'sydney', 'melbourne', 'brisbane'],
        'NZ': ['new zealand', 'nz', 'auckland', 'wellington'],
        'CA': ['canada', 'canadian', 'toronto', 'vancouver', 'montreal'],
        'MX': ['mexico', 'mexican', 'mexico city'],
        'AR': ['argentina', 'argentinian', 'buenos aires'],
        'CL': ['chile', 'chilean', 'santiago'],
        'CO': ['colombia', 'colombian', 'bogota'],
        'PE': ['peru', 'peruvian', 'lima'],
        'EG': ['egypt', 'egyptian', 'cairo'],
        'NG': ['nigeria', 'nigerian', 'lagos', 'abuja'],
        'ZA': ['south africa', 'cape town', 'johannesburg'],
        'PK': ['pakistan', 'pakistani', 'karachi', 'lahore', 'islamabad'],
        'BD': ['bangladesh', 'bangladeshi', 'dhaka'],
        'LK': ['sri lanka', 'colombo'],
        'NP': ['nepal', 'nepali', 'kathmandu'],
        'KH': ['cambodia', 'cambodian', 'phnom penh'],
        'LA': ['laos', 'laotian', 'vientiane'],
        'MM': ['myanmar', 'burma', 'yangon'],
        'BN': ['brunei', 'bandar seri begawan'],
    }
    
    for code, words in keywords.items():
        for word in words:
            if word in bio_lower:
                return code
    
    return None

def detect_language_from_bio(bio: str) -> str:
    """Deteksi bahasa dari bio berdasarkan kata-kata umum."""
    if not bio:
        return None
    
    bio_lower = bio.lower()
    
    lang_keywords = {
        'id': ['yang', 'dan', 'di', 'ke', 'dengan', 'untuk', 'dari', 'ini', 'itu', 'aku', 'kamu', 'saya', 'kita'],
        'en': ['the', 'and', 'for', 'with', 'from', 'this', 'that', 'you', 'i', 'we', 'they', 'are', 'was'],
        'ja': ['です', 'ます', 'の', 'に', 'を', 'が', 'で', 'と', 'は', 'も', 'た', 'ない'],
        'ko': ['입니다', '습니다', '의', '에', '를', '이', '가', '로', '은', '는', '하다'],
        'zh': ['的', '了', '是', '我', '你', '他', '她', '们', '在', '有', '这', '那'],
        'es': ['el', 'la', 'los', 'las', 'y', 'en', 'para', 'con', 'de', 'que', 'se', 'me'],
        'fr': ['le', 'la', 'les', 'et', 'en', 'pour', 'avec', 'de', 'que', 'ce', 'se'],
        'de': ['der', 'die', 'das', 'und', 'für', 'mit', 'von', 'zu', 'den', 'dem'],
        'it': ['il', 'la', 'lo', 'e', 'per', 'con', 'di', 'che', 'si', 'mi'],
        'ru': ['и', 'в', 'на', 'с', 'по', 'к', 'у', 'за', 'от', 'не', 'я', 'ты'],
        'pt': ['o', 'a', 'os', 'as', 'e', 'para', 'com', 'de', 'que', 'se', 'me'],
        'ar': ['في', 'من', 'على', 'إلى', 'عن', 'مع', 'ما', 'هذا', 'ذلك', 'كان'],
        'hi': ['और', 'में', 'से', 'को', 'का', 'की', 'के', 'है', 'था', 'मैं'],
        'ms': ['dan', 'di', 'ke', 'dengan', 'untuk', 'dari', 'ini', 'itu', 'aku', 'kamu', 'saya'],
        'th': ['และ', 'ใน', 'ของ', 'ให้', 'ว่า', 'มี', 'จะ', 'ได้', 'นี้', 'นั้น'],
        'vi': ['và', 'trong', 'cho', 'với', 'từ', 'của', 'này', 'đó', 'tôi', 'bạn'],
        'tr': ['ve', 'için', 'ile', 'bu', 'şu', 'ben', 'sen', 'biz', 'onlar'],
    }
    
    for code, words in lang_keywords.items():
        count = 0
        for word in words:
            if word in bio_lower:
                count += 1
        if count >= 2:  # Minimal 2 kata cocok
            return code
    
    return None

# ── TikTok API (NEW) ─────────────────────────────────────────────────

def fetch_profile_details(username: str) -> dict:
    """GET detail profil TikTok dari storyviewer.ai API."""
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://storyviewer.ai",
        "Referer": "https://storyviewer.ai/tiktok-story-viewer",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "TE": "trailers",
    }
    
    resp = session.post(
        "https://storyviewer.ai/api/v1/tiktok/user_info",
        headers=headers,
        json={
            "page_id": "",
            "user_value": username
        },
        timeout=30
    )
    
    resp.raise_for_status()
    result = resp.json()
    
    if not result.get("data"):
        raise Exception("Gagal mengambil profil")
    
    profile = result["data"]
    
    # Konversi ke format yang sama dengan API sebelumnya
    converted_data = {
        "data": {
            "data": {
                "user": {
                    "id": profile.get("uid"),
                    "uniqueId": profile.get("user_name"),
                    "nickname": profile.get("full_name"),
                    "signature": profile.get("bio") or "",
                    "verified": profile.get("is_verified", False),
                    "privateAccount": profile.get("is_private", False),
                    "avatarLarger": profile.get("profile_pic_url_hd"),
                    "avatarMedium": profile.get("profile_pic_url"),
                    "avatarThumb": profile.get("profile_pic_url"),
                    "createTime": 0,  # Tidak tersedia di API ini
                    "region": "-",
                    "language": "-",
                    "secUid": "-",
                },
                "stats": {
                    "followerCount": profile.get("followers", 0),
                    "followingCount": profile.get("following", 0),
                    "heartCount": profile.get("hearts", 0),
                    "videoCount": profile.get("posts", 0),
                    "diggCount": profile.get("hearts", 0),
                    "friendCount": 0,
                }
            }
        }
    }
    
    return converted_data

def fetch_profile_videos(username: str) -> dict:
    """GET daftar video dari profil TikTok."""
    session = requests.Session()
    
    # Ambil dulu UID dari profile
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://storyviewer.ai",
        "Referer": "https://storyviewer.ai/tiktok-story-viewer",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "TE": "trailers",
    }
    
    # Ambil profil dulu untuk dapat UID
    resp_profile = session.post(
        "https://storyviewer.ai/api/v1/tiktok/user_info",
        headers=headers,
        json={
            "page_id": "",
            "user_value": username
        },
        timeout=30
    )
    
    resp_profile.raise_for_status()
    profile_result = resp_profile.json()
    
    if not profile_result.get("data"):
        raise Exception("Gagal mengambil profil untuk mendapatkan UID")
    
    uid = profile_result["data"].get("uid")
    
    # Ambil video
    video_headers = {
        **headers,
        "tracking-marker": "",
    }
    
    resp_video = session.post(
        "https://storyviewer.ai/api/v1/tiktok/publications",
        headers=video_headers,
        json={
            "user_value": username,
            "uid": uid,
            "page_size": 50
        },
        timeout=30
    )
    
    resp_video.raise_for_status()
    result = resp_video.json()
    
    data = result.get("data", {})
    if isinstance(data, dict):
        videos = data.get("items", [])
    else:
        videos = data
    
    if not isinstance(videos, list):
        videos = []
    
    # Konversi ke format yang sama dengan API sebelumnya
    converted_videos = []
    for video in videos:
        if not isinstance(video, dict):
            continue
        
        # Ambil music info jika ada
        music_info = video.get("music", {}) or {}
        
        converted_video = {
            "video_id": video.get("video_id", ""),
            "title": video.get("caption") or "(No Caption)",
            "play": video.get("video_url", ""),
            "wmplay": video.get("video_url", ""),
            "duration": video.get("duration", 0),
            "play_count": video.get("play_count", 0),
            "digg_count": video.get("like_count", 0),
            "comment_count": video.get("comment_count", 0),
            "share_count": video.get("share_count", 0),
            "download_count": video.get("download_count", 0),
            "collect_count": video.get("collect_count", 0),
            "repost_count": video.get("repost_count", 0),
            "create_time": 0,  # Tidak tersedia di API ini
            "region": "-",
            "music_info": {
                "title": music_info.get("title", ""),
                "author": music_info.get("author", ""),
            }
        }
        converted_videos.append(converted_video)
    
    return {
        "data": {
            "data": {
                "videos": converted_videos
            }
        }
    }

# ── Display Functions ──────────────────────────────────────────

def display_profile(data: dict) -> None:
    """Tampilkan profil dengan fallback detection."""
    inner = data.get("data", {}).get("data", {})
    user = inner.get("user", {})
    stats = inner.get("stats", {})

    # ── Header Profile ──
    username = user.get("uniqueId", "-")
    nickname = user.get("nickname", "-")
    bio = user.get("signature", "") or "(kosong)"
    verified = user.get("verified", False)
    private = user.get("privateAccount", False)

    verified_icon = "✅" if verified else "❌"
    private_icon = "🔒" if private else "🔓"

    console.print(Panel(
        f"[bold cyan]@{username}[/bold cyan]\n"
        f"[bold white]{nickname}[/bold white]\n"
        f"[dim]{bio}[/dim]\n"
        f"[dim]{verified_icon} Verified | {private_icon} Account[/dim]",
        title="PROFIL TIKTOK",
        border_style="cyan",
        box=box.HEAVY
    ))

    # ── Stats ──
    stats_table = Table(
        title="STATISTIK",
        box=box.ROUNDED,
        border_style='green',
        show_header=False
    )
    stats_table.add_column("Stat", style="bold cyan", width=16)
    stats_table.add_column("Value", style="white", justify="right")

    stat_items = [
        ("Followers", format_number(stats.get("followerCount", 0))),
        ("Following", format_number(stats.get("followingCount", 0))),
        ("Hearts", format_number(stats.get("heartCount", 0))),
        ("Videos", format_number(stats.get("videoCount", 0))),
        ("Diggs", format_number(stats.get("diggCount", 0))),
        ("Friends", format_number(stats.get("friendCount", 0))),
    ]

    for label, value in stat_items:
        stats_table.add_row(label, str(value))

    console.print(stats_table)

    # ── Region & Language Detection ──
    region = user.get("region")
    language = user.get("language")
    
    # Fallback: detect from bio
    detected_region = None
    detected_lang = None
    
    if not region or region == '-':
        detected_region = detect_country_from_tiktok_bio(bio)
    
    if not language or language == '-':
        detected_lang = detect_language_from_bio(bio)
    
    # Gunakan hasil deteksi jika API tidak return
    final_region = region if region and region != '-' else detected_region
    final_lang = language if language and language != '-' else detected_lang
    
    # ── Details ──
    created = format_timestamp(user.get("createTime", 0))
    
    detail_table = Table(
        title="DETAILS",
        box=box.ROUNDED,
        border_style='magenta'
    )
    detail_table.add_column("Field", style="bold cyan", width=16)
    detail_table.add_column("Value", style="white")
    
    # Region with flag
    region_display = "-"
    if final_region:
        country_name = get_country_name(final_region)
        flag = flag_icon(final_region)
        region_display = f"{flag} {country_name if country_name else final_region}"
        if region and region != '-' and not detected_region:
            # API memberikan region
            pass
        elif detected_region and not region:
            region_display += " [dim](detected from bio)[/dim]"
    else:
        # Fallback terakhir: detect dari IP
        ip_region = detect_country_from_ip()
        if ip_region:
            country_name = get_country_name(ip_region)
            flag = flag_icon(ip_region)
            region_display = f"{flag} {country_name if country_name else ip_region} [dim](from IP)[/dim]"
    
    # Language
    lang_display = "-"
    if final_lang:
        lang_display = final_lang
        if detected_lang and not language:
            lang_display += " [dim](detected from bio)[/dim]"

    details = [
        ("User ID", user.get("id", "-")),
        ("Sec UID", user.get("secUid", "-")[:20] + "..." if user.get("secUid") else "-"),
        ("Region", region_display),
        ("Language", lang_display),
        ("Created", created),
        ("Verified", "Yes" if verified else "No"),
        ("Private", "Yes" if private else "No"),
    ]

    for field, value in details:
        detail_table.add_row(field, str(value))

    console.print(detail_table)
    
    # ── Info jika menggunakan fallback ──
    if detected_region:
        console.print("[dim]Region detected from bio content[/dim]")
    if detected_lang:
        console.print("[dim]Language detected from bio content[/dim]")

    # ── Avatar URL ──
    avatar = user.get("avatarLarger") or user.get("avatarMedium") or user.get("avatarThumb")
    if avatar:
        console.print(f"\n[dim]Avatar: {avatar}[/dim]")

def display_videos(data: dict) -> None:
    """Tampilkan daftar video dengan style OWLTRACK."""
    inner = data.get("data", {}).get("data", {})
    videos = inner.get("videos", [])

    if not videos:
        console.print("[bold yellow]Tidak ada video ditemukan.[/bold yellow]")
        return

    console.print(f"\n[bold cyan]Total Video: {len(videos)}[/bold cyan]\n")

    for i, v in enumerate(videos, start=1):
        # Video header
        title = v.get("title", "-")[:60] + "..." if len(v.get("title", "")) > 60 else v.get("title", "-")
        console.print(Panel(
            f"[bold white]{i}. {title}[/bold white]",
            border_style="blue",
            box=box.HEAVY
        ))

        # Video stats table
        vid_table = Table(box=box.ROUNDED, border_style='cyan', show_header=False)
        vid_table.add_column("Field", style="bold cyan", width=14)
        vid_table.add_column("Value", style="white")

        region = v.get("region", "-")
        region_display = f"{flag_icon(region)} {region}" if region and region != '-' else "-"

        vid_data = [
            ("Video ID", v.get("video_id", "-")),
            ("Region", region_display),
            ("Duration", f"{v.get('duration', 0)} detik"),
            ("Play URL", v.get("play", "-")[:50] + "..." if len(v.get("play", "")) > 50 else v.get("play", "-")),
            ("WMPlay", v.get("wmplay", "-")[:50] + "..." if len(v.get("wmplay", "")) > 50 else v.get("wmplay", "-")),
        ]
        for field, value in vid_data:
            vid_table.add_row(field, str(value))

        console.print(vid_table)

        # Engagement stats
        eng_table = Table(box=box.ROUNDED, border_style='green', show_header=False)
        eng_table.add_column("Stat", style="bold green", width=14)
        eng_table.add_column("Value", style="white", justify="right")

        eng_data = [
            ("Play Count", format_number(v.get("play_count", 0))),
            ("Digg Count", format_number(v.get("digg_count", 0))),
            ("Comment", format_number(v.get("comment_count", 0))),
            ("Share", format_number(v.get("share_count", 0))),
            ("Download", format_number(v.get("download_count", 0))),
            ("Collect", format_number(v.get("collect_count", 0))),
            ("Repost", format_number(v.get("repost_count", 0))),
        ]
        for label, value in eng_data:
            eng_table.add_row(label, str(value))

        console.print(eng_table)

        # Music info
        music = v.get("music_info") or {}
        if music:
            console.print(f"[dim]Music: {music.get('title', '-')} by {music.get('author', '-')}[/dim]")

        # Created time
        created = format_timestamp(v.get("create_time", 0))
        console.print(f"[dim]Created: {created}[/dim]")

        console.print("─" * 60)

def display_full_data(profile_data: dict, videos_data: dict) -> None:
    """Tampilkan semua data dengan menu interaktif."""
    while True:
        clear_screen()
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(
            box=box.DOUBLE_EDGE,
            show_header=False,
            expand=True,
            border_style='blue',
            padding=(0, 1)
        )
        menu_table.add_column('No', justify='center', style='bold cyan', width=4)
        menu_table.add_column('Module', justify='left', style='white')
        menu_table.add_column('Status', justify='center', width=8)

        menu_table.add_row('01', '[bold white]VIEW PROFILE[/]\n[dim italic]↪ Lihat detail profil[/]', '[bold green]READY[/]')
        menu_table.add_row('02', '[bold white]VIEW VIDEOS[/]\n[dim italic]↪ Lihat daftar video[/]', '[bold green]READY[/]')
        menu_table.add_row('03', '[bold white]EXPORT JSON[/]\n[dim italic]↪ Export semua data ke file[/]', '[bold green]READY[/]')
        menu_table.add_section()
        menu_table.add_row('00', '[bold cyan]BACK TO MAIN[/bold cyan]', '')

        console.print(Panel(menu_table))
        choice = input('\n[tiktok-owl@shadow:~#] ').strip()

        if choice in ('00', '0'):
            break
        elif choice in ('01', '1'):
            display_profile(profile_data)
            input('\n[Press Enter to Return]')
        elif choice in ('02', '2'):
            display_videos(videos_data)
            input('\n[Press Enter to Return]')
        elif choice in ('03', '3'):
            export_data(profile_data, videos_data)
        else:
            console.print('[bold red]Invalid option.[/bold red]')
            time.sleep(1)

def export_data(profile_data: dict, videos_data: dict) -> None:
    """Export data ke JSON."""
    username = profile_data.get("data", {}).get("data", {}).get("user", {}).get("uniqueId", "unknown")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"tiktok_{username}_{timestamp}.json"

    data = {
        "scraped_at": datetime.now().isoformat(),
        "profile": profile_data,
        "videos": videos_data
    }

    os.makedirs("tiktok-results", exist_ok=True)
    filepath = os.path.join("tiktok-results", filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    console.print(f'[bold green]Data exported to: {filepath}[/bold green]')
    input('\n[Press Enter to Return]')

# ── Main Menu ──────────────────────────────────────────────────

def main_menu():
    while True:
        clear_screen()
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(
            box=box.DOUBLE_EDGE,
            show_header=False,
            expand=True,
            border_style='blue',
            padding=(0, 1)
        )
        menu_table.add_column('No', justify='center', style='bold cyan', width=4)
        menu_table.add_column('Module', justify='left', style='white')
        menu_table.add_column('Status', justify='center', width=8)

        menu_table.add_row('01', '[bold white]TIKTOK OSINT[/]\n[dim italic]↪ Scrape profil & videos[/]', '[bold green]READY[/]')
        menu_table.add_section()
        menu_table.add_row('00', '[bold cyan]EXIT[/bold cyan]', '')

        console.print(Panel(menu_table))
        choice = input('\n[ghostl-track@tiktok-osint:~#] ').strip()

        if choice in ('00', '0'):
            sys.exit(0)
        elif choice in ('01', '1'):
            menu_scrape()
        else:
            console.print('[bold red]Invalid option.[/bold red]')
            time.sleep(1)

def menu_scrape():
    clear_screen()
    console.print(get_header())
    console.print(Panel('[bold white]TIKTOK OSINT[/bold white]', style='cyan'))
    
    username = Prompt.ask("[bold cyan][?][/bold cyan] [white]Username TikTok (tanpa @)")
    if not username:
        return

    username = username.strip()
    if username.startswith('@'):
        username = username[1:]

    loading_animation(f"mengambil data @{username}...", 3)

    profile_data = None
    videos_data = None
    errors = []

    # Scrape profile
    try:
        profile_data = fetch_profile_details(username)
        console.print('[bold green]Profile fetched[/bold green]')
    except Exception as e:
        errors.append(f"Profile: {str(e)}")
        console.print(f'[bold red]Profile error: {str(e)}[/bold red]')

    # Scrape videos
    try:
        videos_data = fetch_profile_videos(username)
        console.print('[bold green]Videos fetched[/bold green]')
    except Exception as e:
        errors.append(f"Videos: {str(e)}")
        console.print(f'[bold red]Videos error: {str(e)}[/bold red]')

    if not profile_data and not videos_data:
        console.print('[bold red]Gagal mengambil data.[/bold red]')
        for err in errors:
            console.print(f'[red]  - {err}[/red]')
        input('\n[Press Enter to Return]')
        return

    if profile_data and videos_data:
        display_full_data(profile_data, videos_data)
    elif profile_data:
        display_profile(profile_data)
        input('\n[Press Enter to Return]')
    elif videos_data:
        display_videos(videos_data)
        input('\n[Press Enter to Return]')

# ── Entry Point ──────────────────────────────────────────────────

def tiktok():
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print('\n[bold red]Force Exit Detected.[/bold red]')
        sys.exit(2)