"""
Tugas 7 (opsional) - Simulasi Replikasi Dua Server (Jakarta & Bandung)

Mensimulasikan delay replikasi dan masalah inconsistent read,
lalu memperbaikinya dengan mekanisme Read-Your-Writes sederhana.
"""

import time
import threading

REPLICATION_DELAY = 2.0  # detik, simulasi lambatnya sinkronisasi antar server


class Replica:
    def __init__(self, name: str):
        self.name = name
        self.saldo: dict[str, float] = {}
        self.last_write_version: dict[str, int] = {}

    def write(self, user_id: str, saldo_baru: float, version: int):
        self.saldo[user_id] = saldo_baru
        self.last_write_version[user_id] = version
        print(f"[{self.name}] WRITE saldo {user_id} = {saldo_baru} (versi {version})")

    def read(self, user_id: str) -> float:
        return self.saldo.get(user_id, 0.0)


class ReplicationSystem:
    def __init__(self):
        self.jakarta = Replica("Jakarta")
        self.bandung = Replica("Bandung")
        self.version_counter = 0

    def top_up(self, user_id: str, jumlah: float):
        """Top-up selalu ditulis dulu ke server Jakarta (mis. server terdekat pelanggan)."""
        self.version_counter += 1
        version = self.version_counter
        saldo_baru = self.jakarta.read(user_id) + jumlah
        self.jakarta.write(user_id, saldo_baru, version)

        # TODO 1: replikasi ke Bandung TERTUNDA (simulasikan dengan
        # threading.Timer(REPLICATION_DELAY, ...) yang memanggil
        # self.bandung.write(user_id, saldo_baru, version) setelah delay.
        timer = threading.Timer(
            REPLICATION_DELAY,
            self.bandung.write,
            args=(user_id, saldo_baru, version),
        )
        timer.daemon = True
        timer.start()
        print(f"[SISTEM] Replikasi ke Bandung dijadwalkan (delay {REPLICATION_DELAY} detik)...")

    def baca_saldo_naif(self, user_id: str, server: str) -> float:
        """Baca saldo TANPA mekanisme Read-Your-Writes - bisa saja stale."""
        replica = self.jakarta if server == "Jakarta" else self.bandung
        return replica.read(user_id)

    def baca_saldo_read_your_writes(self, user_id: str, server: str, versi_minimal: int, mode: str = "redirect") -> float:
        """TODO 2: implementasikan Read-Your-Writes -
        jika replika yang dituju versi datanya < versi_minimal (client pernah
        melihat versi lebih baru sebelumnya), tunggu/redirect ke replika yang
        sudah punya versi tersebut (di sini cukup simulasikan dengan polling
        sampai versi replika >= versi_minimal, atau redirect ke Jakarta)."""
        target = self.jakarta if server == "Jakarta" else self.bandung
        versi_sekarang = target.last_write_version.get(user_id, 0)

        if versi_sekarang < versi_minimal:
            print(f"[{target.name}] STALE DETECTED: versi server ({versi_sekarang}) < versi minimal klien ({versi_minimal})")
            if mode == "redirect":
                print(f"[{target.name}] Solusi RYW (Redirect): Mengalihkan pembacaan ke server Jakarta yang sudah konsisten...")
                return self.jakarta.read(user_id)
            elif mode == "wait":
                print(f"[{target.name}] Solusi RYW (Wait/Catch-up): Menunggu proses replikasi selesai...")
                while target.last_write_version.get(user_id, 0) < versi_minimal:
                    time.sleep(0.1)
                print(f"[{target.name}] Replikasi selesai, data telah mutakhir.")
                return target.read(user_id)

        return target.read(user_id)


def main():
    system = ReplicationSystem()
    user_id = "user1"

    print("=== Skenario NAIF (tanpa Read-Your-Writes) ===")
    system.top_up(user_id, 50000)
    time.sleep(0.5)  # pelanggan langsung pesan makanan < REPLICATION_DELAY detik kemudian
    print("Baca saldo dari Bandung (naif):", system.baca_saldo_naif(user_id, "Bandung"))
    print("-> Harusnya 50000, tapi karena delay replikasi, hasilnya bisa 0 (BUG)")

    time.sleep(REPLICATION_DELAY + 0.5)

    print("\n=== Skenario dengan Read-Your-Writes ===")
    system.top_up(user_id, 20000)
    versi_terakhir = system.version_counter
    # TODO 3: panggil baca_saldo_read_your_writes dan tunjukkan hasilnya SELALU benar
    # walau dipanggil segera setelah top_up (< REPLICATION_DELAY detik).
    time.sleep(0.5)  # Pelanggan langsung memesan makanan < REPLICATION_DELAY detik kemudian
    print(f"[Client] Mengirim request baca saldo ke Bandung dengan versi_minimal = {versi_terakhir}...")
    saldo_terbaca = system.baca_saldo_read_your_writes(user_id, "Bandung", versi_terakhir, mode="redirect")
    print(f"Baca saldo dari Bandung (RYW): {saldo_terbaca}")
    print(f"-> Berhasil! Saldo konsisten ({saldo_terbaca}), transaksi sukses diproses.")

    # Menunggu replikasi ke Bandung selesai agar background timer tidak tertinggal
    time.sleep(REPLICATION_DELAY + 0.5)


if __name__ == "__main__":
    main()
