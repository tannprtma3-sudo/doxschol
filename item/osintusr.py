import os
import sys
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

# ====================== DAFTAR 150+ PLATFORM ======================
PLATFORMS = {
    # Sosial Media Utama
    "Instagram": "https://www.instagram.com/{username}",
    "Twitter/X": "https://twitter.com/{username}",
    "Facebook": "https://www.facebook.com/{username}",
    "TikTok": "https://www.tiktok.com/@{username}",
    "YouTube": "https://www.youtube.com/@{username}",
    "Snapchat": "https://www.snapchat.com/add/{username}",
    "Pinterest": "https://www.pinterest.com/{username}",
    "Reddit": "https://www.reddit.com/user/{username}",
    "Tumblr": "https://{username}.tumblr.com",
    "LinkedIn": "https://www.linkedin.com/in/{username}",
    "Threads": "https://www.threads.net/@{username}",
    "Bluesky": "https://bsky.app/profile/{username}",
    "Mastodon": "https://mastodon.social/@{username}",
    
    # Messaging & Chat
    "Telegram": "https://t.me/{username}",
    "WhatsApp": "https://wa.me/{username}",
    "Signal": "https://signal.me/#p/{username}",
    "Discord": "https://discord.com/users/{username}",
    "Slack": "https://{username}.slack.com",
    "Line": "https://line.me/ti/p/@{username}",
    "WeChat": "https://www.wechat.com/{username}",
    "KakaoTalk": "https://story.kakao.com/{username}",
    "Viber": "https://chats.viber.com/{username}",
    
    # Gaming
    "Steam": "https://steamcommunity.com/id/{username}",
    "Xbox": "https://xboxgamertag.com/search/{username}",
    "PlayStation": "https://psnprofiles.com/{username}",
    "Nintendo": "https://nintendo.com/@{username}",
    "Epic Games": "https://www.epicgames.com/id/{username}",
    "Battle.net": "https://www.battle.net/{username}",
    "Riot Games": "https://www.riotgames.com/{username}",
    "Roblox": "https://www.roblox.com/user.aspx?username={username}",
    "Minecraft": "https://namemc.com/profile/{username}",
    "Twitch": "https://www.twitch.tv/{username}",
    "Kick": "https://kick.com/{username}",
    "Rumble": "https://rumble.com/user/{username}",
    "DLive": "https://dlive.tv/{username}",
    
    # Music & Audio
    "Spotify": "https://open.spotify.com/user/{username}",
    "SoundCloud": "https://soundcloud.com/{username}",
    "Apple Music": "https://music.apple.com/profile/{username}",
    "Deezer": "https://www.deezer.com/profile/{username}",
    "Tidal": "https://tidal.com/browse/users/{username}",
    "Bandcamp": "https://bandcamp.com/{username}",
    "Mixcloud": "https://www.mixcloud.com/{username}",
    "Audiomack": "https://audiomack.com/{username}",
    "Genius": "https://genius.com/{username}",
    
    # Video & Streaming
    "Vimeo": "https://vimeo.com/{username}",
    "Dailymotion": "https://www.dailymotion.com/{username}",
    "Bilibili": "https://space.bilibili.com/{username}",
    "VK Video": "https://vk.com/video/@{username}",
    "Odysee": "https://odysee.com/@{username}",
    
    # Programming & Tech
    "GitHub": "https://github.com/{username}",
    "GitLab": "https://gitlab.com/{username}",
    "Bitbucket": "https://bitbucket.org/{username}",
    "Stack Overflow": "https://stackoverflow.com/users/{username}",
    "HackerRank": "https://www.hackerrank.com/{username}",
    "LeetCode": "https://leetcode.com/{username}",
    "Codeforces": "https://codeforces.com/profile/{username}",
    "Dev.to": "https://dev.to/{username}",
    "Medium": "https://medium.com/@{username}",
    "Hashnode": "https://hashnode.com/@{username}",
    "Kaggle": "https://www.kaggle.com/{username}",
    
    # Blog & Writing
    "WordPress": "https://{username}.wordpress.com",
    "Blogger": "https://www.blogger.com/profile/{username}",
    "Ghost": "https://{username}.ghost.io",
    "Substack": "https://{username}.substack.com",
    "Wattpad": "https://www.wattpad.com/user/{username}",
    "Quotev": "https://www.quotev.com/{username}",
    "FanFiction": "https://www.fanfiction.net/u/{username}",
    "Archive of Our Own": "https://archiveofourown.org/users/{username}",
    
    # Photography & Art
    "Flickr": "https://www.flickr.com/people/{username}",
    "500px": "https://500px.com/p/{username}",
    "DeviantArt": "https://www.deviantart.com/{username}",
    "ArtStation": "https://www.artstation.com/{username}",
    "Behance": "https://www.behance.net/{username}",
    "Dribbble": "https://dribbble.com/{username}",
    "Unsplash": "https://unsplash.com/@{username}",
    "Pexels": "https://www.pexels.com/@{username}",
    
    # Dating & Social
    "Tinder": "https://www.tinder.com/@{username}",
    "Bumble": "https://bumble.com/@{username}",
    "OKCupid": "https://www.okcupid.com/profile/{username}",
    "Hinge": "https://hinge.com/@{username}",
    "Plenty of Fish": "https://www.pof.com/{username}",
    
    # Professional & Business
    "AngelList": "https://angel.co/u/{username}",
    "Crunchbase": "https://www.crunchbase.com/person/{username}",
    "Product Hunt": "https://www.producthunt.com/@{username}",
    "Fiverr": "https://www.fiverr.com/{username}",
    "Upwork": "https://www.upwork.com/freelancers/{username}",
    "Freelancer": "https://www.freelancer.com/u/{username}",
    
    # Forum & Community
    "Quora": "https://www.quora.com/profile/{username}",
    "StackExchange": "https://stackexchange.com/users/{username}",
    "ResearchGate": "https://www.researchgate.net/profile/{username}",
    "Academia.edu": "https://independent.academia.edu/{username}",
    "Couchsurfing": "https://www.couchsurfing.com/people/{username}",
    "Meetup": "https://www.meetup.com/members/{username}",
    
    # News & Bookmark
    "Pocket": "https://getpocket.com/@{username}",
    "Instapaper": "https://www.instapaper.com/p/{username}",
    "Digg": "https://digg.com/@{username}",
    "News.yc": "https://news.ycombinator.com/user?id={username}",
    
    # Lainnya
    "Patreon": "https://www.patreon.com/{username}",
    "OnlyFans": "https://onlyfans.com/{username}",
    "Linktree": "https://linktr.ee/{username}",
    "Beacons": "https://beacons.ai/{username}",
    "Carrd": "https://{username}.carrd.co",
    "About.me": "https://about.me/{username}",
    "Keybase": "https://keybase.io/{username}",
    "Gravatar": "https://en.gravatar.com/{username}",
    "Disqus": "https://disqus.com/by/{username}",
    
    # Regional (Asia)
    "Weibo": "https://weibo.com/u/{username}",
    "Douyin": "https://www.douyin.com/user/{username}",
    "Kuaishou": "https://www.kuaishou.com/profile/{username}",
    "Xiaohongshu": "https://www.xiaohongshu.com/user/profile/{username}",
    "Zhihu": "https://www.zhihu.com/people/{username}",
    "Naver": "https://blog.naver.com/{username}",
    "Daum": "https://blog.daum.net/{username}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# ====================== HEADER & BANNER ======================
def get_header():
    grid = Table.grid(expand=True)
    grid.add_column(justify='left')
    grid.add_column(justify='right')
    date_now = time.strftime('%Y-%m-%d %H:%M:%S')
    grid.add_row(
        '[bold cyan]OSINT CHECKER[/bold cyan] [bold white]v2.0[/bold white]',
        f'[dim white]⏱  {date_now}[/dim white]'
    )
    return Panel(grid, style='bold blue', border_style='blue', box=box.HEAVY)

def show_banner():
    logo = (
        '\n   [bold cyan]  ,_,\n'
        '    (o,o)    [bold white]OSINT USERNAME CHECKER[/bold white]\n'
        '    {`"\'}    [dim]Cari username di 150+ platform[/dim]\n'
        '    -"-"-    [dim]coded by [bold cyan]denz[/bold cyan][/dim][/bold cyan]\n    '
    )
    return Align.center(Text.from_markup(logo))

# ====================== FUNGSI CEK PLATFORM ======================
def check_platform(platform, url_template, username):
    """Cek apakah username ada di platform tertentu"""
    url = url_template.format(username=username)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=False)
        
        if response.status_code == 200:
            return (platform, url, "✅", "Ditemukan")
        elif response.status_code == 404:
            return (platform, url, "❌", "Tidak ditemukan")
        elif response.status_code in [301, 302, 303, 307, 308]:
            if "profile" in response.headers.get("Location", "").lower() or "user" in response.headers.get("Location", "").lower():
                return (platform, url, "✅", "Ditemukan (redirect)")
            return (platform, url, "↗️", f"Redirect {response.status_code}")
        elif response.status_code == 403:
            return (platform, url, "🚫", "Diblokir/Private")
        elif response.status_code == 429:
            return (platform, url, "⏳", "Rate limited")
        else:
            return (platform, url, "⚠️", f"Status {response.status_code}")
            
    except requests.exceptions.Timeout:
        return (platform, url, "⏰", "Timeout")
    except requests.exceptions.ConnectionError:
        return (platform, url, "🔌", "Gagal konek")
    except requests.exceptions.SSLError:
        return (platform, url, "🔒", "SSL Error")
    except Exception as e:
        return (platform, url, "❌", f"Error: {str(e)[:35]}")

