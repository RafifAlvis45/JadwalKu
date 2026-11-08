import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

with open("jadwal.json", encoding="utf-8") as f:
    jadwal = json.load(f)

root = tk.Tk()
root.title("JadwalKu")
root.geometry("500x400")

label = tk.Label(root, font=("Segoe UI", 20))
label.pack(pady=20)

tabel = ttk.Treeview(root, columns=("Mulai", "Selesai", "Mapel"), show="headings", height=8)
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


def perbarui_jam():
    sekarang = datetime.now()
    nama_hari = HARI [sekarang.weekday()]
    label.config(text=f"{nama_hari}, {sekarang:%H:%M:%S}")
    root.after(1000, perbarui_jam)

perbarui_jam()
isi_tabel()
root.mainloop()