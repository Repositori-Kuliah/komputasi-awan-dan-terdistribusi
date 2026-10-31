# Jurnal Proses — Tugas 6

## Implementasi find_successor

- Kesalahan pertama yang ditemui: Pada implementasi awal, fungsi `find_successor()` belum memiliki logika untuk mencari node penerus berdasarkan hash key. Selain itu, perlu memperhatikan kondisi ketika hash key lebih besar daripada seluruh ID node.
- Cara memperbaikinya: Mengurutkan ID node menggunakan `sorted()` dan mencari node dengan ID terkecil yang lebih besar atau sama dengan hash key. Jika tidak ditemukan, fungsi mengembalikan node dengan ID terkecil sebagai mekanisme wrap-around.

## Skenario join/leave

- Hasil sebelum node baru bergabung: Ring memiliki empat node, yaitu Jakarta-1 (177), Jakarta-2 (102), Bandung-1 (40), dan Surabaya-1 (136). Mapping kurir disimpan berdasarkan successor masing-masing.
- Hasil sesudah node baru bergabung: Node Medan (123) berhasil bergabung ke ring. Node tersebut menjadi successor untuk key yang berada pada rentang setelah node 102 sampai dengan 123.
- Hasil sebelum node keluar: Kurir-005 dengan hash 175 dan kurir-009 dengan hash 170 menjadi tanggung jawab node Jakarta-1 (177).
- Hasil sesudah node keluar: Node Jakarta-1 berhasil keluar dari ring. Mapping kurir-005 dan kurir-009 berpindah tanggung jawab ke node Bandung (40) melalui mekanisme wrap-around. Lookup kedua kurir tetap menghasilkan alamat IP yang sama.

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 31 Oktober 2026 | ChatGPT | Bagaimana cara mengimplementasikan simulasi Chord DHT dengan Python? | AI memberikan arahan tentang lookup, join, leave, dan successor | Kami mempelajari kode, menjalankan simulasi, dan memeriksa hasil pengujian |