# ====================== FUNGSI SEARCH ======================
def search_all_platforms(username, max_workers=20):
    """Cari username di semua platform secara paralel dengan progress bar"""
    total = len(PLATFORMS)
    results = []
    found_count = 0

    console.print(f"[bold cyan]Mencari username: [bold white]{username}[/bold white]")
    console.print(f"[dim]Total platform: {total}[/dim]")

    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        BarColumn(bar_width=None, complete_style='green'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Scanning...", total=total)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(check_platform, platform, url, username): platform
                for platform, url in PLATFORMS.items()
            }
            
            for future in as_completed(futures):
                platform, url, icon, status = future.result()
                results.append((platform, url, icon, status))
                if icon == "✅":
                    found_count += 1
                progress.advance(task)
                # Live update progress di console (optional)
                # console.print(f"{icon} {platform:20} | {status:15}")
    
    # Urutkan hasil: yang ditemukan di atas
    results.sort(key=lambda x: x[2] != "✅")
    return results, found_count

def search_by_email(email):
    """Cari berdasarkan email"""
    console.print(f"[bold cyan]Mencari berdasarkan email: [bold white]{email}[/bold white]")
    username = email.split('@')[0]
    console.print(f"[dim]Username yang dicoba: {username}[/dim]")
    return search_all_platforms(username)

