import json
import threading
import urllib.parse
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

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

MENIT_SEBELUM = config.get("menit_sebelum", 5)

# mencatat pengingat yang sudah terkirim agar tidak dikirim berulang
sudah_dikirim = set()

def telegram_siap():
    return bool(TOKEN and CHAT_ID)


def catat_log(status, teks):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ringkas = teks.replace("\n", " | ")
    with open("riwayat_kirim.log", "a", encoding="utf-8") as f:
        f.write(f"{waktu} [{status}] {ringkas}\n")


def kirim_telegram(teks):
    if not telegram_siap():
        return

    def kerja():
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": teks}).encode()
            urllib.request.urlopen(url, data=data, timeout=10)
            catat_log("BERHASIL", teks)
        except Exception as e:
            catat_log("GAGAL", teks)
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
tabel.tag_configure("sekarang", background="#c8f0c8")

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


def cek_pengingat(sekarang):
    for p in pelajaran_hari_ini():
        jam, menit = map(int, p["mulai"].split(":"))
        waktu_mulai = sekarang.replace(hour=jam, minute=menit, second=0, microsecond=0)
        selisih = waktu_mulai - sekarang
        kunci = (sekarang.date(), p["mulai"], p["mapel"])
        if timedelta(0) < selisih <= timedelta(minutes=MENIT_SEBELUM) and kunci not in sudah_dikirim:
            sudah_dikirim.add(kunci)
            kirim_telegram(
                f"Pengingat: {p['mapel']} dimulai pukul {p['mulai']} "
                f"({int(selisih.total_seconds() // 60) + 1} menit lagi)"
            )


def sorot_pelajaran(sekarang):
    jam_sekarang = sekarang.strftime("%H:%M")
    for iid in tabel.get_children():
        mulai, selesai, _ = tabel.item(iid, "values")
        aktif = mulai <= jam_sekarang < selesai
        tabel.item(iid, tags=("sekarang",) if aktif else ())


def pelajaran_berikutnya(sekarang):
    for p in pelajaran_hari_ini():
        jam, menit = map(int, p["mulai"].split(":"))
        waktu_mulai = sekarang.replace(hour=jam, minute=menit, second=0, microsecond=0)
        if waktu_mulai > sekarang:
            return p, waktu_mulai - sekarang
    return None, None


def perbarui_info(sekarang):
    p, selisih = pelajaran_berikutnya(sekarang)
    if p is None:
        info.config(text="Tidak ada pelajaran berikutnya hari ini")
        return
    menit = int(selisih.total_seconds() // 60) + 1
    if menit >= 60:
        sisa = f"{menit // 60} jam {menit % 60} menit lagi"
    else:
        sisa = f"{menit} menit lagi"
    info.config(text=f"Berikutnya: {p['mapel']} pukul {p['mulai']} ({sisa})")


def perbarui_jam():
    sekarang = datetime.now()
    nama_hari = HARI [sekarang.weekday()]
    label.config(text=f"{nama_hari}, {sekarang:%H:%M:%S}")
    cek_pengingat(sekarang)
    sorot_pelajaran(sekarang)
    perbarui_info(sekarang)
    root.after(1000, perbarui_jam)

tombol = tk.Button(root, text="Kirim Jadwal ke Telegram", command=kirim_jadwal_manual)
tombol.pack(pady=8)

status = tk.Label(root, font=("Segoe UI", 9), fg="gray")
status.pack()

if telegram_siap():
    status.config(text="Telegram aktif")
else:
    status.config(text="Telegram belum diatur (lihat config.json)")

info = tk.Label(root, font=("Segoe UI", 10))
info.pack(pady=4)

perbarui_jam()
isi_tabel()
root.mainloop()