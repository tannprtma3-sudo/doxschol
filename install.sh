#!/usr/bin/env bash

# Color
g="\033[1;32m"
r="\033[1;31m"
b="\033[1;34m"
w="\033[0m"
null="> /dev/null 2>&1"

echo -e "${b}========================================${w}"
echo -e "${b}   GHOST-CRACK TOOL INSTALLER${w}"
echo -e "${b}========================================${w}"

# Pilih platform
echo -e "${b}[1]${w} Install untuk ${g}Termux${w} (Android)"
echo -e "${b}[2]${w} Install untuk ${g}Linux${w} (Debian/Ubuntu)"
echo -ne "${b}>> Pilih [1/2]: ${w}"
read -r platform

case $platform in
  1)
    echo -e "${b}>>${w} Memulai instalasi untuk ${g}Termux${w}"
    sleep 1
    # ─── TERMUX INSTALL ───
    echo -e "${b}>>${w} Mengupdate package..."
    pkg update -y $null
    pkg upgrade -y $null

    echo -e "${b}>>${w} Installing: ${g}wget${w}"
    pkg install wget -y $null

    echo -e "${b}>>${w} Installing: ${g}curl${w}"
    pkg install curl -y $null

    echo -e "${b}>>${w} Installing: ${g}apktool${w}"
    git clone https://github.com/Lexiie/Termux-Apktool 2>/dev/null
    cd Termux-Apktool
    dpkg -i apktool_2.3.4_all.deb $null
    cd ..
    pkg install apktool -y $null

    echo -e "${b}>>${w} Installing: ${g}imagemagick${w}"
    pkg install imagemagick -y $null

    echo -e "${b}>>${w} Installing: ${g}java${w}"
    wget -q https://raw.githubusercontent.com/popeye0013/Exploit/main/installjava -O installjava
    bash installjava $null

    echo -e "${b}>>${w} Installing: ${g}python3${w}"
    pkg install python3 -y $null

    echo -e "${b}>>${w} Installing modules: ${g}pillow${w}"
    pip3 install Pillow $null

    echo -e "${b}>>${w} Installing: ${g}flask${w}"
    pip3 install flask $null

    echo -e "${b}>>${w} Installing: ${g}dnspython${w}"
    pip install dnspython $null

    echo -e "${b}>>${w} Installing: ${g}python-whois${w}"
    pip3 install python-whois $null

    echo -e "${b}>>${w} Installing: ${g}aiohttp${w}"
    pip install aiohttp $null

    echo -e "${b}>>${w} Installing: ${g}beautifulsoup4${w}"
    pip install beautifulsoup4 $null

    echo -e "${b}>>${w} Installing: ${g}x11-repo${w}"
    pkg install x11-repo -y $null

    echo -e "${b}>>${w} Installing: ${g}chromium${w}"
    pkg install chromium -y $null

    echo -e "${b}>>${w} Installing: ${g}nodejs${w}"
    pkg install nodejs -y $null

    echo -e "${b}>>${w} Installing: ${g}cryptography${w}"
    pip install cryptography pycryptodome $null

    echo -e "${b}>>${w} Installing: ${g}phonenumbers${w}"
    pip install phonenumbers $null

    echo -e "${b}>>${w} Installing: ${g}colorama${w}"
    pip install colorama $null

    echo -e "${b}>>${w} Installing: ${g}pyrogram${w}"
    pip install pyrogram $null

    echo -e "${b}>>${w} Installing: ${g}telethon${w}"
    pip install telethon $null

    echo -e "${b}>>${w} ${g}✅ Instalasi selesai!${w}"
    echo -e "${b}>>${w} Jalankan dengan: ${g}python3 ghost-track.py${w}"
    ;;

  2)
    echo -e "${b}>>${w} Memulai instalasi untuk ${g}Linux (Debian/Ubuntu)${w}"
    sleep 1

    # Cek apakah apt tersedia
    if ! command -v apt &> /dev/null; then
      echo -e "${r}❌ Sistem tidak mendukung apt (bukan Debian/Ubuntu).${w}"
      echo -e "${r}   Script ini hanya untuk distro berbasis Debian.${w}"
      exit 1
    fi

    echo -e "${b}>>${w} Mengupdate package..."
    sudo apt update -y $null
    sudo apt upgrade -y $null

    echo -e "${b}>>${w} Installing: ${g}wget${w}"
    sudo apt install wget -y $null

    echo -e "${b}>>${w} Installing: ${g}curl${w}"
    sudo apt install curl -y $null

    echo -e "${b}>>${w} Installing: ${g}git${w}"
    sudo apt install git -y $null

    echo -e "${b}>>${w} Installing: ${g}python3${w}"
    sudo apt install python3 python3-pip -y $null

    echo -e "${b}>>${w} Installing: ${g}apktool${w}"
    sudo apt install apktool -y $null

    echo -e "${b}>>${w} Installing: ${g}imagemagick${w}"
    sudo apt install imagemagick -y $null

    echo -e "${b}>>${w} Installing: ${g}default-jre${w} (Java)"
    sudo apt install default-jre -y $null

    echo -e "${b}>>${w} Installing: ${g}chromium-browser${w}"
    sudo apt install chromium-browser -y $null

    echo -e "${b}>>${w} Installing: ${g}nodejs${w}"
    sudo apt install nodejs npm -y $null

    echo -e "${b}>>${w} Installing modules: ${g}pillow${w}"
    pip3 install Pillow $null

    echo -e "${b}>>${w} Installing: ${g}flask${w}"
    pip3 install flask $null

    echo -e "${b}>>${w} Installing: ${g}dnspython${w}"
    pip3 install dnspython $null

    echo -e "${b}>>${w} Installing: ${g}python-whois${w}"
    pip3 install python-whois $null

    echo -e "${b}>>${w} Installing: ${g}aiohttp${w}"
    pip3 install aiohttp $null

    echo -e "${b}>>${w} Installing: ${g}beautifulsoup4${w}"
    pip3 install beautifulsoup4 $null

    echo -e "${b}>>${w} Installing: ${g}cryptography${w}"
    pip3 install cryptography pycryptodome $null

    echo -e "${b}>>${w} Installing: ${g}phonenumbers${w}"
    pip3 install phonenumbers $null

    echo -e "${b}>>${w} Installing: ${g}colorama${w}"
    pip3 install colorama $null

    echo -e "${b}>>${w} Installing: ${g}pyrogram${w}"
    pip3 install pyrogram $null

    echo -e "${b}>>${w} Installing: ${g}telethon${w}"
    pip3 install telethon $null

    echo -e "${b}>>${w} ${g}✅ Instalasi selesai!${w}"
    echo -e "${b}>>${w} Jalankan dengan: ${g}python3 ghost-track.py${w}"
    ;;

  *)
    echo -e "${r}❌ Pilihan tidak valid. Keluar.${w}"
    exit 1
    ;;
esac