# ====================== SAVE RESULTS ======================
def save_results(username, results, found_count):
    """Simpan hasil ke file"""
    filename = f"osint_result_{username}_{int(time.time())}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"HASIL OSINT - {username}\n")
        f.write(f"Total platform: {len(results)}\n")
        f.write(f"Username ditemukan di: {found_count} platform\n")
        f.write("="*70 + "\n\n")
        
        for platform, url, icon, status in results:
            if icon == "✅":
                f.write(f"[✓] {platform:25} → {url}\n")
            elif icon in ["❌", "🚫", "⏰", "🔌"]:
                f.write(f"[ ] {platform:25} → {status}\n")
            else:
                f.write(f"[?] {platform:25} → {status}\n")
    
    console.print(f"[green]Hasil disimpan ke: {filename}[/green]")
    return filename

# ====================== DISPLAY RESULTS ======================
def display_results(username, results, found_count, elapsed):
    """Tampilkan hasil dalam tabel rich"""
    table = Table(box=box.ROUNDED, border_style='cyan', title=f"[bold green]HASIL OSINT: {username}[/bold green]")
    table.add_column("No", style="bold cyan", width=4)
    table.add_column("Platform", style="bold cyan")
    table.add_column("Status", style="white")
    table.add_column("URL", style="white", overflow="ellipsis")
    
    idx = 0
    for platform, url, icon, status in results[:30]:  # Tampilkan 30 pertama saja
        idx += 1
        # Warna status
        if icon == "✅":
            status_text = f"[green]✅ Ditemukan[/green]"
        elif icon == "❌":
            status_text = f"[red]❌ Tidak ditemukan[/red]"
        elif icon == "🚫":
            status_text = f"[yellow]🚫 Private[/yellow]"
        elif icon == "⏰":
            status_text = f"[yellow]⏰ Timeout[/yellow]"
        else:
            status_text = f"[dim]{icon} {status}[/dim]"
        
        table.add_row(str(idx), platform, status_text, url[:60])
    
    if len(results) > 30:
        table.add_row("...", f"[dim]dan {len(results)-30} lainnya[/dim]", "", "")
    
    console.print(table)
    
    # Ringkasan
    console.print(f"\n[bold]RINGKASAN:[/bold]")
    console.print(f"  Ditemukan: [green]{found_count}[/green] platform")
    console.print(f"  Tidak ditemukan: [red]{len(results) - found_count}[/red] platform")
    console.print(f"  ⏱️ Waktu: [yellow]{elapsed:.2f} detik[/yellow]")
    console.print(f"  Total platform: [cyan]{len(results)}[/cyan]")

