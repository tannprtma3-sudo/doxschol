import os
import sys
import json
import time
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich.text import Text
from rich import box

console = Console()

# ====================== API SOURCES ======================
API_FAZRIANSYAH = "https://api.fazriansyah.eu.org/v1/sekolah?npsn={npsn}"
API_IKSAN = "https://sekolah.devapi.id/sekolah?npsn={npsn}"
API_KEMENDIKBUD = "https://dataref-kemdikbud.vercel.app/pendidikan/npsn/{npsn}"

# ====================== HELPER ======================
def loading_animation(task_name, duration=2):
    with Progress(
        SpinnerColumn(spinner_name='dots'),
        TextColumn('[bold cyan]{task.description}'),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
        console=console,
    ) as progress:
        task = progress.add_task(task_name, total=100)
        step = 100 / duration / 10
        while not progress.finished:
            progress.update(task, advance=step)
            time.sleep(0.1)

def banner():
    logo = (
        '\n[bold cyan]      [bold white]OSINT SEKOLAH INDONESIA v1.0[/bold white]\n'
        '         [dim]Data Lengkap: BY  NPSN,[/dim]\n'
        '              [dim]coded by denz [/dim]\n'
    )
    return Align.center(Text.from_markup(logo))

# ====================== PARSER STATISTIK ======================
def extract_statistics(data):
    stats = {}
    possible_keys = {
        'jumlah_siswa': ['jumlah_siswa', 'jumlahSiswa', 'total_siswa', 'siswa'],
        'jumlah_siswa_l': ['jumlah_siswa_laki', 'siswa_laki', 'jumlah_siswa_l'],
        'jumlah_siswa_p': ['jumlah_siswa_perempuan', 'siswa_perempuan', 'jumlah_siswa_p'],
        'jumlah_guru': ['jumlah_guru', 'jumlahGuru', 'guru', 'total_guru'],
        'jumlah_guru_l': ['jumlah_guru_laki', 'guru_laki', 'jumlah_guru_l'],
        'jumlah_guru_p': ['jumlah_guru_perempuan', 'guru_perempuan', 'jumlah_guru_p'],
        'jumlah_rombel': ['rombel', 'jumlah_rombel', 'rombongan_belajar', 'rombel_siswa'],
    }
    
    if isinstance(data, dict):
        obj = data.get('satuanPendidikan', data)
        if isinstance(obj, dict):
            for stat, keys in possible_keys.items():
                for k in keys:
                    val = obj.get(k)
                    if val not in (None, '', '-'):
                        stats[stat] = val
                        break
    elif isinstance(data, list) and len(data) > 0:
        obj = data[0]
        if isinstance(obj, dict):
            for stat, keys in possible_keys.items():
                for k in keys:
                    val = obj.get(k)
                    if val not in (None, '', '-'):
                        stats[stat] = val
                        break
    
    if 'jumlah_siswa' in stats and 'jumlah_guru' in stats:
        try:
            siswa = float(stats['jumlah_siswa'])
            guru = float(stats['jumlah_guru'])
            if guru > 0:
                stats['rasio_siswa_guru'] = round(siswa / guru, 1)
        except:
            pass
    return stats

