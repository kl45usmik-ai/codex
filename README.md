> English: [README.en.md](README.en.md)

> Kurulum rehberi: [KURULUM_REHBERI.md](KURULUM_REHBERI.md) · Setup guide (English): [SETUP_GUIDE.md](SETUP_GUIDE.md)

# CODEX - AI Code Engine

Termux üzerinde çalışan, Google Gemini API ile kod yazan, düzenleyen ve çalıştıran Türkçe yapay zeka kod asistanı.

By Klaus

## Gereksinimler

- Android üzerinde [Termux](https://termux.dev)
- Python 3: `pkg install python git`
- Gemini API anahtarı: [Google AI Studio](https://aistudio.google.com/apikey)

## Kurulum

```bash
git clone https://github.com/kl45usmik-ai/codex.git
cd codex
bash install.sh
```

Kurulumdan sonra herhangi bir klasörde şunlardan birini yazmanız yeterli:

```bash
codex
Codex
CODEX
```

Linux büyük/küçük harfe duyarlıdır, bu yüzden üç yazım da ayrı ayrı kurulur.

Termux'ta `install.sh` komutu `$PREFIX/bin` içine bir `codex` komutu koyar; bu klasör zaten PATH'tedir, ek bir ayar gerekmez. Diğer Linux sistemlerinde script `~/.local/bin` kullanır ve gerekirse PATH için yapmanız gereken satırı size gösterir.

İlk açılışta API anahtarını `/key` komutuyla girin. Anahtar `~/.codex_config.json` dosyasına, yalnızca sizin okuyabileceğiniz izinle (600) kaydedilir. Ortam değişkeni olarak `GEMINI_API_KEY` da tanımlayabilirsiniz.

## İlk açılış: dil ve ortam

Programı ilk açtığınızda iki soru sorulur, yalnızca bir kez:

1. Dil: `1` Türkçe, `2` English
2. Ortam: `1` Windows, `2` Linux / macOS, `3` Termux (Android)

Seçimler `~/.codex_config.json` dosyasına kaydedilir ve bir daha sorulmaz. Ortam seçimi HTML açma komutunu, kayıt klasörünü ve komut çalıştırmayı etkiler. Daha sonra dili ve ortamı değiştirmek için config dosyasındaki `language` ve `platform` alanlarını değiştirebilirsiniz (`en` / `tr`, `windows` / `linux` / `termux`).

## Platformlar

- **Termux (Android):** `bash install.sh`
- **Linux ve macOS:** `bash install.sh`
- **Windows:** `install.bat` dosyasına çift tıklayın ya da cmd'de çalıştırın. Python 3'ün kurulu ve PATH'e eklenmiş olması gerekir (python.org, kurulumda "Add python.exe to PATH" seçilmeli).

Windows'ta kurulumdan sonra `codex`, `Codex` ya da `CODEX` yazmak yeterli. Komut `%LOCALAPPDATA%\Codex\bin` içine kurulur. Script PATH'i sizin yerinize değiştirmez; ekranda gösterilen PowerShell komutunu bir kez çalıştırın.

Kayıt klasörü: Termux'ta `/storage/emulated/0/Codex`, diğer sistemlerde kullanıcı klasörünüzdeki `Codex` klasörü.

## Komutlar

| Komut | Açıklama |
|---|---|
| `/new` | Sohbet gecmisini ve yuklu dosyalari sifirlar, ana modele doner |
| `/paste` | Birden fazla satir kod yapistirmani saglar (bitirmek icin .end) |
| `/edit <yol>` | Dosyayi modele verip degisiklik yaptirir, farki gosterir, onaylarsan yazar (.bak yedegi alir) |
| `/diff` | Son /edit degisikligini eski ve yeni hali arasindaki fark olarak gosterir |
| `/undo` | Son /edit islemini .bak yedeginden geri alir |
| `/open <yol>` | Dosyayi okuyup modele baglam olarak yukler |
| `/explain <yol>` | Dosyayi modele verip kisaca aciklamasini ister |
| `/run <komut>` | Komut calistirir, ciktiyi ekrana basar ve modele iletir |
| `/test [komut]` | Test calistirir; komut verilmezse projeden test komutunu otomatik bulur |
| `/fix` | Son hatali /run veya /test ciktisini modele verip duzeltme ister |
| `/save [ad]` | Son kodu kaydeder; ad verirsen o adla kaydeder |
| `/export [ad]` | Sohbeti Markdown dosyasi olarak Codex klasorune kaydeder |
| `/save-chat [ad]` | Sohbeti diske kaydeder; program kapansa da kalir |
| `/load [ad]` | Kayitli sohbeti yukler (ad verilmezse listeler) |
| `/history` | Sohbet gecmisini numarali olarak listeler |
| `/list [yol]` | Klasordeki dosya ve klasorleri listeler |
| `/tree [yol] [derinlik]` | Klasoru agac seklinde gosterir |
| `/find <metin>` | Bulundugun klasor altinda metin arar; dosya ve satir numarasi gosterir |
| `/usage` | Bu oturumda kullanilan token sayisini gosterir |
| `/limit` | Modellerin durumunu, kullanim sayisini ve limit yenilenme surelerini gosterir |
| `/model [ad|saglayici|auto]` | Gemini modellerini API'den canli listeler ve secer; saglayici degistirir |
| `/settings` | Banner rengi, stili ve otomatik kayit ayarini yapar (/settings otomatik ac|kapat) |
| `/key` | Gemini API anahtarini gizli olarak girer veya gunceller |
| `/ask-file <yol> <soru>` | Dosya hakkinda belirli bir soru sorar |
| `/run-file <yol>` | Dosyayi dilini tanyarak calistirir |
| `/lint <yol>` | Dosyayi linter ile kontrol eder (ruff, eslint, shellcheck vb.) |
| `/format <yol>` | Dosyayi bicimlendirir (black, prettier, gofmt vb.), farki gosterir, onaylarsan yazar |
| `/commit [mesaj]` | Git degisikliklerini gosterir, mesaj onerir ve onaylarsan commit atar (push yapmaz) |
| `/todo` | Projedeki TODO, FIXME ve XXX yorumlarini listeler |
| `/secrets` | Kodda yanlislikla yazilmis API anahtari ve sifre gibi degerleri tarar |
| `/template [ad]` | Hazir baslangic dosyasi olusturur (html, python, flask, express, php, bash) |
| `/snippet [liste|kaydet|sil] [ad]` | Kod parcalarini kaydeder ve tekrar kullanmanizi saglar |
| `/alias [sil] <ad> <komut>` | Kendi kisayolunuzu tanimlar (ornek: /alias /t /test) |
| `/context` | Modele giden baglami (model, mesajlar, dosyalar) gosterir |
| `/theme [ad]` | Cikti renk temasini degistirir (varsayilan, mavi, yesil, mono) |
| `/render <yol>` | Flask uygulamasini Render'a hazirlar: app.run blogunu kaldirir, requirements.txt ve render.yaml olusturur |
| `/vds <dosya>` | Python dosyasina gore requirements.txt ve Procfile olusturur, projeyi Codex/projeler klasorune zip yapar |
| `/help [komut]` | Komut listesini veya bir komutun ayrintili aciklamasini gosterir |
| `/cmds` | Bu komut listesini ve aciklamalarini gosterir |
| `/quit` | Programdan cikar |

## Render'a deploy

Flask uygulamanızı Render'a hazırlamak için:

```bash
/render app.py
```

Komut `app.run` bloğunu kaldırır, `requirements.txt` ve `render.yaml` oluşturur (ya da eksik paketleri ekler). Sonra dosyaları GitHub'a yükleyip Render'da depoyu bağlayın. Proje alt klasördeyse Render panelinde Root Directory olarak o klasörü seçin.

## VDS'e hazırlama

```bash
/vds main.py
```

Komut dosyanın import'larına bakıp `requirements.txt` oluşturur (ya da eksikleri ekler), Flask veya FastAPI varsa `web`, değilse `worker` satırıyla `Procfile` yazar. Sonra projeyi zip yapıp `Codex/projeler` klasörüne kaydeder. Zip'i sunucuya kopyalayıp kurulum komutlarını ekranda gösterilen sırayla çalıştırabilirsiniz.

## Yardım

Her komutun ayrıntılı açıklaması için `/help <komut>` yazın, örneğin `/help /vds`. `/help` tek başına bütün komutların listesini gösterir.

## Yanıt süresi

Her Gemini isteği en fazla 30 saniye beklenir. Bu sürede yanıt gelmezse program o modeli bir süreliğine atlayıp sonraki modele geçer. Bu sırada Ctrl+C gerekmez. Ayarı `main.py` içindeki `REQUEST_TIMEOUT` ile değiştirebilirsiniz.

## Sağlayıcılar

- **gemini** (varsayılan): Google Gemini resmi API. Anahtar gerekir (`/key`). Sohbet geçmişi ve dosya bağlamı desteklenir.
- **taklagpt**: TaklaGPT 1.0 (`ta-kla-gpt-api.vercel.app`). Anahtar gerekmez, ancak sohbet geçmişi ve sistem talimatı iletilmez; her istek bağımsızdır. Mesajlar URL içinde gönderildiği için çok uzun istekler reddedilir.

## Desteklenen diller

Python, JavaScript, TypeScript, HTML, CSS, PHP, Java, C, C++, C#, Go, Rust, Ruby, Dart, SQL, Bash ve diğerleri. Kod kaydedildiğinde, kurulu olan araçlarla sözdizimi otomatik kontrol edilir:

- Python, JavaScript, PHP, Bash, Ruby, Perl, Lua, Go, C ve C++ için ilgili derleyici veya yorumlayıcının kontrol modu kullanılır.
- JSON dosyaları programın içinde kontrol edilir.
- Araç kurulu değilse kontrol sessizce atlanır ve bir not gösterilir.

HTML dosyaları için `termux-open` ile tarayıcıda açma ipucu gösterilir.

## Otomatik kayıt

Varsayılan olarak program kod yazınca kaydetmek isteyip istemediğinizi sorar. `/settings` menüsünden ya da doğrudan şöyle açabilirsiniz:

```bash
/settings otomatik ac
/settings otomatik kapat
```

Açıkken kodlar sormadan `Codex` klasörüne kaydedilir.

## Modeller

Gemini model listesi API'den alınır. Açılışta ek istek gönderilmez, model kontrolü yapılmaz. Bir model çalışma sırasında "bulunamadı" (404) hatası verirse listeden çıkarılır ve bu kalıcı olarak kaydedilir. `/model yenile` bu kara listeyi sıfırlar. Seçtiğiniz model kullanılamaz hale gelirse program otomatik seçime döner. Kota (429) veya kapasite hataları modeli listeden çıkarmaz, sadece `COOLDOWN_SECONDS` süresince bekletir.

## Kaldırma

```bash
rm -f "$PREFIX/bin/"{codex,Codex,CODEX}   # Termux
rm -f ~/.local/bin/{codex,Codex,CODEX}     # diğer sistemler
```

## Lisans

Kişisel proje. Kullanım koşulları için depo sahibine danışın.