# ==================== MAIN LOOP ====================
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(get_header())
        console.print(show_banner())

        menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
        menu_table.add_column("No", justify="center", style="bold cyan", width=4)
        menu_table.add_column("Menu", justify="left", style="white")
        menu_table.add_row("01", "[bold white]Cari berdasarkan Username[/bold white]")
        menu_table.add_row("02", "[bold white]Cari berdasarkan Email[/bold white]")
        menu_table.add_row("03", "[bold white]Bulk dari File (satu username per baris)[/bold white]")
        menu_table.add_row("04", "[bold white]Lihat daftar platform[/bold white]")
        menu_table.add_row("00", "[bold red]Keluar[/bold red]")
        console.print(Panel(menu_table, title="[bold blue]OSINT USERNAME CHECKER[/bold blue]", border_style="blue"))

        choice = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]", choices=["01","02","03","04","00"])

        if choice == "00":
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

        elif choice == "01":
            username = Prompt.ask("[bold cyan]Masukkan username[/bold cyan]")
            if not username:
                console.print("[red]Username tidak boleh kosong.[/red]")
                continue
            start = time.time()
            results, found_count = search_all_platforms(username)
            elapsed = time.time() - start
            display_results(username, results, found_count, elapsed)
            if Confirm.ask("[bold cyan]Simpan hasil ke file?[/bold cyan]", default=True):
                save_results(username, results, found_count)

        elif choice == "02":
            email = Prompt.ask("[bold cyan]Masukkan email[/bold cyan]")
            if not email or '@' not in email:
                console.print("[red]Email tidak valid.[/red]")
                continue
            username = email.split('@')[0]
            start = time.time()
            results, found_count = search_all_platforms(username)
            elapsed = time.time() - start
            display_results(username, results, found_count, elapsed)
            if Confirm.ask("[bold cyan]Simpan hasil ke file?[/bold cyan]", default=True):
                save_results(username, results, found_count)

        elif choice == "03":
            filename = Prompt.ask("[bold cyan]Masukkan path file (satu username per baris)[/bold cyan]")
            if not os.path.exists(filename):
                console.print("[red]File tidak ditemukan.[/red]")
                continue
            with open(filename, 'r', encoding='utf-8') as f:
                usernames = [line.strip() for line in f if line.strip()]
            if not usernames:
                console.print("[red]File kosong.[/red]")
                continue
            console.print(f"[bold cyan]Memproses {len(usernames)} username...[/bold cyan]")
            all_results = {}
            for u in usernames:
                console.print(f"\n[bold yellow]--- {u} ---[/bold yellow]")
                start = time.time()
                results, found_count = search_all_platforms(u)
                elapsed = time.time() - start
                display_results(u, results, found_count, elapsed)
                all_results[u] = (results, found_count)
                if not Confirm.ask("[bold cyan]Lanjut ke username berikutnya?[/bold cyan]", default=True):
                    break

        elif choice == "04":
            console.print("[bold cyan]DAFTAR PLATFORM[/bold cyan]")
            platform_list = sorted(PLATFORMS.keys())
            table = Table(box=box.ROUNDED, border_style='cyan')
            table.add_column("No", style="bold cyan")
            table.add_column("Platform", style="white")
            for i, p in enumerate(platform_list, 1):
                table.add_row(str(i), p)
            console.print(table)
            console.print(f"[dim]Total: {len(PLATFORMS)} platform[/dim]")
            input("\n[dim]Tekan Enter untuk kembali...[/dim]")

        else:
            console.print("[red]Pilihan tidak valid.[/red]")

        if not Confirm.ask("[bold cyan]Kembali ke menu utama?[/bold cyan]", default=True):
            console.print("[bold yellow]Keluar...[/bold yellow]")
            break

def osint():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    osint()
