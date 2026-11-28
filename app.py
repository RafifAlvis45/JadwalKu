import json
import threading
import urllib.parse
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

with open("jadwal.json", encoding="utf-8") as f:
    jadwal = json.load(f)
try:
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

TOKEN = config.get("token", "")
CHAT_ID = config.get("chat_id", "")


def telegram_siap():
    return bool(TOKEN and CHAT_ID)

def kirim_telegram(teks):
    if not telegram_siap():
        return

    def kerja():
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": teks}).encode()
            urllib.request.urlopen(url, data=data, timeout=10)
        except Exception as e:
            print("Gagal kirim Telegram:", e)

    threading.Thread(target=kerja, daemon=True).start()

print("Telegram siap:", telegram_siap())

root = tk.Tk()
root.title("JadwalKu")
root.geometry("500x400")

label = tk.Label(root, font=("Segoe UI", 20))
label.pack(pady=20)

tabel = ttk.Treeview(root, columns=("mulai", "selesai", "mapel"), show="headings", height=8)
tabel.heading("mulai", text="Mulai")
tabel.heading("selesai", text="Selesai")
tabel.heading("mapel", text="Mata Pelajaran")
tabel.column("mulai", width=70)
tabel.column("selesai", width=70)
tabel.column("mapel", width=300)
tabel.pack(padx=14, pady=10)


def pelajaran_hari_ini():
    nama_hari = HARI[datetime.now().weekday()]
    return jadwal.get(nama_hari, [])

def isi_tabel():
    for p in pelajaran_hari_ini():
        tabel.insert("", "end", values=(p["mulai"], p["selesai"], p["mapel"]))


def teks_jadwal_hari_ini():
    nama_hari = HARI[datetime.now().weekday()]
    pelajaran = pelajaran_hari_ini()
    if not pelajaran:
        return f"Jadwal {nama_hari}: tidak ada pelajaran."
    baris = [f"Jadwal {nama_hari}"]
    for p in pelajaran:
        baris.append(f"{p['mulai']} - {p['selesai']}  {p['mapel']}")
    return "\n".join(baris)


def kirim_jadwal_manual():
    if not telegram_siap():
        messagebox.showwarning("Telegram belum diatur",
                               "Isi token dan chat_id di config.json dulu.")
        return
    kirim_telegram(teks_jadwal_hari_ini())
    messagebox.showinfo("Telegram", "Jadwal hari ini sedang dikirim ke Telegram.")

def perbarui_jam():
    sekarang = datetime.now()
    nama_hari = HARI [sekarang.weekday()]
    label.config(text=f"{nama_hari}, {sekarang:%H:%M:%S}")
    root.after(1000, perbarui_jam)

tombol = tk.Button(root, text="Kirim Jadwal ke Telegram", command=kirim_jadwal_manual)
tombol.pack(pady=8)

status = tk.Label(root, font=("Segoe UI", 9), fg="gray")
status.pack()

if telegram_siap():
    status.config(text="Telegram aktif")
else:
    status.config(text="Telegram belum diatur (lihat config.json)")

perbarui_jam()
isi_tabel()
root.mainloop()