# ====================== TAMPILAN DATA ======================
def tampilkan_data(data, source):
    meta = {}
    # Normalisasi data
    if isinstance(data, dict) and 'satuanPendidikan' in data:
        sekolah = data['satuanPendidikan']
        meta = data.get('meta', {})
    elif isinstance(data, list) and len(data) > 0:
        sekolah = data[0]
        # beberapa API mungkin punya meta di luar list
        if len(data) > 1 and isinstance(data[1], dict) and 'meta' in data[1]:
            meta = data[1]['meta']
    else:
        sekolah = data

    # --- Ambil alamat detail jika berbentuk dict ---
    alamat_dict = sekolah.get('alamatJalan', sekolah.get('alamat', {}))
    if isinstance(alamat_dict, dict):
        jalan = alamat_dict.get('jalan', '-')
        rt = alamat_dict.get('rt', '-')
        rw = alamat_dict.get('rw', '-')
        dusun = alamat_dict.get('nama_dusun', '-')
        desa = alamat_dict.get('nama_desa', '-')
        kecamatan = alamat_dict.get('nama_kecamatan', '-')
        kabupaten = alamat_dict.get('nama_kabupaten', '-')
        provinsi = alamat_dict.get('nama_provinsi', '-')
        kode_provinsi = alamat_dict.get('kode_provinsi', '-')
        kode_kabupaten = alamat_dict.get('kode_kabupaten', '-')
        kode_kecamatan = alamat_dict.get('kode_kecamatan', '-')
        kode_wilayah = alamat_dict.get('kode_wilayah', '-')
        # Gabungkan jalan + rt/rw/dusun untuk alamat lengkap
        alamat_parts = [jalan]
        if rt != '-':
            alamat_parts.append(f"RT {rt}")
        if rw != '-':
            alamat_parts.append(f"RW {rw}")
        if dusun != '-':
            alamat_parts.append(dusun)
        alamat_str = ', '.join(alamat_parts)
    else:
        # Jika bukan dict, pakai langsung
        alamat_str = alamat_dict if alamat_dict and alamat_dict != '-' else '-'
        # fallback untuk field lain
        rt = rw = dusun = kode_wilayah = '-'
        desa = sekolah.get('namaDesaKelurahan', sekolah.get('desa', '-'))
        kecamatan = sekolah.get('namaKecamatan', sekolah.get('kecamatan', '-'))
        kabupaten = sekolah.get('namaKabupaten', sekolah.get('kabupaten', '-'))
        provinsi = sekolah.get('namaProvinsi', sekolah.get('provinsi', '-'))
        kode_provinsi = kode_kabupaten = kode_kecamatan = '-'

    # Jika alamat dict, field desa dll sudah diambil dari dict, tapi jika ada di sekolah juga, kita timpa?
    # Lebih baik gunakan dari dict karena lebih detail
    if isinstance(alamat_dict, dict):
        desa = alamat_dict.get('nama_desa', '-')
        kecamatan = alamat_dict.get('nama_kecamatan', '-')
        kabupaten = alamat_dict.get('nama_kabupaten', '-')
        provinsi = alamat_dict.get('nama_provinsi', '-')
        # Kode pos mungkin ada di alamat atau di sekolah
        kode_pos = alamat_dict.get('kode_pos', sekolah.get('kodePos', '-'))
    else:
        kode_pos = sekolah.get('kodePos', '-')

    # Siapkan tabel utama
    table_umum = Table(box=box.ROUNDED, border_style='blue', title=f"[bold cyan]DATA SEKOLAH[/bold cyan]")
    table_umum.add_column("Field", style="bold cyan")
    table_umum.add_column("Value", style="white")
    
    fields_umum = [
        ('NPSN', sekolah.get('npsn', '-')),
        ('Nama Sekolah', sekolah.get('nama', '-')),
        ('Status', sekolah.get('statusSatuanPendidikan', sekolah.get('status', '-'))),
        ('Jenjang', sekolah.get('bentukPendidikan', sekolah.get('jenjang', '-'))),
        ('Akreditasi', sekolah.get('akreditasi', '-')),
        ('Alamat Jalan', alamat_str),
        ('RT', rt),
        ('RW', rw),
        ('Dusun', dusun),
        ('Desa/Kelurahan', desa),
        ('Kecamatan', kecamatan),
        ('Kabupaten/Kota', kabupaten),
        ('Provinsi', provinsi),
        ('Kode Pos', kode_pos),
        ('Kode Wilayah', kode_wilayah if 'kode_wilayah' in locals() else '-'),
        ('Telepon', sekolah.get('nomorTelepon', sekolah.get('telepon', '-'))),
        ('Email', sekolah.get('email', '-')),
        ('Website', sekolah.get('website', '-')),
        ('Latitude', sekolah.get('lintang', sekolah.get('latitude', '-'))),
        ('Longitude', sekolah.get('bujur', sekolah.get('longitude', '-'))),
    ]
    for label, value in fields_umum:
        if value and value != '-':
            table_umum.add_row(label, str(value))
    console.print(table_umum)
    
    # Statistik
    stats = extract_statistics(data)
    if stats:
        table_stats = Table(box=box.ROUNDED, border_style='green', title="[bold green]STATISTIK[/bold green]")
        table_stats.add_column("Item", style="bold green")
        table_stats.add_column("Jumlah", style="white")
        mapping = {
            'jumlah_siswa': 'Total Siswa',
            'jumlah_siswa_l': 'Siswa Laki-laki',
            'jumlah_siswa_p': 'Siswa Perempuan',
            'jumlah_guru': 'Total Guru',
            'jumlah_guru_l': 'Guru Laki-laki',
            'jumlah_guru_p': 'Guru Perempuan',
            'jumlah_rombel': 'Rombel (Rombongan Belajar)',
            'rasio_siswa_guru': 'Rasio Siswa/Guru',
        }
        for key, label in mapping.items():
            if key in stats:
                val = stats[key]
                if key == 'rasio_siswa_guru':
                    val = f"{val:.1f}" if isinstance(val, float) else str(val)
                table_stats.add_row(label, str(val))
        console.print(table_stats)
    
    # Yayasan
    if isinstance(sekolah, dict) and 'yayasan' in sekolah:
        yayasan = sekolah['yayasan']
        if yayasan and yayasan.get('nama'):
            console.print(f"[bold yellow]Yayasan:[/bold yellow] {yayasan.get('nama', '-')}")
            if yayasan.get('alamat'):
                console.print(f"   Alamat Yayasan: {yayasan.get('alamat', '-')}")
    
    # Update terakhir
    if meta and meta.get('lastUpdatedAt'):
        console.print(f"[dim]Terakhir Update: {meta['lastUpdatedAt']}[/dim]")
    elif isinstance(sekolah, dict) and sekolah.get('updated_at'):
        console.print(f"[dim]Terakhir Update: {sekolah['updated_at']}[/dim]")

