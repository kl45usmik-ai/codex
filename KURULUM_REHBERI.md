# CODEX Kurulum Rehberi (Türkçe)

Bu rehber CODEX'i **Termux (Android)**, **Linux** ve **Windows** üzerinde kurmanızı anlatır. İngilizce rehber için: [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## Başlamadan önce

Her platform için şunlar gerekir:

- **Python 3.10 veya üzeri**
- **git** (`/commit` komutu için gerekli, isteğe bağlı)
- **Gemini API anahtarı**: [Google AI Studio](https://aistudio.google.com/apikey) üzerinden ücretsiz alabilirsiniz.

Depoyu klonlamak için:

```bash
git clone https://github.com/kl45usmik-ai/codex.git
cd codex
```

> `kl45usmik-ai` kısmını kendi GitHub kullanıcı adınızla değiştirin.

---

## 1. Termux (Android)

### Kurulum

1. Termux'u F-Droid'den kurun (Play Store sürümü güncel değil).
2. Termux'ta gerekli paketleri kurun:

   ```bash
   pkg update && pkg upgrade
   pkg install python git
   ```

3. Depoyu klonlayın ve kurulum scriptini çalıştırın:

   ```bash
   git clone https://github.com/kl45usmik-ai/codex.git
   cd codex
   bash install.sh
   ```

4. Kurulum bittiğinde `codex`, `Codex` ve `CODEX` komutları oluşur. Termux'ta bu klasör zaten PATH'te olduğu için ek bir ayar gerekmez.

### Kayıt klasörü için depolama izni

Kodların telefonunuzda `Codex` klasörüne kaydedilmesi için bir kez şunu çalıştırın:

```bash
termux-setup-storage
```

Açılan izin penceresinde **İzin ver**'e dokunun. Kayıtlar `/storage/emulated/0/Codex` klasörüne gider.

### İlk açılış

```bash
codex
```

Program iki soru sorar:

- Dil: `2` (English) ya da `1` (Türkçe)
- Ortam: `3` (Termux)

Ardından API anahtarınızı girin:

```
/key
```

Anahtar gizli girilir ve sadece sizin cihazınızda saklanır.

---

## 2. Linux

Bu rehber Ubuntu, Debian, Fedora, Arch ve benzeri dağıtımlar içindir. macOS için de benzerdir.

### Kurulum

1. Python ve git'in kurulu olduğunu kontrol edin:

   ```bash
   python3 --version
   git --version
   ```

   Yoksa dağıtımınıza göre kurun, örneğin Ubuntu/Debian için `sudo apt install python3 python3-pip git`.

2. Depoyu klonlayın ve kurulum scriptini çalıştırın:

   ```bash
   git clone https://github.com/kl45usmik-ai/codex.git
   cd codex
   bash install.sh
   ```

3. Komutlar `~/.local/bin` klasörüne kurulur. Bu klasör PATH'te değilse script size eklenmesi gereken satırı gösterir. Örneğin `~/.bashrc` dosyasının sonuna şunu ekleyin:

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

   Sonra yeni bir terminal açın ya da `source ~/.bashrc` çalıştırın.

### Python paketleri hakkında

Program ilk açılışta `google-genai` paketini kendisi kurar. Yeni Debian/Ubuntu sürümleri sistem Python'una doğrudan paket kurulmasını engelleyebilir. Program bunu otomatik olarak `--break-system-packages` ile tekrar dener. Yine de sorun yaşarsanız:

```bash
python3 -m venv ~/codex-venv
source ~/codex-venv/bin/activate
pip install google-genai
```

Sonra `codex` komutunu yeni ortamda çalıştırın.

### İlk açılış

```bash
codex
```

- Dil: `1` (Türkçe) ya da `2` (English)
- Ortam: `2` (Linux / macOS)

Ardından `/key` ile API anahtarınızı girin.

---

## 3. Windows

### Kurulum

1. **Python'u kurun:** [python.org/downloads](https://www.python.org/downloads/) adresinden Python 3'ü indirin.
   **Kurulum ekranında "Add python.exe to PATH" seçeneğini mutlaka işaretleyin.**

2. **git'i kurun (isteğe bağlı):** [git-scm.com](https://git-scm.com/download/win). `/commit` komutu için gerekir.

3. Depoyu klonlayın. PowerShell veya Komut İstemi'nde:

   ```powershell
   git clone https://github.com/kl45usmik-ai/codex.git
   cd codex
   ```

   Git kurmadıysanız GitHub sayfasından **Code → Download ZIP** ile indirip klasörü açabilirsiniz.

4. Kurulum scriptini çalıştırın. Klasördeki **`install.bat`** dosyasına çift tıklayın ya da cmd'de:

   ```
   install.bat
   ```

5. Script `codex.cmd` dosyasını `%LOCALAPPDATA%\Codex\bin` klasörüne kurar. Klasör PATH'te değilse ekranda bir PowerShell komutu gösterilir. Bunu **bir kez** çalıştırın:

   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:LOCALAPPDATA\Codex\bin", "User")
   ```

   Sonra yeni bir cmd ya da PowerShell penceresi açın.

### İlk açılış

Yeni bir pencerede:

```
codex
```

- Dil: `1` (Türkçe) ya da `2` (English)
- Ortam: `1` (Windows)

Ardından `/key` ile API anahtarınızı girin.

> Windows büyük/küçük harfe duyarsız olduğu için `codex`, `Codex` ve `CODEX` aynı komutu açar.

---

## İlk kullanım

Kurulum ve anahtar girişinden sonra deneyin:

```
bir not defteri uygulaması yap
```

Model kodu yazar ve sözdizimini kontrol eder. Kaydetmek isteyip istemediğinizi sorar. Her kod için sorulmasın istiyorsanız:

```
/settings otomatik ac
```

Yardım:

- `/cmds`: tüm komutlar
- `/help /komut`: bir komutun ayrıntısı, örneğin `/help /edit`

Sık kullanılanlar:

| Komut | Ne işe yarar |
|---|---|
| `/edit dosya.py` | Dosyayı modelle değiştirir, farkı gösterir, onayla yazar |
| `/run python dosya.py` | Komutu çalıştırır ve sonucu modele iletir |
| `/fix` | Son hatayı modele düzelttirir |
| `/model` | Gemini modellerini listeler, `/model <ad>` ile seçer |
| `/settings` | Dil, renk ve otomatik kayıt ayarları |

---

## Sorun giderme

**`codex: command not found` (Linux/Termux)**
Kurulum scriptini çalıştırdınız mı? `ls ~/.local/bin` (Linux) ya da `ls $PREFIX/bin/codex` (Termux) ile dosyaların oluştuğunu kontrol edin. Linux'ta `~/.local/bin` PATH'te olmalı.

**`'codex' is not recognized` (Windows)**
Yeni bir pencere açtınız mı? PATH değişikliği yalnızca yeni pencerelerde geçerli olur. Yine olmuyorsa PowerShell komutunu tekrar çalıştırıp kontrol edin.

**Python bulunamadı (Windows)**
Python'u kurarken "Add python.exe to PATH" işaretli miydi? Değilse Python'u kaldırıp yeniden kurun.

**Kodlar kaydedilmiyor (Termux)**
`termux-setup-storage` komutunu çalıştırdınız mı? Depolama izni olmadan `Codex` klasörü oluşturulamaz.

**API hatası veya "tüm modellerin limiti dolu"**
Ücretsiz Gemini kotası sınırlıdır. Birkaç dakika bekleyin ya da `/model` ile başka bir model seçin. Anahtarı yeniden girmek için `/key`.

**Model yanıt vermiyor**
Program her isteği 30 saniye bekler, sonra sonraki modele geçer. Ayarı `main.py` içindeki `REQUEST_TIMEOUT` ile değiştirebilirsiniz.

**Dil ya da ortamı yanlış seçtim**
`~/.codex_config.json` dosyasındaki `language` (`tr` / `en`) ve `platform` (`windows` / `linux` / `termux`) alanlarını düzenleyin. Dosya yoksa program ilk açılışta sorar.

**`/key` girişi çalışmıyor**
Girdiğiniz karakterler ekranda görünmez, bu normaldir. Yapıştırdıktan sonra Enter'a basın.

---

## Kaldırma

**Termux:**
```bash
rm -f "$PREFIX/bin/"{codex,Codex,CODEX}
```

**Linux / macOS:**
```bash
rm -f ~/.local/bin/{codex,Codex,CODEX}
```

**Windows:** `%LOCALAPPDATA%\Codex` klasörünü silin ve PATH'e eklediğiniz satırı kaldırın.

Ayar ve anahtar dosyasını da silmek isterseniz: `~/.codex_config.json`, `~/.codex_chats`, `~/.codex_snippets.json`.

---

## Güvenlik

- API anahtarınızı hiçbir zaman GitHub'a yüklemeyin. Anahtar `~/.codex_config.json` dosyasında (Linux/Termux'ta izin 600) tutulur.
- Depoyu paylaşmadan önce `/secrets` komutuyla kodda kalmış anahtar ya da şifre olup olmadığını kontrol edin.
