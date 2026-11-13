# Nexora Automated Intelligence & AutoCache Protocol (Always Active)

Aturan operasional ini SELALU AKTIF secara otomatis untuk seluruh pekerjaan dalam direktori dan subdirektori repositori ini.

---

## 1. Automatic Skill Activation
1. Pada setiap giliran (turn), perintah, atau sesi kerja, agent WAJIB otomatis beroperasi di bawah protokol `nexora-advanced-intelligence` (`.agents/skills/nexora-advanced-intelligence/SKILL.md` atau `nexora-advanced-intelligence/SKILL.md`).
2. Agent tidak boleh menunggu pengguna meminta aktivasi secara manual.
3. Pilih mode berpikir adaptif yang tepat (`FAST`, `BALANCED`, `DEEP`, `EXPERT`, `CRITICAL`, `DEBUG`, `ARCHITECT`, `RESEARCH`, `AUTONOMOUS`, `RECOVERY`) berdasarkan kompleksitas tugas.
4. Ikuti 9 Quality Gates (`GATE 1: Audit` hingga `GATE 9: Final Verification`).

---

## 2. Automatic Project Cache Protocol (AutoCache)
Agent wajib mengeksekusi siklus hidup cache berbasis file `.nexora/cache/` secara otomatis:

### A. Pre-Flight (Otomatis saat Turn Dimulai)
1. Periksa ketersediaan folder `.nexora/cache/`.
2. Jika ada, otomatis baca:
   - `CACHE_INDEX.json`
   - `PROJECT_STATE.json`
   - `SESSION_HANDOFF.json`
3. Bandingkan `FILE_FINGERPRINTS.json` dengan kondisi aktual file di workspace (deteksi modifikasi eksternal).
4. Jika repositori berubah sejak sesi terakhir, perbarui cache yang terpengaruh dan lanjutkan dari status terakhir tanpa memindai ulang seluruh codebase.
5. Jika `.nexora/cache/` belum ada, inisialisasi direktori dan buat snapshot awal.

### B. In-Flight (Selama Pengerjaan)
1. Jalankan pembacaan bertahap (incremental reading). Baca hanya file yang relevan dengan tugas.
2. Terapkan ambang batas compacting konteks kebijakan (50%, 65%, 75%, 85%, 95%) untuk menghemat token dan menjaga ketepatan penalaran.
3. Catat keputusan arsitektur baru ke `.nexora/cache/DECISION_CACHE.json`.

### C. Post-Flight (Otomatis setelah Modifikasi / Pengujian / Penyelesaian Tugas)
Setiap kali agent selesai melakukan perubahan file, menjalankan tes, atau menyelesaikan langkah kerja:
1. Hitung ulang fingerprint file yang dimodifikasi dan perbarui `.nexora/cache/FILE_FINGERPRINTS.json`.
2. Perbarui ringkasan kemajuan di `.nexora/cache/PROJECT_STATE.json`.
3. Tulis ringkasan hasil pengujian ke `.nexora/cache/TEST_CACHE.json`.
4. Jika membuat file pengujian sementara, jalankan Auto Test Cleanup sebelum memperbarui cache.
5. Perbarui status handoff di `.nexora/cache/SESSION_HANDOFF.json` (completed tasks, pending tasks, modified files, next recommended action).
6. Perbarui metadata dan timestamp di `.nexora/cache/CACHE_INDEX.json`.
7. Jangan pernah menyimpan password, API key, token, kredensial, atau rahasia ke dalam cache.

---

## 3. Auto Test Cleanup Invariant
- Setiap kali pengujian dijalankan, bersihkan semua temporary test files (Kategori A) dan test artifacts (Kategori B) secara otomatis.
- Lindungi seluruh existing test suite (Kategori C) dan permanent test infrastructure (Kategori D).
- Laporkan status pengujian dan status pembersihan test secara jujur.