# ====================== PENCARIAN ======================
def cari_sekolah(npsn):
    console.print(f"[bold cyan]Mencari data NPSN: {npsn}[/bold cyan]")
    results = []
    
    try:
        url = API_FAZRIANSYAH.format(npsn=npsn)
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('data'):
                results.append(('denz', data['data']))
    except:
        pass
    
    try:
        url = API_IKSAN.format(npsn=npsn)
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success') and data.get('data'):
                results.append(('denz', data['data']))
    except:
        pass
    
    try:
        url = API_KEMENDIKBUD.format(npsn=npsn)
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('data'):
                results.append(('denz', data['data']))
    except:
        pass
    
    if not results:
        console.print(f"[bold red]Data tidak ditemukan untuk NPSN: {npsn}[/bold red]")
        return None
    
    for source, data in results:
        console.print(f"\n[bold green]Source: {source}[/bold green]")
        console.print("-" * 60)
        tampilkan_data(data, source)
        console.print("=" * 60)
    return results

# ====================== BATCH ======================
def batch_from_file(filename):
    try:
        with open(filename, 'r') as f:
            npsns = [line.strip() for line in f if line.strip()]
        console.print(f"[bold cyan]Memproses {len(npsns)} NPSN dari {filename}[/bold cyan]")
        results = {}
        for npsn in npsns:
            console.print(f"\n[bold yellow]--- NPSN: {npsn} ---[/bold yellow]")
            res = cari_sekolah(npsn)
            if res:
                results[npsn] = res
            time.sleep(0.5)
        with open('hasil_npsn.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"\n[bold green]Hasil disimpan ke hasil_npsn.json[/bold green]")
        return results
    except FileNotFoundError:
        console.print(f"[bold red]File {filename} tidak ditemukan.[/bold red]")
        return None

# ====================== MAIN ======================
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(banner())
    
    menu_table = Table(box=box.DOUBLE_EDGE, show_header=False, expand=True)
    menu_table.add_column("No", justify="center", style="bold cyan", width=4)
    menu_table.add_column("Menu", justify="left", style="white")
    
    menu_table.add_row("01", "[bold white]Cari Satu NPSN[/bold white]")
    menu_table.add_row("02", "[bold white]Batch dari File[/bold white]")
    menu_table.add_row("00", "[bold red]Keluar[/bold red]")
    
    console.print(Panel(menu_table, title="[bold blue]OSINT SEKOLAH v1.0[/bold blue]", border_style="blue"))
    
    choice = input("\n[bold cyan]Pilih [01-02/00]: [/bold cyan]").strip()
    
    if choice in ('01', '1'):
        while True:
            npsn = input("Masukkan NPSN (8 digit): ").strip()
            if not npsn or len(npsn) != 8 or not npsn.isdigit():
                console.print("[bold red]NPSN harus 8 digit angka.[/bold red]")
                continue
            loading_animation("Mengecek database...", 2)
            cari_sekolah(npsn)
            
            while True:
                lanjut = input("\n[bold cyan]Cari lagi? (y/n): [/bold cyan]").strip().lower()
                if lanjut in ('y', 'n'):
                    break
                console.print("[bold red]Masukkan 'y' atau 'n'.[/bold red]")
            if lanjut == 'n':
                console.print("[bold yellow]Keluar...[/bold yellow]")
                sys.exit(0)
    
    elif choice in ('02', '2'):
        filename = input("Masukkan nama file (contoh: npsn_list.txt): ").strip()
        if not filename:
            console.print("[bold red]Nama file tidak boleh kosong.[/bold red]")
            return
        batch_from_file(filename)
        input("\n[dim]Tekan Enter untuk kembali...[/dim]")
    
    elif choice in ('00', '0'):
        console.print("[bold yellow]Keluar...[/bold yellow]")
        sys.exit(0)
    else:
        console.print("[bold red]Pilihan tidak valid.[/bold red]")
        time.sleep(1)

def leaktol():
    try:
        while True:
            main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Force Exit.[/bold red]")
        sys.exit(0)
