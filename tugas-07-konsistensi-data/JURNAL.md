# Jurnal Proses — Tugas 7

## Diskusi pemilihan model konsistensi
- Argumen yang dipertimbangkan:
  1. Karakteristik data: Saldo *e-wallet* adalah data finansial bernilai riil yang bersifat sangat sensitif terhadap inkonsistensi. Ketidaksamaan data antar replika dapat menyebabkan *double spending* (saldo dipakai dua kali di replika berbeda) atau *false rejection* (pesanan ditolak padahal pengguna sudah membayar top-up).
  2. Batasan Eventual Consistency: Pada Eventual Consistency, ada *replication window* di mana replika Bandung tertinggal beberapa detik dari Jakarta. Jika pengguna langsung bertransaksi di Bandung sesaat setelah top-up di Jakarta, data yang dibaca adalah data basi (*stale read*). Hal ini merusak *user trust* dan memicu lonjakan komplain ke CS.
  3. Konsekuensi Sequential Consistency global: Menuntut sinkronisasi sekuensial penuh pada seluruh operasi lintas data center (Jakarta-Bandung) via konsensus terdistribusi (seperti Raft/2PC) akan menyebabkan lonjakan latensi jaringan dan menurunkan ketersediaan (*availability*) saat terjadi gangguan jaringan (prinsip CAP Theorem).
- Kesimpulan akhir & alasan:
  Eventual Consistency murni tidak dapat digunakan untuk sistem finansial FoodGo. Namun, menerapkan Sequential Consistency global murni juga tidak efisien dari segi performa. Oleh karena itu, pendekatan terbaik adalah **Client-Centric Consistency**, khususnya model **Read-Your-Writes (RYW)** yang dipadukan dengan **Monotonic Reads**. Dengan melacak nomor versi pembaruan (*version token*) pada sisi klien, sistem memastikan pengguna selalu membaca versi datanya sendiri yang paling mutakhir, sementara replikasi antar server di latar belakang tetap dapat berjalan secara asinkron dan efisien.

## Simulasi (jika dikerjakan)
- Hasil skenario naif vs Read-Your-Writes:
  1. Pada skenario naif (tanpa RYW), ketika pengguna melakukan top-up sebesar 50.000 di server Jakarta dan langsung membaca saldo dari server Bandung 0.5 detik kemudian, saldo yang terbaca masih bernilai 0.0 karena replikasi tertunda 2.0 detik. Kondisi ini merepresentasikan *bug inconsistent read* yang menyebabkan pesanan ditolak.
  2. Pada skenario Read-Your-Writes, pengguna melakukan penambahan saldo 20.000 (total saldo 70.000, versi 2). Saat pengguna meminta saldo dari Bandung dengan membawa parameter `versi_minimal = 2`, replika Bandung mendeteksi bahwa versinya masih tertinggal (`versi 1 < versi minimal 2`). Melalui mekanisme RYW, pembacaan dialihkan (*redirect*) ke server Jakarta yang memegang versi terbaru, sehingga saldo yang diperoleh tepat sebesar 70.000. Transaksi berhasil dieksekusi secara mulus tanpa kegagalan.

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 15 November 2026 | ChatGPT / Claude | Bagaimana membandingkan trade-off antara Data-Centric (Sequential, Eventual) dan Client-Centric Consistency (Read-Your-Writes) pada arsitektur e-wallet multi-region? | AI menjelaskan definisi teoritis CAP theorem, bahaya stale read pada e-wallet, dan konsep token versioning untuk Read-Your-Writes. | Kami mengontekstualisasikan saran tersebut ke dalam kasus spesifik FoodGo Jakarta-Bandung, menyusun analisis dampak bisnis nyata (false rejection, customer churn), membuat sequence diagram Mermaid alur transaksi, serta mengimplementasikan dan menguji simulasi pada `replica_simulation.py`. |
