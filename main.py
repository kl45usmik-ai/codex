#!/usr/bin/env python3
# CODEX - AI Code Engine (Termux / Google Gemini API)

import os
import re
import sys
import json
import time
import shutil
import difflib
import zipfile
import shlex
import tempfile
import getpass
import subprocess
import threading
import urllib.parse
import urllib.request
from datetime import datetime

# Turkce metin -> Ingilizce (dil English secildiginde print/input ciktilarinda uygulanir)
TR_EN = [
    ("' bulunamadi, otomatik kuruluyor...", "' not found, installing automatically..."),
    ("Hata: '", "Error: '"),
    ("' kurulamadi. Elle deneyin: pip install ", "' could not be installed. Install manually: pip install "),
    ("Termux'ta derleme hatasi alirsaniz: pkg install rust clang make", 'If you get a build error in Termux: pkg install rust clang make'),
    ("' kuruldu.", "' installed."),
    ('Degisiklik yok.', 'No changes.'),
    ('... (fark kisaltildi)', '... (diff shortened)'),
    ('Snippet kaydedilemedi: ', 'Could not save snippet: '),
    ('Uyari: config okunamadi (', 'Warning: could not read config ('),
    ('Config kaydedilemedi: ', 'Could not save config: '),
    ('Bu bir klasor, dosya degil: ', 'This is a folder, not a file: '),
    ('Dosya UTF-8 metin formatinda degil: ', 'File is not UTF-8 text: '),
    ('Dosya okunamadi: ', 'Could not read file: '),
    ('Dosya yazilamadi: ', 'Could not write file: '),
    (' kullanilamadi: ', ' is not usable: '),
    (': JSON hatasi: ', ': JSON error: '),
    (': JSON gecerli', ': valid JSON'),
    (' kurulu degil, sozdizimi kontrolu atlandi.', ' is not installed, syntax check skipped.'),
    ('[CHECK] sozdizimi kontrol ediliyor: ', '[CHECK] checking syntax: '),
    ('[CHECK] kontrol calistirilamadi: ', '[CHECK] could not run check: '),
    (': sozdizimi dogru', ': syntax OK'),
    (': sozdizimi hatasi', ': syntax error'),
    ('Calistirmak icin: ', 'To run: '),
    ('Model listesi alinamadi, mevcut liste kullaniliyor.', 'Could not fetch model list, using the current list.'),
    ("API'de kullanilabilir Gemini modeli bulunamadi.", 'No usable Gemini model found in the API.'),
    ('Secili model su an kullanilamiyor: ', 'Selected model is currently unavailable: '),
    ('. Otomatik secime donuldu.', '. Switched to automatic selection.'),
    ('Model listesi guncel (', 'Model list updated ('),
    (' model).', ' models).'),
    ('Gemini istemcisi olusturulamadi: ', 'Could not create Gemini client: '),
    ('Mesaj TaklaGPT icin cok uzun (GET istegi sinirini asiyor). Kisaltin ya da /model gemini ile devam edin.', 'Message is too long for TaklaGPT (exceeds the GET limit). Shorten it or continue with /model gemini.'),
    ("TaklaGPT'ye ulasilamadi: ", 'Could not reach TaklaGPT: '),
    ('TaklaGPT gecerli yanit vermedi: ', 'TaklaGPT returned no valid reply: '),
    (' yanit vermedi (', ' did not respond ('),
    ('Hicbir model zamaninda yanit vermedi. Tekrar deneyin.', 'No model responded in time. Please try again.'),
    ('Sonraki modele geciliyor: ', 'Switching to the next model: '),
    ('Model artik kullanilamiyor, listeden kaldirildi: ', 'Model is no longer usable and was removed from the list: '),
    (' (geri almak icin /model yenile)', ' (to restore it, use /model refresh)'),
    ('Kullanilabilir baska model kalmadi.', 'No other usable model is left.'),
    ('(bos yanit)', '(empty reply)'),
    ('Klasor bulunamadi: ', 'Folder not found: '),
    ('... ilk 100 sonuc gosterildi', '... first 100 results shown'),
    ('Sonuc yok.', 'No results.'),
    ('Henuz /edit ile yapilan bir degisiklik yok.', 'No change made with /edit yet.'),
    ('Geri alinacak degisiklik yok.', 'Nothing to undo.'),
    ('Yedek bulunamadi: ', 'Backup not found: '),
    (' yedekten geri alinsin mi? [e/H]: ', ' restore from backup? [y/N]: '),
    ('Geri alinamadi: ', 'Could not restore: '),
    ('Geri alindi: ', 'Restored: '),
    ('Sohbet gecmisi bos.', 'Chat history is empty.'),
    ('Kaydedilecek sohbet yok.', 'No chat to save.'),
    ('Sohbet kaydedildi: ', 'Chat saved: '),
    ('Sohbet kaydedilemedi: ', 'Could not save chat: '),
    ('Yuklemek icin: /load ', 'To load it: /load '),
    ('Kayitli sohbet yok.', 'No saved chats.'),
    ('Kayitli sohbetler', 'Saved chats'),
    ('Yuklemek icin: /load <ad>', 'To load one: /load <name>'),
    ('Sohbet yuklenemedi: ', 'Could not load chat: '),
    ('Sohbet yuklendi: ', 'Chat loaded: '),
    (' mesaj)', ' messages)'),
    ('Test komutu bulunamadi. ', 'Test command not found. '),
    ('Test komutu: ', 'Test command: '),
    ('Once /run veya /test ile bir komut calistirin.', 'Run a command with /run or /test first.'),
    ('Son komut basarili (cikis kodu 0), duzeltilecek hata gorunmuyor.', 'The last command succeeded (exit code 0), no error to fix.'),
    ('Bu oturumda henuz token bilgisi yok (TaklaGPT token bilgisi vermez).', 'No token data in this session yet (TaklaGPT does not report tokens).'),
    ('Bu oturum token kullanimi', 'Token usage this session'),
    ('  Giris (prompt): ', '  Input (prompt): '),
    ('  Cikis (yanit):  ', '  Output (reply): '),
    ('  Toplam:         ', '  Total:          '),
    ("Not: Gemini API'nin bildirdigi degerler.", 'Note: values reported by the Gemini API.'),
    ('Bu dosya turu icin calistirma komutu tanimli degil.', 'No run command is defined for this file type.'),
    ('Tarayicida aciliyor...', 'Opening in the browser...'),
    ('Tarayicida acmak icin: ', 'To open in a browser: '),
    ('Bu dosya turu icin linter tanimli degil.', 'No linter is defined for this file type.'),
    (' kurulu degil. Kurup tekrar deneyin.', ' is not installed. Install it and try again.'),
    ('Linter calistirilamadi: ', 'Could not run the linter: '),
    ('Sorun bulunamadi: ', 'No problems found: '),
    ('Linter hata kodu dondurdu: ', 'Linter returned error code: '),
    ('Bu dosya turu icin bicimlendirici tanimli degil.', 'No formatter is defined for this file type.'),
    ('Bicimlendirici calistirilamadi: ', 'Could not run the formatter: '),
    ('Bicimlendirici hata verdi:', 'Formatter reported an error:'),
    ('Dosya zaten bicimli.', 'File is already formatted.'),
    (' bu bicimle yazilsin mi? [e/H]: ', ' write it in this format? [y/N]: '),
    ('Yedek alinamadi: ', 'Could not create backup: '),
    ('Bicimlendirildi: ', 'Formatted: '),
    ('Bu klasor bir git deposu degil.', 'This folder is not a git repository.'),
    ('Commit edilecek degisiklik yok.', 'Nothing to commit.'),
    ('Degisen dosyalar', 'Changed files'),
    ('Commit mesaji alinamadi.', 'Could not get a commit message.'),
    ('Bu mesajla commit atilsin mi? [e/H]: ', 'Commit with this message? [y/N]: '),
    ('Commit mesaji: ', 'Commit message: '),
    ('Commit iptal edildi.', 'Commit cancelled.'),
    ('(cikti yok)', '(no output)'),
    ('... ilk 200 sonuc gosterildi', '... first 200 results shown'),
    ('TODO, FIXME veya XXX bulunamadi.', 'No TODO, FIXME or XXX found.'),
    (' olasi gizli deger bulundu. Bunlari commit etmeden once kaldirin.', ' possible secret(s) found. Remove them before committing.'),
    ('Olasi gizli deger bulunamadi.', 'No possible secrets found.'),
    ('Sablonlar', 'Templates'),
    ('Bilinmeyen sablon. Liste icin /template yazin.', 'Unknown template. Type /template for the list.'),
    (' zaten var. Uzerine yazilsin mi? [e/H]: ', ' already exists. Overwrite it? [y/N]: '),
    ('Kayitli snippet yok. Kaydetmek icin: /snippet kaydet <ad>', 'No saved snippets. To save one: /snippet save <name>'),
    ('Kaydedilecek kod yok. Once bir kod isteyin.', 'No code to save. Ask for code first.'),
    ('Snippet kaydedildi: ', 'Snippet saved: '),
    ('Snippet silindi: ', 'Snippet deleted: '),
    ('Bu ad yok: ', 'No such name: '),
    ('Snippet bulunamadi: ', 'Snippet not found: '),
    ('Takma ad yok. Ornek: /alias /t /test', 'No shortcuts yet. Example: /alias /t /test'),
    ('Bu takma ad yok: ', 'No such shortcut: '),
    ('Bu ad kullanilamaz. Ornek: /alias /t /test', 'This name cannot be used. Example: /alias /t /test'),
    ('Hedef bir komut olmali (/ ile baslamali).', 'The target must be a command (starting with /).'),
    ('Takma adlar guncellendi.', 'Shortcuts updated.'),
    ('Modele giden baglam', 'Context sent to the model'),
    ('  Saglayici: ', '  Provider: '),
    ('  Sohbet mesaji: ', '  Chat messages: '),
    (' karakter)', ' characters)'),
    ('  Yuklu dosyalar: ', '  Loaded files: '),
    ('  Sistem talimati: ', '  System prompt: '),
    (' karakter', ' characters'),
    ('  Tahmini token: ~', '  Estimated tokens: ~'),
    (' (karakter / 4 yaklasimi)', ' (characters / 4 estimate)'),
    ('Temalar', 'Themes'),
    ('Bilinmeyen tema. Secenekler: ', 'Unknown theme. Options: '),
    ('Tema degisti: ', 'Theme changed: '),
    ('Python dosyasi bulunamadi: ', 'Python file not found: '),
    ('Bu dosyada Flask uygulamasi bulunamadi (app = Flask(...) satiri yok).', 'No Flask app found in this file (no line like app = Flask(...)).'),
    ('requirements.txt guncellendi (eklenen: ', 'requirements.txt updated (added: '),
    ('requirements.txt zaten uygun.', 'requirements.txt is already fine.'),
    ('render.yaml zaten var, degistirilmedi.', 'render.yaml already exists, left unchanged.'),
    ('render.yaml olusturuldu: ', 'render.yaml created: '),
    ('--- degisiklikler ---', '--- changes ---'),
    (' Render icin guncellensin mi? [e/H]: ', ' update it for Render? [y/N]: '),
    ('Yedek alindi: ', 'Backup created: '),
    ('Kod guncellendi: ', 'Code updated: '),
    ('Kod degistirilmedi.', 'Code not changed.'),
    ('Kodda app.run blogu yok, degisiklik gerekmedi.', 'No app.run block found, no change needed.'),
    ('Render ayarlari', 'Render settings'),
    ('  (Render panelinde bu klasoru secin)', '  (select this folder in the Render dashboard)'),
    ("Not: Dosyalari GitHub'a yukleyin; Render depodan otomatik deploy eder.", 'Note: push the files to GitHub; Render deploys from the repository automatically.'),
    ('(ornek: ', '(example: '),
    ('Ornek: ', 'Example: '),
    ('requirements.txt hazir (', 'requirements.txt ready ('),
    (' paket)', ' packages)'),
    ('Procfile zaten var, degistirilmedi.', 'Procfile already exists, left unchanged.'),
    ('Procfile olusturuldu: ', 'Procfile created: '),
    ('Proje zip olarak kaydedildi (', 'Project saved as a zip ('),
    (' dosya): ', ' files): '),
    ("VDS'te calistirmak icin", 'To run it on a VDS'),
    ('Not: Procfile icin honcho ya da foreman, kalici calistirma icin systemd onerilir.', 'Note: honcho or foreman runs the Procfile; systemd is recommended for permanent running.'),
    ('Model limitleri', 'Model limits'),
    (' | bu oturumda ', ' | this session: '),
    (' istek', ' requests'),
    ('Gunluk kota sifirlanmasi: ', 'Daily quota resets in: '),
    (' sonra (yerel saat ', ' (local time '),
    ('Gunluk kota her gun Pasifik saatiyle gece yarisi sifirlanir.', 'The daily quota resets at midnight Pacific time.'),
    ("Not: Gemini API kalan istek sayisini vermez. Sureler Codex'in kendi takibidir (limit dolunca ", "Note: the Gemini API does not report remaining requests. These times are Codex's own tracking (after a limit, wait "),
    (' dk bekletilir).', ' min).'),
    ('Ayarlar', 'Settings'),
    ('  Renk: ', '  Color: '),
    ('   Stil: ', '   Style: '),
    ('   Otomatik kayit: acik', '   Auto-save: on'),
    ('   Otomatik kayit: kapali', '   Auto-save: off'),
    ('Otomatik kayit acildi.', 'Auto-save enabled.'),
    ('Otomatik kayit kapatildi.', 'Auto-save disabled.'),
    ('Otomatik kayit kapali.', 'Auto-save off.'),
    ('Otomatik kayit acik.', 'Auto-save on.'),
    ('  1) Banner rengi', '  1) Banner color'),
    ('  2) Banner stili (bold / italic / underline / dim)', '  2) Banner style (bold / italic / underline / dim)'),
    ('  3) Otomatik kayit (kod yazinca Codex klasorune kaydet)', '  3) Auto-save (save code to the Codex folder automatically)'),
    ('  4) Varsayilana don', '  4) Reset to defaults'),
    ('  0) Cik', '  0) Exit'),
    ('Secim: ', 'Choice: '),
    ('Renk sec (bos = iptal): ', 'Choose a color (empty = cancel): '),
    ('Kod (0-255): ', 'Code (0-255): '),
    ('Gecersiz kod.', 'Invalid code.'),
    ('Gecersiz secim.', 'Invalid choice.'),
    ('0-255 renk kodu gir', 'enter a 0-255 color code'),
    ('Ac/kapat icin numara (bos = bitti): ', 'Number to toggle on/off (empty = done): '),
    ('Renkler: ', 'Colors: '),
    (' veya 0-255', ' or 0-255'),
    ('Saglayicilar', 'Providers'),
    ("Gemini modelleri (API'den canli)", 'Gemini models (live from the API)'),
    ('Model secmek: /model <ad>   Otomatige donmek: /model auto', 'Select a model: /model <name>   Back to automatic: /model auto'),
    ('Model secimi otomatige alindi (Gemini).', 'Model selection set to automatic (Gemini).'),
    ('Aktif saglayici: ', 'Active provider: '),
    ('Not: TaklaGPT sohbet gecmisi ve dosya baglamini almaz; her istek bagimsizdir.', 'Note: TaklaGPT does not receive chat history or file context; each request is independent.'),
    ('Aktif model: ', 'Active model: '),
    ('Bilinmeyen model veya saglayici: ', 'Unknown model or provider: '),
    ('. Liste icin /model yazin.', '. Type /model for the list.'),
    ('Klasor listelenemedi: ', 'Could not list the folder: '),
    ('  (bos)', '  (empty)'),
    ('Dosya cok buyuk; ilk ', 'The file is too large; first '),
    (' karakter alindi.', ' characters loaded.'),
    ('Yuklendi: ', 'Loaded: '),
    ('Uyari: TaklaGPT dosya baglamini kullanmaz. Bu dosya TaklaGPT yanitlarina dahil edilmeyecek. Dosya baglami icin /model gemini kullanin.', 'Warning: TaklaGPT does not use file context. This file will not be included in TaklaGPT replies. Use /model gemini for file context.'),
    ('Uyari: TaklaGPT dosyayi guvenilir sekilde duzenleyemez. Dosya icerigi kisa degilse istek sinirini asabilir ve yanit dosyayi bozabilir. Duzenleme icin /model gemini kullanin.', 'Warning: TaklaGPT cannot edit files reliably. Long content may exceed the request limit and the reply may corrupt the file. Use /model gemini for editing.'),
    ('Talimat (ne degissin?): ', 'Instruction (what should change?): '),
    ('Yanitta kod blogu bulunamadi, dosya degistirilmedi.', 'No code block in the reply, the file was not changed.'),
    ('--- onizleme sonu ---', '--- end of preview ---'),
    (' uzerine yazilsin mi? [e/H]: ', ' overwrite it? [y/N]: '),
    ('Dosya guncellendi: ', 'File updated: '),
    ('Kaydedilecek kod blogu yok. Once bir istek yapin.', 'No code block to save. Make a request first.'),
    ('Zaman asimi (', 'Timeout ('),
    (' sn)', ' s)'),
    ('Komut calistirilamadi: ', 'Could not run the command: '),
    ('cikis kodu: ', 'exit code: '),
    ("Kodu yapistirin. Bitirmek icin yeni bir satira '.end' yazin.", "Paste the code. To finish, type '.end' on a new line."),
    ('Bos icerik, iptal edildi.', 'Empty input, cancelled.'),
    ('Bu kodla ne yapayim? (bos = analiz et): ', 'What should I do with this code? (empty = analyze): '),
    ('Beklenmeyen hata: ', 'Unexpected error: '),
    ('  Model: ', '  Model: '),
    ('Calisma dizini: ', 'Working directory: '),
    ('AKTIF', 'ACTIVE'),
    ('SECILI', 'SELECTED'),
    ('HAZIR', 'READY'),
    ('LIMIT DOLU', 'RATE LIMITED'),
    ('sirada bekliyor', 'waiting in queue'),
    ('kullanima hazir', 'ready to use'),
    ('yenilenme: ', 'resets in: '),
    (' sa ', ' h '),
    (' dk ', ' min '),
    (' sn', ' s'),
    ('Renk: ', 'Color: '),
    ('<dosya_yolu>', '<path>'),
    ('<dosya>', '<file>'),
    ('<ad>', '<name>'),
    ('<komut>', '<command>'),
    ('<metin>', '<text>'),
    ('<soru>', '<question>'),
    ('<yol>', '<path>'),
    ('[yol]', '[path]'),
    ('[derinlik]', '[depth]'),
    ('[ad]', '[name]'),
    ('[komut]', '[command]'),
    ('[mesaj]', '[message]'),
    ('[ad|saglayici|auto|yenile]', '[name|provider|auto|refresh]'),
    ('[ad|saglayici|auto|yenile]', '[name|provider|auto|refresh]'),
    ('[liste|kaydet|sil] [ad]', '[list|save|delete] [name]'),
    ('[sil] <ad> <komut>', '[delete] <name> <command>'),
    ('[sil] <ad>', '[delete] <name>'),
    ('<ad> <komut>', '<name> <command>'),
    ('<ad>', '<name>'),
    ('otomatik ac|kapat', 'auto on|off'),
    ('[otomatik ac|kapat]', '[auto on|off]'),
    ('ac|kapat', 'on|off'),
    ('(ornek: /vds main.py)', '(example: /vds main.py)'),
    ('/alias sil <ad>', '/alias delete <name>'),
    ('/snippet kaydet <ad>', '/snippet save <name>'),
    ('/load <ad>', '/load <name>'),
    ('/model <ad>', '/model <name>'),
    ('/theme <ad>', '/theme <name>'),
    ('/template <ad>', '/template <name>'),
    ('/snippet sil <ad>', '/snippet delete <name>'),
    ('/alias <ad> <komut>', '/alias <name> <command>'),
    ('/alias sil <ad>', '/alias delete <name>'),
    ('[ad]', '[name]'),
]
_TR_EN_SORTED = sorted(TR_EN, key=lambda p: -len(p[0]))


def _loc(text):
    if LANG != "en" or not isinstance(text, str):
        return text
    for tr, en in _TR_EN_SORTED:
        if tr in text:
            text = text.replace(tr, en)
    return text


_builtin_print = print
_builtin_input = input


def print(*args, **kwargs):
    if LANG == "en" and args:
        args = tuple(_loc(a) if isinstance(a, str) else a for a in args)
    _builtin_print(*args, **kwargs)


def input(prompt=""):
    return _builtin_input(_loc(prompt))


IS_WINDOWS = os.name == "nt"
if IS_WINDOWS:
    os.system("")  # Windows konsolunda ANSI renk kodlarini etkinlestirir
try:
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except (AttributeError, ValueError):
    pass


def shell_quote(path):
    """Yolu, mevcut kabuk icin guvenli sekilde tirnaklar (Windows cmd / Unix sh)."""
    if PLATFORM == "windows":
        return f'"{path}"'
    return shlex.quote(path)


def open_command(path):
    """Dosyayi varsayilan uygulamada acan komut (Termux, Windows, macOS, Linux)."""
    if PLATFORM == "termux" or shutil.which("termux-open"):
        return f"termux-open {shell_quote(path)}"
    if PLATFORM == "windows":
        return f'start "" "{path}"'
    if sys.platform == "darwin":
        return f"open {shell_quote(path)}"
    return f"xdg-open {shell_quote(path)}"

# ----------------------------------------------------------------------
# Otomatik modul kurulumu
# ----------------------------------------------------------------------
# import_adi -> pip_paket_adi
REQUIRED_MODULES = {
    "google.genai": "google-genai",
}


def _pip_install(package):
    """Paketi pip ile kurar. Basarisiz olursa --break-system-packages ile tekrar dener."""
    base = [sys.executable, "-m", "pip", "install", "--upgrade", package]
    for extra in ([], ["--break-system-packages"]):
        result = subprocess.run(base + extra)
        if result.returncode == 0:
            return True
    return False


def ensure_modules():
    import importlib
    import importlib.util

    for module, package in REQUIRED_MODULES.items():
        try:
            found = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            found = False
        if found:
            continue

        print(f"'{package}' bulunamadi, otomatik kuruluyor...")
        if not _pip_install(package):
            print(f"Hata: '{package}' kurulamadi. Elle deneyin: pip install {package}")
            print("Termux'ta derleme hatasi alirsaniz: pkg install rust clang make")
            sys.exit(1)
        importlib.invalidate_caches()
        print(f"'{package}' kuruldu.\n")


ensure_modules()

from google import genai
from google.genai import types

# ----------------------------------------------------------------------
# Ayarlar
# ----------------------------------------------------------------------
# Sira onemli: ilk model ana model, limit dolunca siradakine gecilir.
# Tercih sirasi. API'den canli liste alinamazsa bu liste kullanilir.
# Asil liste calisma aninda API'den guncellenir (refresh_models).
DEFAULT_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
]
# Sohbet icin uygun olmayan Gemini modelleri (ses, gorsel, gomme vb.)
EXCLUDE_KEYWORDS = (
    "embedding", "tts", "live", "audio", "image", "robotics",
    "deep-research", "omni", "aqa", "computer-use", "learnlm",
    "banana", "transcribe", "customtools",
)
COOLDOWN_SECONDS = 600
# Kullanilabilir sağlayicilar (/model komutu ile secilir)
PROVIDERS = ["gemini", "taklagpt"]
TAKLA_API_URL = "https://ta-kla-gpt-api.vercel.app/ask"
# GET istegi URL uzunlugu siniri (bu asildiginda istek gonderilmez)
TAKLA_MAX_URL = 7000
CONFIG_PATH = os.path.expanduser("~/.codex_config.json")
MAX_FILE_CHARS = 200_000
RUN_TIMEOUT = 120
# Modele gonderilecek en fazla mesaj sayisi (eski mesajlar kirpilir)
MAX_HISTORY_MESSAGES = 40
# Tek bir Gemini istegi bu sureden uzun surerse beklemeyi birakip sonraki modele gecilir (saniye)
REQUEST_TIMEOUT = 30

# Kayit klasoru adi ve denenecek ana depolama yollari (sirayla)
SAVE_DIR_NAME = "Codex"
SAVE_BASE_CANDIDATES = [
    "/storage/emulated/0",
    "/sdcard",
    os.path.expanduser("~/storage/shared"),
]

# Dil etiketi -> dosya uzantisi
EXT_MAP = {
    "python": "py", "py": "py",
    "javascript": "js", "js": "js", "node": "js", "mjs": "js",
    "typescript": "ts", "ts": "ts",
    "jsx": "jsx", "tsx": "tsx", "vue": "vue",
    "html": "html", "htm": "html", "css": "css", "scss": "scss",
    "php": "php",
    "bash": "sh", "sh": "sh", "shell": "sh", "zsh": "sh",
    "powershell": "ps1", "ps1": "ps1",
    "json": "json", "xml": "xml", "toml": "toml",
    "java": "java", "kotlin": "kt", "kt": "kt",
    "c": "c", "h": "h", "cpp": "cpp", "c++": "cpp", "cc": "cpp",
    "csharp": "cs", "c#": "cs", "cs": "cs",
    "go": "go", "golang": "go",
    "rust": "rs", "rs": "rs",
    "ruby": "rb", "rb": "rb",
    "perl": "pl", "pl": "pl",
    "lua": "lua", "dart": "dart", "swift": "swift",
    "scala": "scala", "r": "r",
    "markdown": "md", "md": "md",
    "sql": "sql", "yaml": "yaml", "yml": "yml",
}

# ANSI renkler
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
GREY = "\033[90m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

BANNER_COLORS = {
    "kirmizi": "\033[91m",
    "yesil": "\033[92m",
    "sari": "\033[93m",
    "mavi": "\033[94m",
    "mor": "\033[95m",
    "camgobegi": "\033[96m",
    "beyaz": "\033[97m",
    "turuncu": "\033[38;5;208m",
    "pembe": "\033[38;5;205m",
}
BANNER_STYLES = {
    "bold": "\033[1m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "dim": "\033[2m",
}
DEFAULT_SETTINGS = {"banner_color": "kirmizi", "banner_styles": ["bold"], "auto_save": False}
SETTINGS = dict(DEFAULT_SETTINGS)

LOGO = [
    " ██████╗ ██████╗ ██████╗ ███████╗██╗  ██╗",
    "██╔════╝██╔═══██╗██╔══██╗██╔════╝╚██╗██╔╝",
    "██║     ██║   ██║██║  ██║█████╗   ╚███╔╝ ",
    "██║     ██║   ██║██║  ██║██╔══╝   ██╔██╗ ",
    "╚██████╗╚██████╔╝██████╔╝███████╗██╔╝ ██╗",
    " ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝",
]

MENU = "/new  /paste  /edit  /open  /run  /save  /list  /key  /cmds  /quit"

COMMAND_HELP = [
    ("/new", "Sohbet gecmisini ve yuklu dosyalari sifirlar, ana modele doner"),
    ("/paste", "Birden fazla satir kod yapistirmani saglar (bitirmek icin .end)"),
    ("/edit <yol>", "Dosyayi modele verip degisiklik yaptirir, farki gosterir, onaylarsan yazar (.bak yedegi alir)"),
    ("/diff", "Son /edit degisikligini eski ve yeni hali arasindaki fark olarak gosterir"),
    ("/undo", "Son /edit islemini .bak yedeginden geri alir"),
    ("/open <yol>", "Dosyayi okuyup modele baglam olarak yukler"),
    ("/explain <yol>", "Dosyayi modele verip kisaca aciklamasini ister"),
    ("/run <komut>", "Komut calistirir, ciktiyi ekrana basar ve modele iletir"),
    ("/test [komut]", "Test calistirir; komut verilmezse projeden test komutunu otomatik bulur"),
    ("/fix", "Son hatali /run veya /test ciktisini modele verip duzeltme ister"),
    ("/save [ad]", "Son kodu kaydeder; ad verirsen o adla kaydeder"),
    ("/export [ad]", "Sohbeti Markdown dosyasi olarak Codex klasorune kaydeder"),
    ("/save-chat [ad]", "Sohbeti diske kaydeder; program kapansa da kalir"),
    ("/load [ad]", "Kayitli sohbeti yukler (ad verilmezse listeler)"),
    ("/history", "Sohbet gecmisini numarali olarak listeler"),
    ("/list [yol]", "Klasordeki dosya ve klasorleri listeler"),
    ("/tree [yol] [derinlik]", "Klasoru agac seklinde gosterir"),
    ("/find <metin>", "Bulundugun klasor altinda metin arar; dosya ve satir numarasi gosterir"),
    ("/usage", "Bu oturumda kullanilan token sayisini gosterir"),
    ("/limit", "Modellerin durumunu, kullanim sayisini ve limit yenilenme surelerini gosterir"),
    ("/model [ad|saglayici|auto]", "Gemini modellerini API'den canli listeler ve secer; saglayici degistirir"),
    ("/settings", "Banner rengi, stili ve otomatik kayit ayarini yapar (/settings otomatik ac|kapat)"),
    ("/key", "Gemini API anahtarini gizli olarak girer veya gunceller"),
    ("/ask-file <yol> <soru>", "Dosya hakkinda belirli bir soru sorar"),
    ("/run-file <yol>", "Dosyayi dilini tanyarak calistirir"),
    ("/lint <yol>", "Dosyayi linter ile kontrol eder (ruff, eslint, shellcheck vb.)"),
    ("/format <yol>", "Dosyayi bicimlendirir (black, prettier, gofmt vb.), farki gosterir, onaylarsan yazar"),
    ("/commit [mesaj]", "Git degisikliklerini gosterir, mesaj onerir ve onaylarsan commit atar (push yapmaz)"),
    ("/todo", "Projedeki TODO, FIXME ve XXX yorumlarini listeler"),
    ("/secrets", "Kodda yanlislikla yazilmis API anahtari ve sifre gibi degerleri tarar"),
    ("/template [ad]", "Hazir baslangic dosyasi olusturur (html, python, flask, express, php, bash)"),
    ("/snippet [liste|kaydet|sil] [ad]", "Kod parcalarini kaydeder ve tekrar kullanmanizi saglar"),
    ("/alias [sil] <ad> <komut>", "Kendi kisayolunuzu tanimlar (ornek: /alias /t /test)"),
    ("/context", "Modele giden baglami (model, mesajlar, dosyalar) gosterir"),
    ("/theme [ad]", "Cikti renk temasini degistirir (varsayilan, mavi, yesil, mono)"),
    ("/render <yol>", "Flask uygulamasini Render'a hazirlar: app.run blogunu kaldirir, requirements.txt ve render.yaml olusturur"),
    ("/vds <dosya>", "Python dosyasina gore requirements.txt ve Procfile olusturur, projeyi Codex/projeler klasorune zip yapar"),
    ("/help [komut]", "Komut listesini veya bir komutun ayrintili aciklamasini gosterir"),
    ("/cmds", "Bu komut listesini ve aciklamalarini gosterir"),
    ("/quit", "Programdan cikar"),
]

DETAILED_HELP = {
    "/new": """Ne yapar: Sohbet gecmisini ve yuklu dosyalari temizler, ana modele doner.
Kullanim: /new
Not: Kaydedilmemis sohbet kaybolur. Kalici kayit icin /save-chat kullanin.""",

    "/paste": """Ne yapar: Birden fazla satir kod yapistirmanizi saglar.
Kullanim: /paste
Yapistirdiktan sonra yeni bir satira .end yazin. Ardindan ne yapilacagini sorar; bos birakirsaniz kod analiz edilir.""",

    "/edit": """Ne yapar: Dosyayi modele verir, ne degissin diye sorar, donen kodun farkini gosterir. Onaylarsaniz dosyaya yazar ve .bak yedegi alir.
Kullanim: /edit <dosya_yolu>
Ornek: /edit app.py  ->  talimat: hata yakalama ekle
Not: Degisiklik /undo ile geri alinabilir. TaklaGPT ile duzenleme guvenilir degildir.""",

    "/diff": """Ne yapar: Son degisikligin (/edit, /format, /render) farkini tekrar gosterir. Dosyayi degistirmez.
Kullanim: /diff""",

    "/undo": """Ne yapar: Son degistirilen dosyayi .bak yedeginden geri yukler.
Kullanim: /undo
Onay ister. Yalnizca son islem geri alinir.""",

    "/open": """Ne yapar: Dosyayi okuyup sohbete baglam olarak ekler. Sonraki sorular bu dosyayi dikkate alir.
Kullanim: /open <dosya_yolu>
Not: Buyuk dosyalarin ilk 200.000 karakteri alinir. TaklaGPT dosya baglamini kullanmaz.""",

    "/explain": """Ne yapar: Dosyayi modele verip Turkce, kisa bir aciklama ister. Dosyayi degistirmez.
Kullanim: /explain <dosya_yolu>""",

    "/run": """Ne yapar: Komutu Termux'ta calistirir, ciktiyi ve cikis kodunu gosterir, sonucu modele iletip yorum ister.
Kullanim: /run <komut>
Ornek: /run python app.py
Not: Komut dogrudan calisir, dikkatli kullanin. Zaman asimi 120 saniyedir.""",

    "/test": """Ne yapar: Projenin test komutunu calistirir.
Kullanim: /test [komut]
Komut verilmezse proje dosyalarina bakar: package.json icinde test script'i varsa npm test, pytest kuruluysa test_*.py dosyalari veya tests klasoru icin pytest -q, Cargo.toml icin cargo test, go.mod icin go test ./...
Ornek: /test   veya   /test python -m unittest""",

    "/fix": """Ne yapar: Son /run ya da /test ciktisi hatali ise modele gonderir, hatanin nedenini ve duzeltmeyi ister.
Kullanim: /fix
Not: Son komut basarili ise calismaz.""",

    "/save": """Ne yapar: Modelin son verdigi kod blogunu Codex klasorune kaydeder.
Kullanim: /save [ad]
Ornek: /save hesap.py
Ad verilmezse otomatik bir ad uretilir. Uzanti yazilmazsa dilden eklenir.""",

    "/export": """Ne yapar: Tum sohbeti Markdown (.md) dosyasi olarak Codex klasorune yazar. Okumak ya da paylasmak icin uygundur.
Kullanim: /export [ad]
Ornek: /export proje_notlari""",

    "/save-chat": """Ne yapar: Sohbeti ve yuklu dosyalari ~/.codex_chats klasorune JSON olarak kaydeder. Program kapansa da kalir.
Kullanim: /save-chat [ad]
Geri yuklemek icin /load kullanin.""",

    "/load": """Ne yapar: Kayitli bir sohbeti yukler ve mevcut sohbetin yerine koyar.
Kullanim: /load [ad]
Ad verilmezse kayitli sohbetleri listeler.""",

    "/history": """Ne yapar: Sohbet mesajlarini numarali olarak listeler (her biri ilk 70 karakter).
Kullanim: /history""",

    "/list": """Ne yapar: Klasordeki dosya ve klasorleri boyutlariyla listeler.
Kullanim: /list [yol]
Yol verilmezse bulundugunuz klasor gosterilir.""",

    "/tree": """Ne yapar: Klasoru agac seklinde gosterir. .git, node_modules gibi klasorler gizlenir.
Kullanim: /tree [yol] [derinlik]
Ornek: /tree . 2
Varsayilan derinlik 3'tur.""",

    "/find": """Ne yapar: Bulundugunuz klasor altindaki dosyalarda metni arar, dosya yolu ve satir numarasini gosterir.
Kullanim: /find <metin>
Buyuk/kucuk harf duyarsizdir. En fazla 100 sonuc gosterir.""",

    "/usage": """Ne yapar: Bu oturumda Gemini'ye giden (giris) ve gelen (cikis) token sayisini gosterir.
Kullanim: /usage
Not: TaklaGPT token bilgisi vermez.""",

    "/limit": """Ne yapar: Gemini modellerinin durumunu gosterir: aktif, sirada, limit dolu ve yenilenme suresi.
Kullanim: /limit
Not: Bu, Codex'in kendi bekleme takibidir. Google'in kalan kota bilgisi degildir.""",

    "/model": """Ne yapar: Saglayici ve Gemini modeli secimi.
Kullanim:
  /model              kullanilabilir Gemini modellerini listeler
  /model <ad>         o modeli secer (kalici)
  /model auto         modeli otomatik secime birakir
  /model gemini       saglayiciyi Gemini yapar
  /model taklagpt     saglayiciyi TaklaGPT yapar
  /model yenile       kaldirilan modelleri yeniden listeye alir
Not: Kullanilamayan bir model ilk denemede 404 verir ve listeden otomatik cikarilir. /model yenile bu listeyi sifirlar.""",

    "/settings": """Ne yapar: Banner rengi, banner stili, otomatik kayit ve varsayilana donus ayarlari.
Kullanim: /settings [otomatik ac|kapat]
Ornek: /settings otomatik ac
Not: Otomatik kayit aciksa kodlar sormadan Codex klasorune kaydedilir.""",

    "/key": """Ne yapar: Gemini API anahtarini gizli girisle kaydeder.
Kullanim: /key
Anahtar ~/.codex_config.json dosyasinda 600 izniyle tutulur. Anahtari GitHub'a yuklemeyin.""",

    "/cmds": """Ne yapar: Tum komutlari kisa aciklamalariyla listeler.
Kullanim: /cmds""",

    "/quit": """Ne yapar: Programdan cikar. /exit ve /q da ayni isi yapar.
Kullanim: /quit
Not: Kaydedilmemis sohbet kaybolur.""",

    "/ask-file": """Ne yapar: Dosyayi modele verip belirli bir soru sorar. Dosya sohbete eklenmez.
Kullanim: /ask-file <dosya_yolu> <soru>
Ornek: /ask-file app.py veritabanina nasil baglaniyor?""",

    "/run-file": """Ne yapar: Dosyayi uzantisina gore calistirir.
Kullanim: /run-file <dosya_yolu>
py: python, js: node, php: php, sh: bash, rb: ruby, html: varsayilan tarayicida acar.
Ornek: /run-file script.js""",

    "/lint": """Ne yapar: Dosyayi linter ile kontrol eder. Dosyayi degistirmez.
Kullanim: /lint <dosya_yolu>
py: ruff, js/ts: eslint, php: phpcs, sh: shellcheck, rb: rubocop, go: go vet
Arac kurulu degilse uyari verir.""",

    "/format": """Ne yapar: Dosyayi bicimlendirir. Once farki gosterir, onaylarsaniz yazar ve .bak yedegi alir.
Kullanim: /format <dosya_yolu>
py: black, js/ts/css/html/json: prettier, go: gofmt, rs: rustfmt, sh: shfmt
Not: /undo ile geri alinabilir.""",

    "/commit": """Ne yapar: Git deposundaki degisiklikleri gosterir, commit mesaji onerir ve onaylarsaniz commit atar.
Kullanim: /commit [mesaj]
Mesaj verilmezse model bir mesaj onerir. Onaylarsaniz git add -A ve git commit calisir. Push yapmaz.
Not: Commit'ten once /secrets calistirin.""",

    "/todo": """Ne yapar: Projedeki TODO, FIXME ve XXX yorumlarini dosya ve satir numarasiyla listeler.
Kullanim: /todo""",

    "/secrets": """Ne yapar: Kodda yazili API anahtari, sifre ve ozel anahtar gibi gorunen degerleri tarar. Degerlerin tamamini gostermez.
Kullanim: /secrets
GitHub'a yuklemeden once calistirin.""",

    "/template": """Ne yapar: Hazir bir baslangic dosyasi olusturur.
Kullanim: /template [ad]
Sablonlar: html, python, flask, express, php, bash
Ad verilmezse listeler. Flask sablonu Render'a uygundur.""",

    "/snippet": """Ne yapar: Sik kullandiginiz kod parcalarini kaydeder ve tekrar kullanmanizi saglar.
Kullanim:
  /snippet kaydet <ad>   son modelin kod blogunu kaydeder
  /snippet <ad>          kayitli kodu gosterir
  /snippet liste         kayitli parcalari listeler
  /snippet sil <ad>      parcayi siler
Kayitlar ~/.codex_snippets.json dosyasinda tutulur.""",

    "/alias": """Ne yapar: Kendi kisayolunuzu tanimlar.
Kullanim:
  /alias <ad> <komut>    ornek: /alias /t /test
  /alias sil <ad>        kisayolu siler
  /alias                 kisayollari listeler
Ad / ile baslamali ve yerlesik bir komut olmamalidir.""",

    "/context": """Ne yapar: Modele giden baglami gosterir: saglayici, model, mesaj sayisi, yuklu dosyalar ve tahmini token.
Kullanim: /context
Beklenmedik bir cevap aldiginizda nedenini anlamak icin kullanin.""",

    "/theme": """Ne yapar: Cikti renk temasini degistirir.
Kullanim: /theme [ad]
Temalar: varsayilan, mavi, yesil, mono
Banner renkleri /settings ile ayri ayarlanir.""",

    "/render": """Ne yapar: Flask dosyasini Render'a hazirlar.
Kullanim: /render <dosya_yolu>
app.run blogunu kaldirir (onayiniz alinir), requirements.txt ve render.yaml olusturur ya da eksikleri ekler.
Gosterilen Build ve Start komutlarini Render panelinde kullanin.""",

    "/vds": """Ne yapar: Python dosyasi icin requirements.txt ve Procfile olusturur, projeyi zip yapip Codex/projeler klasorune kaydeder.
Kullanim: /vds <dosya_yolu>
Ornek: /vds main.py
Flask veya FastAPI ise web satiri, degilse worker satiri yazilir. Ekranda sunucudaki kurulum komutlari gosterilir.""",

    "/help": """Ne yapar: Komut listesini veya bir komutun ayrintili aciklamasini gosterir.
Kullanim:
  /help          komut listesi
  /help /vds     o komutun ayrintisi (basindaki / isteğe bağlıdır: /help vds)""",
}



# ----------------------------------------------------------------------
# Dil ve ortam (ilk acilista bir kez sorulur, ~/.codex_config.json'a kaydedilir)
# ----------------------------------------------------------------------
LANG = "tr"          # "tr" veya "en"
PLATFORM = "linux"   # "windows", "linux" veya "termux"

STR = {
    "tr": {
        "setup_lang": "Dil secin / Choose language:",
        "setup_platform": "Hangi ortamda calisiyorsunuz?",
        "setup_invalid": "Gecersiz secim / Invalid choice.",
        "setup_done": "Kurulum tamamlandi. Ayarlari /settings ile degistirebilirsiniz.",
        "thinking": "dusunuyor...",
        "model_changed": "Model degistirildi: {model}",
        "all_limited": "Tum modellerin limiti dolu. Bir sure sonra tekrar deneyin.",
        "api_error": "API hatasi ({model}): {err}",
        "need_key": "Baslamak icin /key ile API key girin.",
        "no_key": "API key bulunamadi. /key komutuyla girin.",
        "save_prompt": "Kod {folder} klasorune kaydedilsin mi? [e/H]: ",
        "saved": "Kaydedildi: {path}",
        "open_hint": "Tarayicida acmak icin: {cmd}",
        "bye": "Gorusuruz.",
        "cancelled": "Iptal edildi.",
        "unknown_cmd": "Bilinmeyen komut: {cmd}",
        "all_cmds_hint": "Tum komutlar icin /cmds yazin.",
        "commands_title": "Komutlar",
        "history_cleared": "Sohbet gecmisi ve dosya baglami sifirlandi.",
        "api_key_prompt": "Gemini API Key (gizli girilir): ",
        "api_key_saved": "API key kaydedildi: {path}",
        "storage_missing": "Kayit klasoru kullanilamiyor. Termux'ta 'termux-setup-storage' calistirin.",
        "help_title": "Ayrintili yardim",
        "help_usage": "Kullanim: /help <komut>   ornek: /help /vds",
        "help_none": "Bu komut icin ayrintili yardim yok: {key}",
        "usage_word": "Kullanim",
        "not_saved": "Kaydedilmedi.",
        "file_not_found": "Dosya bulunamadi: {path}",
    },
    "en": {
        "setup_lang": "Dil secin / Choose language:",
        "setup_platform": "Which platform are you using?",
        "setup_invalid": "Gecersiz secim / Invalid choice.",
        "setup_done": "Setup complete. You can change settings with /settings.",
        "thinking": "thinking...",
        "model_changed": "Model changed: {model}",
        "all_limited": "All models are rate limited. Try again in a while.",
        "api_error": "API error ({model}): {err}",
        "need_key": "Enter your API key with /key to start.",
        "no_key": "API key not found. Enter it with /key.",
        "save_prompt": "Save code to the {folder} folder? [y/N]: ",
        "saved": "Saved: {path}",
        "open_hint": "To open in a browser: {cmd}",
        "bye": "Goodbye.",
        "cancelled": "Cancelled.",
        "unknown_cmd": "Unknown command: {cmd}",
        "all_cmds_hint": "Type /cmds for all commands.",
        "commands_title": "Commands",
        "history_cleared": "Chat history and loaded files were cleared.",
        "api_key_prompt": "Gemini API Key (hidden input): ",
        "api_key_saved": "API key saved: {path}",
        "storage_missing": "Save folder is not available. In Termux run 'termux-setup-storage'.",
        "help_title": "Detailed help",
        "help_usage": "Usage: /help <command>   example: /help /vds",
        "help_none": "No detailed help for this command: {key}",
        "usage_word": "Usage",
        "not_saved": "Not saved.",
        "file_not_found": "File not found: {path}",
    },
}


def t(key, **kw):
    """Secili dilde metin dondurur; yoksa Turkce'ye duser."""
    text = STR.get(LANG, {}).get(key) or STR["tr"].get(key, key)
    return text.format(**kw) if kw else text


def default_platform():
    if IS_WINDOWS:
        return "windows"
    if "com.termux" in os.environ.get("PREFIX", ""):
        return "termux"
    return "linux"


def load_locale():
    global LANG, PLATFORM
    cfg = load_config()
    LANG = cfg.get("language", "tr") if cfg.get("language") in ("tr", "en") else "tr"
    PLATFORM = cfg.get("platform") if cfg.get("platform") in ("windows", "linux", "termux") else default_platform()


def _ask_choice(question, options, valid):
    print(question)
    for label in options:
        print(f"  {label}")
    while True:
        answer = input("> ").strip()
        if answer in valid:
            return answer
        print(f"{YELLOW}{STR[LANG]['setup_invalid'] if LANG in STR else ''}{RESET}")


def setup_wizard():
    """Ilk acilista bir kez dil ve ortam sorar, sonucu kaydeder."""
    global LANG, PLATFORM
    try:
        print(f"{BOLD}Dil secin / Choose language{RESET}")
        lang = _ask_choice("", ["1) Turkce", "2) English"], ("1", "2"))
        LANG = "tr" if lang == "1" else "en"

        print()
        plat = _ask_choice(t("setup_platform"),
                           ["1) Windows", "2) Linux / macOS", "3) Termux (Android)"],
                           ("1", "2", "3"))
        PLATFORM = {"1": "windows", "2": "linux", "3": "termux"}[plat]

        cfg = load_config()
        cfg["language"] = LANG
        cfg["platform"] = PLATFORM
        cfg["setup_done"] = True
        save_config(cfg)
        print(f"{GREEN}{t('setup_done')}{RESET}\n")
    except (EOFError, KeyboardInterrupt):
        LANG, PLATFORM = "tr", default_platform()
        cfg = load_config()
        cfg.update({"language": LANG, "platform": PLATFORM, "setup_done": True})
        save_config(cfg)
        print()


EN_CMD = {
    "/new": ("/new", "Clears chat history and loaded files"),
    "/paste": ("/paste", "Paste several lines of code (finish with .end)"),
    "/edit": ("/edit <path>", "Asks the model to change a file, shows the diff, writes after your approval (.bak backup)"),
    "/diff": ("/diff", "Shows the diff of the last change (/edit, /format, /render)"),
    "/undo": ("/undo", "Restores the last changed file from its .bak backup"),
    "/open": ("/open <path>", "Reads a file and adds it to the chat as context"),
    "/explain": ("/explain <path>", "Asks the model to briefly explain a file"),
    "/run": ("/run <command>", "Runs a command, shows output and exit code, sends result to the model"),
    "/test": ("/test [command]", "Runs tests; detects the test command from the project if none given"),
    "/fix": ("/fix", "Sends the last failing /run or /test output to the model for a fix"),
    "/save": ("/save [name]", "Saves the last code block from the model"),
    "/export": ("/export [name]", "Saves the whole chat as a Markdown file in the Codex folder"),
    "/save-chat": ("/save-chat [name]", "Saves the chat to disk so it survives restarts"),
    "/load": ("/load [name]", "Loads a saved chat (lists saved chats if no name)"),
    "/history": ("/history", "Lists chat messages with numbers"),
    "/list": ("/list [path]", "Lists files and folders with sizes"),
    "/tree": ("/tree [path] [depth]", "Shows a folder as a tree"),
    "/find": ("/find <text>", "Searches text in files under the current folder"),
    "/usage": ("/usage", "Shows token usage for this session (Gemini only)"),
    "/limit": ("/limit", "Shows model status and cooldown times"),
    "/model": ("/model [name|provider|auto|refresh]", "Lists and selects Gemini models; switches provider"),
    "/settings": ("/settings", "Banner color, style, auto-save and defaults"),
    "/key": ("/key", "Enters the Gemini API key securely"),
    "/cmds": ("/cmds", "Lists all commands"),
    "/quit": ("/quit", "Exits the program"),
    "/ask-file": ("/ask-file <path> <question>", "Asks a question about a file without adding it to the chat"),
    "/run-file": ("/run-file <path>", "Runs a file based on its extension"),
    "/lint": ("/lint <path>", "Checks a file with a linter (ruff, eslint, shellcheck...)"),
    "/format": ("/format <path>", "Formats a file (black, prettier, gofmt...), shows the diff, writes after approval"),
    "/commit": ("/commit [message]", "Shows git changes, suggests a message, commits after approval (no push)"),
    "/todo": ("/todo", "Lists TODO, FIXME and XXX comments"),
    "/secrets": ("/secrets", "Scans code for API keys, passwords and private keys"),
    "/template": ("/template [name]", "Creates a starter file (html, python, flask, express, php, bash)"),
    "/snippet": ("/snippet [list|save|delete] [name]", "Saves and reuses code snippets"),
    "/alias": ("/alias [delete] <name> <command>", "Creates a shortcut (example: /alias /t /test)"),
    "/context": ("/context", "Shows what is sent to the model (model, messages, files)"),
    "/theme": ("/theme [name]", "Changes the output color theme (default, blue, green, mono)"),
    "/render": ("/render <path>", "Prepares a Flask app for Render (removes app.run, creates requirements.txt and render.yaml)"),
    "/vds": ("/vds <file>", "Creates requirements.txt and Procfile and zips the project into the Codex/projeler folder"),
    "/help": ("/help [command]", "Shows the command list or the details of one command"),
}

EN_DETAIL = {
    "/new": "Clears chat history and loaded files and returns to the main model.\nUsage: /new\nNote: Unsaved chat is lost. Use /save-chat to keep it.",
    "/paste": "Paste several lines of code. Finish with .end on a new line, then say what to do (empty = analyze).\nUsage: /paste",
    "/edit": "Sends a file to the model with your instruction, shows the diff, writes it after approval and makes a .bak backup.\nUsage: /edit <path>\nExample: /edit app.py -> add error handling\nNote: Undo with /undo.",
    "/diff": "Shows the diff of the last change (/edit, /format, /render). Does not change files.\nUsage: /diff",
    "/undo": "Restores the last changed file from its .bak backup. Asks for confirmation. Only the last change.\nUsage: /undo",
    "/open": "Reads a file and adds it to the chat as context for later questions.\nUsage: /open <path>\nNote: Large files are cut to 200,000 characters.",
    "/explain": "Asks the model for a short explanation of a file. Does not change the file.\nUsage: /explain <path>",
    "/run": "Runs a command in the terminal, shows output and exit code, and sends the result to the model.\nUsage: /run <command>\nExample: /run python app.py\nNote: Commands run as typed. Timeout 120 seconds.",
    "/test": "Runs the project's tests. Without arguments it looks for npm test, pytest, cargo test or go test.\nUsage: /test [command]\nExample: /test or /test python -m unittest",
    "/fix": "Sends the last failing /run or /test output to the model and asks for the cause and a fix.\nUsage: /fix\nNote: Does nothing if the last command succeeded.",
    "/save": "Saves the last code block from the model to the Codex folder.\nUsage: /save [name]\nExample: /save calc.py\nWithout a name a name is generated.",
    "/export": "Saves the whole chat as a Markdown file in the Codex folder.\nUsage: /export [name]",
    "/save-chat": "Saves the chat and loaded files as JSON in ~/.codex_chats. Survives restarts.\nUsage: /save-chat [name]",
    "/load": "Loads a saved chat, replacing the current one. Without a name it lists saved chats.\nUsage: /load [name]",
    "/history": "Lists chat messages with numbers (first 70 characters each).\nUsage: /history",
    "/list": "Lists files and folders with sizes. Default is the current folder.\nUsage: /list [path]",
    "/tree": "Shows a folder as a tree. .git and node_modules are hidden. Default depth is 3.\nUsage: /tree [path] [depth]\nExample: /tree . 2",
    "/find": "Searches text in files under the current folder (case-insensitive). Shows file and line. Max 100 results.\nUsage: /find <text>",
    "/usage": "Shows input and output token counts for this session (Gemini only).\nUsage: /usage",
    "/limit": "Shows Gemini model status: active, waiting, rate limited and reset time. This is Codex's own cooldown tracking, not Google's quota.\nUsage: /limit",
    "/model": "Model and provider selection.\n  /model            list available Gemini models\n  /model <name>    select a model (saved)\n  /model auto      automatic selection\n  /model gemini    use Gemini\n  /model taklagpt use TaklaGPT\n  /model refresh   clear the list of removed models",
    "/settings": "Banner color, banner style, auto-save and reset to defaults.\nUsage: /settings [auto on|off]\nExample: /settings auto on",
    "/key": "Stores the Gemini API key with hidden input. Saved in ~/.codex_config.json with permission 600. Never upload the key to GitHub.\nUsage: /key",
    "/cmds": "Lists all commands with short descriptions.\nUsage: /cmds",
    "/quit": "Exits the program. /exit and /q do the same. Unsaved chat is lost.\nUsage: /quit",
    "/ask-file": "Sends a file to the model with a question. The file is not added to the chat.\nUsage: /ask-file <path> <question>\nExample: /ask-file app.py how does it connect to the database?",
    "/run-file": "Runs a file based on its extension: py (Python), js (node), php, sh (bash), rb (ruby), html (default browser).\nUsage: /run-file <path>",
    "/lint": "Checks a file with a linter and does not change it. py: ruff, js/ts: eslint, php: phpcs, sh: shellcheck, rb: rubocop, go: go vet. Shows a warning if the tool is missing.\nUsage: /lint <path>",
    "/format": "Formats a file. Shows the diff first, writes after approval and makes a .bak backup. Undo with /undo.\nUsage: /format <path>\npy: black, js/ts/css/html/json: prettier, go: gofmt, rs: rustfmt, sh: shfmt",
    "/commit": "Shows git changes, suggests a commit message and commits after approval (git add -A then commit). Never pushes.\nUsage: /commit [message]\nNote: Run /secrets before committing.",
    "/todo": "Lists TODO, FIXME and XXX comments with file and line.\nUsage: /todo",
    "/secrets": "Scans code for values that look like API keys, passwords or private keys. Masks the values. Run before uploading to GitHub.\nUsage: /secrets",
    "/template": "Creates a starter file: html, python, flask, express, php, bash. Without a name it lists them. The flask template is Render-ready.\nUsage: /template [name]",
    "/snippet": "Saves and reuses code snippets stored in ~/.codex_snippets.json.\n  /snippet save <name>   saves the last code block\n  /snippet <name>        shows a snippet\n  /snippet list          lists snippets\n  /snippet delete <name> deletes a snippet",
    "/alias": "Creates your own shortcut. Name must start with / and must not be a built-in command.\n  /alias <name> <command>  e.g. /alias /t /test\n  /alias delete <name>\n  /alias                   lists shortcuts",
    "/context": "Shows what goes to the model: provider, model, number of messages, loaded files and an estimated token count. Useful for understanding odd answers.\nUsage: /context",
    "/theme": "Changes the output color theme: default, blue, green, mono. Banner colors are set separately with /settings.\nUsage: /theme [name]",
    "/render": "Prepares a Flask app for Render: removes the app.run block (after approval), creates or updates requirements.txt and render.yaml. Use the Build and Start commands shown in the Render dashboard.\nUsage: /render <path>",
    "/vds": "Creates requirements.txt from the imports and a Procfile (web for Flask/FastAPI, worker otherwise), then zips the project into Codex/projeler.\nUsage: /vds <file>\nExample: /vds main.py",
    "/help": "Shows the command list, or the details of one command.\n  /help            command list\n  /help /vds      details of /vds (the leading / is optional)",
}


def localized_commands():
    """Komut listesini secili dilde (etiket, aciklama) olarak dondurur."""
    if LANG != "en":
        return COMMAND_HELP
    out = []
    for label, desc in COMMAND_HELP:
        base = label.split()[0]
        out.append(EN_CMD.get(base, (label, desc)))
    return out


def detailed_help_text(key):
    if LANG == "en":
        return EN_DETAIL.get(key)
    return DETAILED_HELP.get(key)

SIGNATURE = "Codex By Klaus"
BASE_SYSTEM_EN = (
    "You are CODEX, an expert AI code assistant that replies in English. "
    "You were created by Klaus. Never introduce yourself as Gemini, Google or any other model; "
    "if asked who you are, say 'I am Codex, made by Klaus'. "
    "The user works on Termux (Android), Windows or Linux. Write clean, modular, working code in any language. "
    "Always put code in fenced blocks with a language tag. "
    "Put the comment '" + SIGNATURE + "' at the top of every code file (after a shebang if there is one). "
    "When asked to edit a file, return the ENTIRE file in a single code block."
)

BASE_SYSTEM = (
    "Sen CODEX adli, Turkce yanit veren uzman bir yapay zeka kod asistanisin. "
    "Python, JavaScript, TypeScript, HTML, CSS, PHP, Java, C/C++, C#, Go, Rust, "
    "Ruby, Dart, SQL, Bash ve diger tum dillerde uzmansin; kullanicinin istedigi dilde yaz. "
    "Seni Klaus gelistirdi. Kendini asla Gemini, Google veya baska bir model olarak "
    "tanitma; kim oldugun sorulursa 'Ben Codex, Klaus tarafindan yapildim' de. "
    "Kullanicinin Termux ortaminda calistigini unutma. Kod uretirken temiz, modular "
    "ve calisabilir kod yaz; kod bloklarini her zaman dil etiketiyle ``` icinde ver. "
    "Her kod dosyasinin en ustune (shebang varsa hemen altina) yorum satiri olarak "
    f"'{SIGNATURE}' yaz (ornek: # {SIGNATURE}). "
    "Bir dosyayi duzenlemen istendiginde dosyanin TAMAMINI tek bir kod blogunda dondur."
)


# ----------------------------------------------------------------------
# Yardimci fonksiyonlar
# ----------------------------------------------------------------------
def clear_screen():
    print("\033[2J\033[H", end="")


def color_code(value):
    value = str(value)
    if value in BANNER_COLORS:
        return BANNER_COLORS[value]
    if value.isdigit() and 0 <= int(value) <= 255:
        return f"\033[38;5;{int(value)}m"
    return BANNER_COLORS["kirmizi"]


def banner_format():
    styles = "".join(BANNER_STYLES[x] for x in SETTINGS["banner_styles"] if x in BANNER_STYLES)
    return color_code(SETTINGS["banner_color"]) + styles


def print_logo():
    fmt = banner_format()
    for line in LOGO:
        print(f"{fmt}{line}{RESET}")


def print_header(model):
    clear_screen()
    print_logo()
    sep = color_code(SETTINGS["banner_color"])
    print(f"{sep}{'━' * 42}{RESET}")
    print(f"{UNDERLINE}[ AI CODE ENGINE ]  model: {model}{RESET}")
    print(f"{sep}{'━' * 42}{RESET}")
    print(f"{GREY}{MENU}{RESET}\n")


def fmt_duration(seconds):
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h} sa {m} dk"
    if m:
        return f"{m} dk {sec} sn"
    return f"{sec} sn"


SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
CHAT_DIR = os.path.expanduser("~/.codex_chats")
SNIPPET_FILE = os.path.expanduser("~/.codex_snippets.json")

LINTERS = {
    "py": ["ruff", "check"], "js": ["eslint"], "ts": ["eslint"], "php": ["phpcs"],
    "sh": ["shellcheck"], "rb": ["rubocop"], "go": ["go", "vet"],
}
FORMATTERS = {
    "py": ["black", "-q"], "js": ["prettier", "--write"], "ts": ["prettier", "--write"],
    "css": ["prettier", "--write"], "html": ["prettier", "--write"], "json": ["prettier", "--write"],
    "go": ["gofmt", "-w"], "rs": ["rustfmt"], "sh": ["shfmt", "-w"],
}
SECRET_PATTERNS = [
    ("AWS anahtari", r"AKIA[0-9A-Z]{16}"),
    ("Google API anahtari", r"AIza[0-9A-Za-z\-_]{35}"),
    ("GitHub token", r"gh[pousr]_[A-Za-z0-9]{36}"),
    ("API anahtari benzeri (sk-)", r"sk-[A-Za-z0-9_\-]{20,}"),
    ("Ozel anahtar", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("Gizli deger atamasi", r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"),
]
THEMES = {
    "varsayilan": {"RED": "\033[91m", "GREEN": "\033[92m", "YELLOW": "\033[93m", "GREY": "\033[90m"},
    "mavi": {"RED": "\033[94m", "GREEN": "\033[96m", "YELLOW": "\033[93m", "GREY": "\033[37m"},
    "yesil": {"RED": "\033[92m", "GREEN": "\033[32m", "YELLOW": "\033[33m", "GREY": "\033[90m"},
    "mono": {"RED": "\033[97m", "GREEN": "\033[97m", "YELLOW": "\033[97m", "GREY": "\033[90m"},
}
TEMPLATES = {
    "html": ("index.html", """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sayfa</title>
</head>
<body>
  <h1>Merhaba</h1>
</body>
</html>
"""),
    "python": ("main.py", """def main():
    print("Merhaba")


if __name__ == "__main__":
    main()
"""),
    "flask": ("app.py", """from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Merhaba"
"""),
    "express": ("index.js", """const express = require("express");
const app = express();

app.get("/", (req, res) => res.send("Merhaba"));

app.listen(3000, () => console.log("http://localhost:3000"));
"""),
    "php": ("index.php", """<?php
echo "Merhaba";
"""),
    "bash": ("script.sh", """#!/usr/bin/env bash
set -e

echo "Merhaba"
"""),
}


def show_diff(old, new, name):
    """Eski ve yeni metin arasindaki farki renkli olarak gosterir."""
    diff = list(difflib.unified_diff(
        old.splitlines(True), new.splitlines(True),
        fromfile=f"{name} (once)", tofile=f"{name} (sonra)",
    ))
    if not diff:
        print(f"{GREY}Degisiklik yok.{RESET}")
        return
    for line in diff[:200]:
        line = line.rstrip("\n")
        if line.startswith("+++") or line.startswith("---"):
            print(f"{BOLD}{line}{RESET}")
        elif line.startswith("+"):
            print(f"{GREEN}{line}{RESET}")
        elif line.startswith("-"):
            print(f"{RED}{line}{RESET}")
        else:
            print(f"{GREY}{line}{RESET}")
    if len(diff) > 200:
        print(f"{GREY}... (fark kisaltildi){RESET}")


def tree_lines(root, max_depth=3, limit=300):
    """Klasor agacini satir listesi olarak dondurur."""
    lines = [os.path.abspath(root)]
    state = {"count": 0, "stop": False}

    def walk(path, prefix, depth):
        try:
            names = os.listdir(path)
        except OSError:
            return
        names = [n for n in names if not n.startswith(".") and n not in SKIP_DIRS]
        names.sort(key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower()))
        for i, name in enumerate(names):
            if state["count"] >= limit:
                state["stop"] = True
                return
            full = os.path.join(path, name)
            last = i == len(names) - 1
            is_dir = os.path.isdir(full)
            lines.append(prefix + ("└── " if last else "├── ") + name + ("/" if is_dir else ""))
            state["count"] += 1
            if is_dir and depth < max_depth:
                walk(full, prefix + ("    " if last else "│   "), depth + 1)
                if state["stop"]:
                    return

    walk(root, "", 1)
    if state["stop"]:
        lines.append("... (liste kisaltildi)")
    return lines


def safe_chat_name(name):
    """Sohbet adini dosya adina uygun hale getirir."""
    name = os.path.basename(name.strip())
    return re.sub(r"[^\w\-]", "_", name) if name else ""


def detect_test_command():
    """Proje klasorune bakip test komutunu tahmin eder."""
    if os.path.exists("package.json"):
        try:
            with open("package.json", encoding="utf-8") as f:
                scripts = json.load(f).get("scripts", {})
            if scripts.get("test") and "no test specified" not in scripts["test"]:
                return "npm test"
        except (OSError, ValueError):
            pass
    names = os.listdir(".")
    if shutil.which("pytest") and (
        "tests" in names or "pytest.ini" in names
        or any(n.startswith("test_") and n.endswith(".py") for n in names)
    ):
        return "pytest -q"
    if "Cargo.toml" in names:
        return "cargo test"
    if "go.mod" in names:
        return "go test ./..."
    return None


IMPORT_TO_PIP = {
    "cv2": "opencv-python", "PIL": "Pillow", "bs4": "beautifulsoup4", "yaml": "PyYAML",
    "dotenv": "python-dotenv", "sklearn": "scikit-learn", "telegram": "python-telegram-bot",
    "discord": "discord.py", "Crypto": "pycryptodome", "jwt": "PyJWT", "serial": "pyserial",
    "dateutil": "python-dateutil", "psycopg2": "psycopg2-binary", "MySQLdb": "mysqlclient",
    "flask_cors": "flask-cors", "attr": "attrs", "magic": "python-magic",
    "flask": "Flask", "fastapi": "fastapi",
}


def scan_imports(content):
    """Dosyadaki ust duzey import edilen modul adlarini dondurur."""
    names = set()
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("from "):
            parts = s.split()
            if len(parts) > 1 and (parts[1][0].isalpha() or parts[1][0] == "_"):
                names.add(parts[1].split(".")[0])
        elif s.startswith("import "):
            for part in s[7:].split(","):
                tokens = part.strip().split()
                if tokens and (tokens[0][0].isalpha() or tokens[0][0] == "_"):
                    names.add(tokens[0].split(".")[0])
    return names


def build_project_files(content, folder):
    """Import'lara ve framework'e gore (paketler, Procfile satiri) dondurur."""
    stdlib = getattr(sys, "stdlib_module_names", set())
    local = {f[:-3] for f in os.listdir(folder) if f.endswith(".py")}
    pkgs = set()
    for name in scan_imports(content):
        if name in stdlib or name in local:
            continue
        if name == "google":
            if "genai" in content:
                pkgs.add("google-genai")
            continue
        pkgs.add(IMPORT_TO_PIP.get(name, name))

    flask_var = re.search(r"^(\w+)\s*=\s*Flask\(", content, re.M)
    fastapi_var = re.search(r"^(\w+)\s*=\s*FastAPI\(", content, re.M)
    if flask_var:
        pkgs |= {"Flask", "gunicorn"}
    if fastapi_var:
        pkgs |= {"fastapi", "uvicorn"}
    unique = {}
    for p in pkgs:
        unique.setdefault(p.lower(), p)
    return sorted(unique.values(), key=str.lower), flask_var, fastapi_var


def apply_theme(name):
    """Cikti renklerini secilen temaya gore ayarlar."""
    global RED, GREEN, YELLOW, GREY
    t = THEMES.get(name, THEMES["varsayilan"])
    RED, GREEN, YELLOW, GREY = t["RED"], t["GREEN"], t["YELLOW"], t["GREY"]


def load_snippets():
    try:
        with open(SNIPPET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_snippets(data):
    try:
        with open(SNIPPET_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"{RED}Snippet kaydedilemedi: {e}{RESET}")
        return False


def walk_text_files():
    """Proje klasorundeki okunabilir metin dosyalarini (adres, icerik) olarak verir."""
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            try:
                if os.path.getsize(full) > 1_000_000:
                    continue
                with open(full, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except (OSError, UnicodeDecodeError):
                continue
            yield os.path.relpath(full), lines


def is_yes(answer):
    return answer.strip().lower() in ("e", "evet", "y", "yes")


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        print(f"{YELLOW}Uyari: config okunamadi ({e}){RESET}")
        return {}


def save_config(cfg):
    try:
        # Dosya en bastan 600 izniyle olusturulur (API anahtari herkese acik kalmaz)
        fd = os.open(CONFIG_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        os.chmod(CONFIG_PATH, 0o600)
        return True
    except OSError as e:
        print(f"{RED}Config kaydedilemedi: {e}{RESET}")
        return False


def load_settings():
    saved = load_config().get("settings", {})
    color = str(saved.get("banner_color", DEFAULT_SETTINGS["banner_color"]))
    if color in BANNER_COLORS or (color.isdigit() and 0 <= int(color) <= 255):
        SETTINGS["banner_color"] = color
    styles = saved.get("banner_styles", DEFAULT_SETTINGS["banner_styles"])
    if isinstance(styles, list):
        SETTINGS["banner_styles"] = [x for x in styles if x in BANNER_STYLES]
    SETTINGS["auto_save"] = bool(saved.get("auto_save", DEFAULT_SETTINGS["auto_save"]))


def store_settings():
    cfg = load_config()
    cfg["settings"] = dict(SETTINGS)
    return save_config(cfg)


def get_api_key():
    return os.environ.get("GEMINI_API_KEY") or load_config().get("api_key")


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"{RED}{t('file_not_found', path=path)}{RESET}")
    except IsADirectoryError:
        print(f"{RED}Bu bir klasor, dosya degil: {path}{RESET}")
    except UnicodeDecodeError:
        print(f"{RED}Dosya UTF-8 metin formatinda degil: {path}{RESET}")
    except OSError as e:
        print(f"{RED}Dosya okunamadi: {e}{RESET}")
    return None


def write_file(path, content):
    try:
        folder = os.path.dirname(os.path.abspath(path))
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except OSError as e:
        print(f"{RED}Dosya yazilamadi: {e}{RESET}")
        return False


def get_save_dir():
    """Codex kayit klasorunu dondurur: Termux'ta /storage/emulated/0/Codex, yoksa ~/Codex."""
    for base in (SAVE_BASE_CANDIDATES if PLATFORM == "termux" else []):
        if not os.path.isdir(base):
            continue
        target = os.path.join(base, SAVE_DIR_NAME)
        try:
            os.makedirs(target, exist_ok=True)
            test_path = os.path.join(target, ".codex_test")
            with open(test_path, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(test_path)
            return target
        except OSError as e:
            print(f"{YELLOW}{target} kullanilamadi: {e}{RESET}")
    # Android depolama yok (normal Linux vb.): kullanicinin ev klasorunde calis
    fallback = os.path.join(os.path.expanduser("~"), SAVE_DIR_NAME)
    try:
        os.makedirs(fallback, exist_ok=True)
        return fallback
    except OSError:
        return None


def resolve_save_path(name, folder, ext):
    """Sadece ad verilirse Codex klasorune, yol verilirse o yola kaydeder.
    Uzanti yazilmadiysa dilin uzantisini ekler."""
    name = os.path.expanduser(name.strip())
    if not os.path.splitext(name)[1]:
        name = f"{name}.{ext}"
    if os.path.dirname(name):
        return name
    return os.path.join(folder, name)


# Uzanti -> calistirma komutu (Termux'ta kurulu olmasi gerekir)
RUN_HINTS = {
    "py": "python", "js": "node", "php": "php", "sh": "bash",
    "rb": "ruby", "pl": "perl", "lua": "lua", "go": "go run",
}

# Uzanti -> sozdizimi kontrolu. Arac sistemde yoksa kontrol atlanir.
# Dosya yolu komutun sonuna eklenir.
SYNTAX_CHECKERS = {
    "py": [sys.executable, "-c",
           "import ast,sys; ast.parse(open(sys.argv[1], encoding='utf-8').read())"],
    "js": ["node", "--check"],
    "php": ["php", "-l"],
    "sh": ["bash", "-n"],
    "rb": ["ruby", "-c"],
    "pl": ["perl", "-c"],
    "lua": ["luac", "-p"],
    "go": ["gofmt", "-e"],
    "c": ["gcc", "-fsyntax-only"],
    "cpp": ["g++", "-fsyntax-only"],
}


def check_syntax(path):
    """Dosyanin sozdizimini kontrol eder ve sonucu ekrana yazar."""
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    name = os.path.basename(path)

    if ext == "json":
        try:
            with open(path, encoding="utf-8") as f:
                json.load(f)
        except (OSError, ValueError) as e:
            print(f"{RED}[FAIL] {name}: JSON hatasi: {e}{RESET}")
            return False
        print(f"{GREEN}[PASS] {name}: JSON gecerli{RESET}")
        return True

    cmd = SYNTAX_CHECKERS.get(ext)
    if not cmd:
        return None
    if not shutil.which(cmd[0]):
        print(f"{GREY}[CHECK] {cmd[0]} kurulu degil, sozdizimi kontrolu atlandi.{RESET}")
        return None

    print(f"{GREY}[CHECK] sozdizimi kontrol ediliyor: {name}{RESET}")
    try:
        result = subprocess.run(cmd + [path], capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"{YELLOW}[CHECK] kontrol calistirilamadi: {e}{RESET}")
        return None

    if result.returncode == 0:
        print(f"{GREEN}[PASS] {name}: sozdizimi dogru{RESET}")
        return True
    output = ((result.stdout or "") + (result.stderr or "")).strip()
    print(f"{RED}[FAIL] {name}: sozdizimi hatasi{RESET}")
    if output:
        print(output[:800])
    return False


def run_command_for(path):
    """Dosya turune gore calistirma komutunu dondurur (yoksa None)."""
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    if ext == "html":
        return open_command(path)
    if ext == "py":
        return f"{shell_quote(sys.executable)} {shell_quote(path)}"
    hint = RUN_HINTS.get(ext)
    if not hint:
        return None
    return f"{hint} {shell_quote(path)}"


def print_saved(path):
    print(f"{GREEN}{t('saved', path=path)}{RESET}")
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    if ext == "html":
        print(f"{GREY}{t('open_hint', cmd=open_command(path))}{RESET}")
    elif ext in RUN_HINTS:
        print(f"{GREY}Calistirmak icin: {RUN_HINTS[ext]} {path}{RESET}")
    check_syntax(path)


def parse_code_blocks(text):
    """[(dil_etiketi, kod), ...] listesi dondurur."""
    return [
        (lang.strip().lower(), code)
        for lang, code in re.findall(r"```([^\n]*)\n(.*?)```", text, re.S)
    ]


LAUNCH_CMD_RE = re.compile(
    r"^\s*(\$\s*)?(python3?|pip3?|node|npx|bash|sh|php|ruby|perl|lua|go|cd|chmod|pkg|apt|npm|\./|termux-\S+)(\s|$)"
)


def is_launch_block(lang, code):
    """'python dosya.py' gibi sadece baslatma/kurulum komutu iceren blok mu?"""
    if lang not in ("", "bash", "sh", "shell", "console", "zsh", "text", "txt"):
        return False
    if code.lstrip().startswith("#!"):
        return False
    lines = [l.strip() for l in code.strip().splitlines()
             if l.strip() and not l.strip().startswith("#")]
    if not lines:
        return True
    return len(lines) <= 3 and all(LAUNCH_CMD_RE.match(l) for l in lines)


def pick_main_block(blocks):
    """Baslatma komutlarini atlar, en buyuk (asil) kod blogunu dondurur: (lang, code)."""
    if not blocks:
        return None
    real = [b for b in blocks if not is_launch_block(b[0], b[1])]
    if real:
        return max(real, key=lambda b: len(b[1]))
    return blocks[-1]


def guess_filename(text, ext):
    """Yanittaki 'python x.py' veya `x.py` ifadelerinden dosya adini tahmin eder."""
    patterns = [
        r"(?:python3?|node|php|ruby|perl|lua|bash|sh|go run)\s+([\w\-./]+\." + re.escape(ext) + r")\b",
        r"`([\w\-./]+\." + re.escape(ext) + r")`",
        r"\b([\w\-]+\." + re.escape(ext) + r")\b",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return os.path.basename(m.group(1))
    return f"codex_{datetime.now():%Y%m%d_%H%M%S}.{ext}"


def unique_path(folder, name):
    """Dosya varsa ustune yazmaz; _2, _3 ... ekler."""
    path = os.path.join(folder, name)
    base, ext = os.path.splitext(name)
    n = 2
    while os.path.exists(path):
        path = os.path.join(folder, f"{base}_{n}{ext}")
        n += 1
    return path


COMMENT_PREFIX = {
    "py": "# ", "sh": "# ", "yaml": "# ", "yml": "# ", "rb": "# ", "pl": "# ",
    "r": "# ", "ps1": "# ", "toml": "# ",
    "js": "// ", "jsx": "// ", "ts": "// ", "tsx": "// ", "java": "// ",
    "c": "// ", "h": "// ", "cpp": "// ", "cs": "// ", "go": "// ", "rs": "// ",
    "kt": "// ", "php": "// ", "dart": "// ", "swift": "// ", "scala": "// ",
    "sql": "-- ", "lua": "-- ",
}


def add_signature(code, ext):
    """Kodun ustune '# Codex By Klaus' yorumunu ekler (yoksa)."""
    if ext in ("html", "vue", "xml"):
        line = f"<!-- {SIGNATURE} -->"
    elif ext in ("css", "scss"):
        line = f"/* {SIGNATURE} */"
    elif ext in COMMENT_PREFIX:
        line = COMMENT_PREFIX[ext] + SIGNATURE
    else:
        return code
    lines = code.split("\n")
    if any(SIGNATURE.lower() in l.lower() for l in lines[:4]):
        return code
    at = 0
    if lines and lines[0].startswith("#!"):
        at = 1
    elif lines and lines[0].strip().startswith("<?php"):
        at = 1
    lines.insert(at, line)
    return "\n".join(lines)


def fetch_live_models(client):
    """API'deki kullanilabilir Gemini sohbet modellerinin adlarini dondurur.
    Basarisiz olursa None doner."""
    try:
        names = set()
        for m in client.models.list():
            name = (getattr(m, "name", "") or "").split("/", 1)[-1]
            if not name.startswith("gemini-"):
                continue
            if any(k in name for k in EXCLUDE_KEYWORDS):
                continue
            actions = getattr(m, "supported_actions", None)
            if actions is not None and "generateContent" not in actions:
                continue
            names.add(name)
        return sorted(names)
    except Exception:
        return None


class RequestTimeout(Exception):
    """Gemini istegi REQUEST_TIMEOUT suresinde yanit vermedi."""


def call_with_timeout(fn, timeout):
    """fn'i arka planda calistirir. Sure dolarsa RequestTimeout firlatir.
    Bekleme join ile yapildigi icin Ctrl+C her zaman calisir."""
    box = {}

    def target():
        try:
            box["value"] = fn()
        except Exception as e:
            box["error"] = e

    worker = threading.Thread(target=target, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        raise RequestTimeout(f"{timeout} sn icinde yanit gelmedi")
    if "error" in box:
        raise box["error"]
    return box.get("value")


def is_model_missing(e):
    """Model adi degismis veya kaldirilmis mi (404 / NOT_FOUND)?"""
    code = getattr(e, "code", None) or getattr(e, "status_code", None)
    return code == 404 or "NOT_FOUND" in str(e).upper()


def is_limit_error(e):
    """Kota/limit veya gecici kapasite hatalarini tespit eder (model adi hatasi haric)."""
    code = getattr(e, "code", None) or getattr(e, "status_code", None)
    msg = str(e).upper()
    return (
        code in (429, 503)
        or "RESOURCE_EXHAUSTED" in msg
        or "QUOTA" in msg
        or "RATE LIMIT" in msg
        or "UNAVAILABLE" in msg
        or "OVERLOADED" in msg
    )


# ----------------------------------------------------------------------
# Ana uygulama
# ----------------------------------------------------------------------
class CodexApp:
    def __init__(self):
        self.client = None
        self.history = []
        self.files = {}
        self.last_reply = ""
        self.exhausted = {}
        self.usage = {}
        self.tokens = {"in": 0, "out": 0}
        self.last_edit = None
        self.last_run = None
        self.aliases = load_config().get("aliases", {})
        self.current_model = DEFAULT_MODELS[0]
        self.models = list(DEFAULT_MODELS)
        self.selected = load_config().get("gemini_model")
        saved = load_config().get("provider", "gemini")
        self.provider = saved if saved in PROVIDERS else "gemini"

    # ---------- Model secimi ----------
    @property
    def model(self):
        now = time.time()
        chain = self.chain()
        for m in chain:
            t = self.exhausted.get(m)
            if t is None or now - t > COOLDOWN_SECONDS:
                self.exhausted.pop(m, None)
                return m
        return chain[0]

    def chain(self):
        """Denenecek sira: secili model varsa basta, sonra canli liste sirasi."""
        models = list(self.models) or list(DEFAULT_MODELS)
        if self.selected in models:
            models.remove(self.selected)
            models.insert(0, self.selected)
        return models

    def mark_exhausted(self, model):
        self.exhausted[model] = time.time()

    def next_model_after(self, model):
        now = time.time()
        chain = self.chain()
        if model in chain:
            idx = chain.index(model)
            candidates = chain[idx + 1:] + chain[:idx]
        else:
            candidates = chain
        for m in candidates:
            t = self.exhausted.get(m)
            if t is None or now - t > COOLDOWN_SECONDS:
                return m
        return None

    def refresh_models(self, announce=False, force=False):
        """API'den canli model listesini alir. Model kontrolu yapilmaz; daha once
        404 verip kaldirilan modeller listeye alinmaz. force=True ise bu kara liste sifirlanir."""
        if not self.client:
            return
        live = fetch_live_models(self.client)
        if live is None:
            if announce:
                print(f"{YELLOW}Model listesi alinamadi, mevcut liste kullaniliyor.{RESET}")
            return
        if not live:
            if announce:
                print(f"{YELLOW}API'de kullanilabilir Gemini modeli bulunamadi.{RESET}")
            return

        cfg = load_config()
        if force:
            cfg.pop("verified", None)
            save_config(cfg)
        dead = {n for n, ok in cfg.get("verified", {}).get("results", {}).items() if ok is False}

        ok = [n for n in live if n not in dead]
        preferred = [m for m in DEFAULT_MODELS if m in ok]
        others = sorted((m for m in ok if m not in DEFAULT_MODELS), reverse=True)
        new = preferred + others

        for m in self.models:
            if m not in new:
                self.exhausted.pop(m, None)
        self.models = new

        if self.selected and self.selected not in new:
            print(f"{YELLOW}Secili model su an kullanilamiyor: {self.selected}. Otomatik secime donuldu.{RESET}")
            self.clear_selected()
        if announce:
            print(f"{GREY}Model listesi guncel ({len(new)} model).{RESET}")

    def drop_model(self, model):
        """Adi degismis/kaldirilmis modeli listeden cikarir ve dogrulama sonucunu gunceller."""
        self.models = [m for m in self.models if m != model]
        self.exhausted.pop(model, None)
        cfg = load_config()
        verified = cfg.get("verified", {})
        verified.setdefault("results", {})[model] = False
        cfg["verified"] = verified
        save_config(cfg)
        if self.selected == model:
            self.clear_selected()
        if not self.models:
            self.models = list(DEFAULT_MODELS)

    def set_selected(self, name):
        self.selected = name
        cfg = load_config()
        cfg["gemini_model"] = name
        save_config(cfg)

    def clear_selected(self):
        self.selected = None
        cfg = load_config()
        cfg.pop("gemini_model", None)
        save_config(cfg)

    def set_provider(self, name):
        self.provider = name
        cfg = load_config()
        cfg["provider"] = name
        save_config(cfg)

    # ---------- API ----------
    def _make_client(self, key):
        try:
            self.client = genai.Client(api_key=key)
            return True
        except Exception as e:
            print(f"{RED}Gemini istemcisi olusturulamadi: {e}{RESET}")
            self.client = None
            return False

    def ensure_client(self):
        if self.client:
            return True
        key = get_api_key()
        if not key:
            print(f"{YELLOW}{t('no_key')}{RESET}")
            return False
        return self._make_client(key)

    def build_system(self):
        base = BASE_SYSTEM if LANG == "tr" else BASE_SYSTEM_EN
        parts = [base, f"Calisma dizini: {os.getcwd()}"]
        for name, content in self.files.items():
            parts.append(
                f"=== DOSYA: {name} ===\n{content}\n=== DOSYA SONU: {name} ==="
            )
        return "\n\n".join(parts)

    def _ask_taklagpt(self, message, offer_save=True):
        """TaklaGPT API'sine tek bir istek gonderir. Sohbet gecmisi tasinmaz."""
        url = f"{TAKLA_API_URL}?{urllib.parse.urlencode({'prompt': message})}"
        if len(url) > TAKLA_MAX_URL:
            print(f"{YELLOW}Mesaj TaklaGPT icin cok uzun (GET istegi sinirini asiyor). "
                  f"Kisaltin ya da /model gemini ile devam edin.{RESET}")
            return None

        print(f"{GREY}{t('thinking')}{RESET}")
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"{RED}TaklaGPT'ye ulasilamadi: {e}{RESET}")
            return None

        text = data.get("response") if isinstance(data, dict) else None
        if not text:
            print(f"{RED}TaklaGPT gecerli yanit vermedi: {data}{RESET}")
            return None

        self.last_reply = text
        print(f"{RED}{BOLD}CODEX [TaklaGPT 1.0] >{RESET}\n{text}\n")
        print(f"{RED}{BOLD}{SIGNATURE}{RESET}\n")
        if offer_save:
            self.offer_save(text)
        return text

    def trim_history(self):
        """Gecmisi son MAX_HISTORY_MESSAGES mesajla sinirlar. Gecmis her zaman
        kullanici mesajiyla baslar (API bunu bekler)."""
        if len(self.history) > MAX_HISTORY_MESSAGES:
            self.history = self.history[-MAX_HISTORY_MESSAGES:]
        while self.history and self.history[0].role != "user":
            self.history.pop(0)

    def ask(self, message, offer_save=True):
        if self.provider == "taklagpt":
            return self._ask_taklagpt(message, offer_save)
        if not self.ensure_client():
            return None

        self.history.append(
            types.Content(role="user", parts=[types.Part(text=message)])
        )
        self.trim_history()
        print(f"{GREY}{t('thinking')}{RESET}")

        text = None
        model = self.model
        start_model = model
        while model is not None:
            try:
                response = call_with_timeout(
                    lambda m=model: self.client.models.generate_content(
                        model=m,
                        contents=self.history,
                        config=types.GenerateContentConfig(
                            system_instruction=self.build_system()
                        ),
                    ),
                    REQUEST_TIMEOUT,
                )
                um = getattr(response, "usage_metadata", None)
                if um is not None:
                    self.tokens["in"] += getattr(um, "prompt_token_count", 0) or 0
                    self.tokens["out"] += getattr(um, "candidates_token_count", 0) or 0
                text = response.text or "(bos yanit)"
                self.current_model = model
                self.usage[model] = self.usage.get(model, 0) + 1
                break
            except RequestTimeout as e:
                self.mark_exhausted(model)
                nxt = self.next_model_after(model)
                print(f"{YELLOW}{model} yanit vermedi ({e}).{RESET}")
                if nxt is None:
                    print(f"{RED}Hicbir model zamaninda yanit vermedi. Tekrar deneyin.{RESET}")
                    break
                print(f"{GREY}Sonraki modele geciliyor: {nxt}{RESET}")
                model = nxt
                continue
            except Exception as e:
                if is_model_missing(e):
                    nxt = self.next_model_after(model)
                    self.drop_model(model)
                    print(f"{YELLOW}Model artik kullanilamiyor, listeden kaldirildi: {model} (geri almak icin /model yenile){RESET}")
                    if nxt is None:
                        print(f"{RED}Kullanilabilir baska model kalmadi.{RESET}")
                        break
                    model = nxt
                    continue
                if is_limit_error(e):
                    self.mark_exhausted(model)
                    nxt = self.next_model_after(model)
                    if nxt is None:
                        print(f"{RED}{t('all_limited')}{RESET}")
                        break
                    model = nxt
                    continue
                print(f"{RED}{t('api_error', model=model, err=e)}{RESET}")
                break

        if text is None:
            self.history.pop()
            return None

        self.history.append(
            types.Content(role="model", parts=[types.Part(text=text)])
        )
        self.last_reply = text
        if model != start_model:
            print(f"{YELLOW}{t('model_changed', model=model)}{RESET}")
        print(f"{RED}{BOLD}CODEX [{model}] >{RESET}\n{text}\n")
        print(f"{RED}{BOLD}{SIGNATURE}{RESET}\n")

        if offer_save:
            self.offer_save(text)
        return text

    # ---------- Kaydetme (e derse otomatik Codex klasorune) ----------
    def offer_save(self, text):
        picked = pick_main_block(parse_code_blocks(text))
        if not picked:
            return
        lang, code = picked
        ext = EXT_MAP.get(lang, "txt")

        if not SETTINGS.get("auto_save"):
            answer = input(
                f"{YELLOW}{t('save_prompt', folder=SAVE_DIR_NAME)}{RESET}"
            )
            if not is_yes(answer):
                return

        folder = get_save_dir()
        if folder is None:
            print(f"{RED}{t('storage_missing')}{RESET}")
            return

        path = unique_path(folder, guess_filename(text, ext))
        if write_file(path, add_signature(code, ext)):
            print_saved(path)

    # ---------- Komutlar ----------
    def cmd_tree(self, arg):
        parts = arg.split()
        root = parts[0] if parts else "."
        depth = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 3
        if not os.path.isdir(root):
            print(f"{RED}Klasor bulunamadi: {root}{RESET}")
            return
        for line in tree_lines(root, max_depth=depth):
            print(line)

    def cmd_find(self, arg):
        needle = arg.strip().lower()
        if not needle:
            print(f"{YELLOW}{t('usage_word')}: /find <metin>{RESET}")
            return
        found = 0
        for dirpath, dirnames, filenames in os.walk("."):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
            for fname in filenames:
                full = os.path.join(dirpath, fname)
                try:
                    if os.path.getsize(full) > 1_000_000:
                        continue
                    with open(full, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except (OSError, UnicodeDecodeError):
                    continue
                for num, line in enumerate(lines, 1):
                    if needle in line.lower():
                        rel = os.path.relpath(full)
                        print(f"{GREEN}{rel}{RESET}:{GREY}{num}{RESET}: {line.strip()[:120]}")
                        found += 1
                        if found >= 100:
                            print(f"{GREY}... ilk 100 sonuc gosterildi{RESET}")
                            return
        if not found:
            print(f"{GREY}Sonuc yok.{RESET}")

    def cmd_diff(self, _arg):
        if not self.last_edit:
            print(f"{GREY}Henuz /edit ile yapilan bir degisiklik yok.{RESET}")
            return
        show_diff(self.last_edit["old"], self.last_edit["new"], self.last_edit["path"])

    def cmd_undo(self, _arg):
        if not self.last_edit:
            print(f"{GREY}Geri alinacak degisiklik yok.{RESET}")
            return
        path = self.last_edit["path"]
        bak = path + ".bak"
        if not os.path.exists(bak):
            print(f"{YELLOW}Yedek bulunamadi: {bak}{RESET}")
            return
        if not is_yes(input(f"{YELLOW}{path} yedekten geri alinsin mi? [e/H]: {RESET}")):
            print(t("cancelled"))
            return
        try:
            shutil.copy2(bak, path)
        except OSError as e:
            print(f"{RED}Geri alinamadi: {e}{RESET}")
            return
        print(f"{GREEN}Geri alindi: {path}{RESET}")
        self.last_edit = None

    def cmd_history(self, _arg):
        if not self.history:
            print(f"{GREY}Sohbet gecmisi bos.{RESET}")
            return
        for i, c in enumerate(self.history, 1):
            who = "Sen" if c.role == "user" else "CODEX"
            text = (c.parts[0].text or "").strip().replace("\n", " ")
            print(f"{GREY}{i:>3}.{RESET} {BOLD}{who}:{RESET} {text[:70]}")

    def cmd_export(self, arg):
        if not self.history:
            print(f"{GREY}Kaydedilecek sohbet yok.{RESET}")
            return
        folder = get_save_dir()
        if folder is None:
            print(f"{RED}{t('storage_missing')}{RESET}")
            return
        name = arg.strip() or f"codex_sohbet_{datetime.now():%Y%m%d_%H%M%S}"
        path = resolve_save_path(name, folder, "md")
        path = unique_path(os.path.dirname(path), os.path.basename(path))
        parts = ["# Codex sohbeti", ""]
        for c in self.history:
            who = "Sen" if c.role == "user" else "CODEX"
            parts += [f"## {who}", "", c.parts[0].text or "", ""]
        if write_file(path, "\n".join(parts)):
            print(f"{GREEN}Sohbet kaydedildi: {path}{RESET}")

    def cmd_save_chat(self, arg):
        if not self.history:
            print(f"{GREY}Kaydedilecek sohbet yok.{RESET}")
            return
        name = safe_chat_name(arg) or f"sohbet_{datetime.now():%Y%m%d_%H%M%S}"
        os.makedirs(CHAT_DIR, exist_ok=True)
        path = os.path.join(CHAT_DIR, name + ".json")
        data = {
            "history": [{"role": c.role, "text": c.parts[0].text or ""} for c in self.history],
            "files": self.files,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"{RED}Sohbet kaydedilemedi: {e}{RESET}")
            return
        print(f"{GREEN}Sohbet kaydedildi: {name}{RESET}")
        print(f"{GREY}Yuklemek icin: /load {name}{RESET}")

    def cmd_load(self, arg):
        names = []
        if os.path.isdir(CHAT_DIR):
            names = sorted(n[:-5] for n in os.listdir(CHAT_DIR) if n.endswith(".json"))
        name = safe_chat_name(arg)
        if not name:
            if not names:
                print(f"{GREY}Kayitli sohbet yok.{RESET}")
                return
            print(f"{BOLD}Kayitli sohbetler{RESET}")
            for n in names:
                print(f"  {n}")
            print(f"{GREY}Yuklemek icin: /load <ad>{RESET}")
            return
        path = os.path.join(CHAT_DIR, name + ".json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            print(f"{RED}Sohbet yuklenemedi: {e}{RESET}")
            return
        saved = data.get("history", [])
        self.history = [
            types.Content(role=h["role"], parts=[types.Part(text=h["text"])]) for h in saved
        ]
        self.files = data.get("files", {})
        print(f"{GREEN}Sohbet yuklendi: {name} ({len(self.history)} mesaj){RESET}")

    def cmd_test(self, arg):
        cmd = arg.strip() or detect_test_command()
        if not cmd:
            print(f"{YELLOW}Test komutu bulunamadi. {t('usage_word')}: /test <komut>{RESET}")
            return
        print(f"{GREY}Test komutu: {cmd}{RESET}")
        self.cmd_run(cmd)

    def cmd_fix(self, _arg):
        if not self.last_run:
            print(f"{GREY}Once /run veya /test ile bir komut calistirin.{RESET}")
            return
        if self.last_run["code"] == 0:
            print(f"{GREY}Son komut basarili (cikis kodu 0), duzeltilecek hata gorunmuyor.{RESET}")
            return
        self.ask(
            f"Su komutu calistirdim: `{self.last_run['cmd']}`\n"
            f"Cikis kodu: {self.last_run['code']}\n"
            f"Cikti:\n```\n{self.last_run['output'][:20000]}\n```\n"
            "Hatanin nedenini bul ve duzeltmeyi uygula. Dosya degisikligi gerekiyorsa "
            "degisen dosyanin tamamini TEK bir kod blogu icinde ver ve hangi dosya oldugunu belirt.",
            offer_save=True,
        )

    def cmd_explain(self, arg):
        if not arg:
            print(f"{YELLOW}{t('usage_word')}: /explain <dosya_yolu>{RESET}")
            return
        content = read_file(arg)
        if content is None:
            return
        self.ask(
            f"Dosya: {arg}\n\n```\n{content[:MAX_FILE_CHARS]}\n```\n\n"
            "Bu dosyayi Turkce, kisa ve anlasilir sekilde acikla: ne ise yariyor, "
            "ana parcalari neler, dikkat edilmesi gereken bir sey varsa belirt.",
            offer_save=False,
        )

    def cmd_usage(self, _arg):
        tok = self.tokens
        if not tok["in"] and not tok["out"]:
            print(f"{GREY}Bu oturumda henuz token bilgisi yok (TaklaGPT token bilgisi vermez).{RESET}")
            return
        print(f"{BOLD}Bu oturum token kullanimi{RESET}")
        print(f"  Giris (prompt): {tok['in']}")
        print(f"  Cikis (yanit):  {tok['out']}")
        print(f"  Toplam:         {tok['in'] + tok['out']}")
        print(f"{GREY}Not: Gemini API'nin bildirdigi degerler.{RESET}\n")

    def cmd_ask_file(self, arg):
        parts = arg.split(maxsplit=1)
        if len(parts) < 2:
            print(f"{YELLOW}{t('usage_word')}: /ask-file <dosya_yolu> <soru>{RESET}")
            return
        path, question = parts
        content = read_file(path)
        if content is None:
            return
        self.ask(
            f"Dosya: {path}\n\n```\n{content[:MAX_FILE_CHARS]}\n```\n\nSoru: {question}",
            offer_save=False,
        )

    def cmd_run_file(self, arg):
        path = arg.strip()
        if not path:
            print(f"{YELLOW}{t('usage_word')}: /run-file <dosya_yolu>{RESET}")
            return
        if not os.path.exists(path):
            print(f"{RED}{t('file_not_found', path=path)}{RESET}")
            return
        command = run_command_for(path)
        if command is None:
            print(f"{YELLOW}Bu dosya turu icin calistirma komutu tanimli degil.{RESET}")
            return
        if os.path.splitext(path)[1].lower() == ".html":
            print(f"{GREY}Tarayicida aciliyor...{RESET}")
            if PLATFORM == "windows":
                subprocess.Popen(command, shell=True)
                return
        self.cmd_run(command)

    def cmd_lint(self, arg):
        path = arg.strip()
        if not path:
            print(f"{YELLOW}{t('usage_word')}: /lint <dosya_yolu>{RESET}")
            return
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        cmd = LINTERS.get(ext)
        if not cmd:
            print(f"{YELLOW}Bu dosya turu icin linter tanimli degil.{RESET}")
            return
        if not shutil.which(cmd[0]):
            print(f"{YELLOW}{cmd[0]} kurulu degil. Kurup tekrar deneyin.{RESET}")
            return
        try:
            result = subprocess.run(cmd + [path], capture_output=True, text=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError) as e:
            print(f"{RED}Linter calistirilamadi: {e}{RESET}")
            return
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        if result.returncode == 0 and not output:
            print(f"{GREEN}Sorun bulunamadi: {path}{RESET}")
        else:
            print(output or f"{RED}Linter hata kodu dondurdu: {result.returncode}{RESET}")

    def cmd_format(self, arg):
        path = arg.strip()
        if not path:
            print(f"{YELLOW}{t('usage_word')}: /format <dosya_yolu>{RESET}")
            return
        content = read_file(path)
        if content is None:
            return
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        cmd = FORMATTERS.get(ext)
        if not cmd:
            print(f"{YELLOW}Bu dosya turu icin bicimlendirici tanimli degil.{RESET}")
            return
        if not shutil.which(cmd[0]):
            print(f"{YELLOW}{cmd[0]} kurulu degil. Kurup tekrar deneyin.{RESET}")
            return

        tmpdir = tempfile.mkdtemp()
        tmp = os.path.join(tmpdir, os.path.basename(path))
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        try:
            result = subprocess.run(cmd + [tmp], capture_output=True, text=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError) as e:
            print(f"{RED}Bicimlendirici calistirilamadi: {e}{RESET}")
            return
        if result.returncode != 0:
            print(f"{RED}Bicimlendirici hata verdi:\n{result.stderr.strip()}{RESET}")
            return
        with open(tmp, "r", encoding="utf-8") as f:
            formatted = f.read()
        if formatted == content:
            print(f"{GREY}Dosya zaten bicimli.{RESET}")
            return

        show_diff(content, formatted, path)
        if not is_yes(input(f"{YELLOW}{path} bu bicimle yazilsin mi? [e/H]: {RESET}")):
            print(t("not_saved"))
            return
        if os.path.exists(path):
            try:
                shutil.copy2(path, path + ".bak")
            except OSError as e:
                print(f"{YELLOW}Yedek alinamadi: {e}{RESET}")
        if write_file(path, formatted):
            print(f"{GREEN}Bicimlendirildi: {path}{RESET}")
            self.last_edit = {"path": path, "old": content, "new": formatted}

    def cmd_commit(self, arg):
        check = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                               capture_output=True, text=True)
        if check.returncode != 0:
            print(f"{YELLOW}Bu klasor bir git deposu degil.{RESET}")
            return
        status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True).stdout.strip()
        if not status:
            print(f"{GREY}Commit edilecek degisiklik yok.{RESET}")
            return
        print(f"{BOLD}Degisen dosyalar{RESET}")
        print(status)

        message = arg.strip()
        if not message:
            diff = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True).stdout
            reply = self.ask(
                "Asagidaki git degisiklikleri icin kisa bir commit mesaji yaz. "
                "Sadece mesajin kendisini tek satir olarak ver, Ingilizce ve en fazla 72 karakter.\n"
                f"```\n{diff[:8000]}\n```",
                offer_save=False,
            )
            if not reply:
                return
            lines = [l.strip().strip("`\"'") for l in reply.splitlines() if l.strip()]
            message = lines[0] if lines else ""
            if not message:
                print(f"{RED}Commit mesaji alinamadi.{RESET}")
                return

        if not is_yes(input(f"{YELLOW}Commit mesaji: {message}\nBu mesajla commit atilsin mi? [e/H]: {RESET}")):
            print("Commit iptal edildi.")
            return
        subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
        result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
        output = ((result.stdout or "") + (result.stderr or "")).strip()
        print(output or "(cikti yok)")

    def cmd_todo(self, _arg):
        found = 0
        for rel, lines in walk_text_files():
            for num, line in enumerate(lines, 1):
                if re.search(r"\b(TODO|FIXME|XXX)\b", line):
                    print(f"{GREEN}{rel}{RESET}:{GREY}{num}{RESET}: {line.strip()[:120]}")
                    found += 1
                    if found >= 200:
                        print(f"{GREY}... ilk 200 sonuc gosterildi{RESET}")
                        return
        if not found:
            print(f"{GREY}TODO, FIXME veya XXX bulunamadi.{RESET}")

    def cmd_secrets(self, _arg):
        found = 0
        for rel, lines in walk_text_files():
            for num, line in enumerate(lines, 1):
                for label, pattern in SECRET_PATTERNS:
                    for m in re.finditer(pattern, line):
                        masked = m.group(0)[:6] + "***"
                        print(f"{RED}{label}{RESET} {GREEN}{rel}{RESET}:{GREY}{num}{RESET}: {masked}")
                        found += 1
        if found:
            print(f"{YELLOW}{found} olasi gizli deger bulundu. Bunlari commit etmeden once kaldirin.{RESET}")
        else:
            print(f"{GREEN}Olasi gizli deger bulunamadi.{RESET}")

    def cmd_template(self, arg):
        key = arg.strip().lower()
        if not key:
            print(f"{BOLD}Sablonlar{RESET}")
            for name, (fname, _) in TEMPLATES.items():
                print(f"  {name:<10} {GREY}-> {fname}{RESET}")
            print(f"{GREY}{t('usage_word')}: /template <ad>{RESET}")
            return
        if key not in TEMPLATES:
            print(f"{YELLOW}Bilinmeyen sablon. Liste icin /template yazin.{RESET}")
            return
        fname, code = TEMPLATES[key]
        if os.path.exists(fname):
            if not is_yes(input(f"{YELLOW}{fname} zaten var. Uzerine yazilsin mi? [e/H]: {RESET}")):
                print(t("cancelled"))
                return
        ext = os.path.splitext(fname)[1].lstrip(".")
        if write_file(fname, add_signature(code, ext)):
            print_saved(os.path.abspath(fname))

    def cmd_snippet(self, arg):
        parts = arg.split(maxsplit=1)
        sub = parts[0].lower() if parts else ""
        rest = parts[1].strip() if len(parts) > 1 else ""
        data = load_snippets()

        if not sub or sub == "liste":
            if not data:
                print(f"{GREY}Kayitli snippet yok. Kaydetmek icin: /snippet kaydet <ad>{RESET}")
                return
            for name, item in sorted(data.items()):
                print(f"  {name}  {GREY}({item.get('lang', 'txt')}){RESET}")
            return
        if sub == "kaydet":
            if not rest:
                print(f"{YELLOW}{t('usage_word')}: /snippet kaydet <ad>{RESET}")
                return
            picked = pick_main_block(parse_code_blocks(self.last_reply))
            if not picked:
                print(f"{YELLOW}Kaydedilecek kod yok. Once bir kod isteyin.{RESET}")
                return
            data[rest] = {"lang": picked[0], "code": picked[1]}
            if save_snippets(data):
                print(f"{GREEN}Snippet kaydedildi: {rest}{RESET}")
            return
        if sub == "sil":
            if rest in data:
                del data[rest]
                save_snippets(data)
                print(f"{GREEN}Snippet silindi: {rest}{RESET}")
            else:
                print(f"{YELLOW}Bu ad yok: {rest}{RESET}")
            return
        name = arg.strip()
        if name not in data:
            print(f"{YELLOW}Snippet bulunamadi: {name}{RESET}")
            return
        print(f"{BOLD}{name}{RESET} {GREY}({data[name].get('lang', 'txt')}){RESET}")
        print(data[name]["code"])

    def cmd_alias(self, arg):
        parts = arg.split(maxsplit=1)
        if not parts:
            if not self.aliases:
                print(f"{GREY}Takma ad yok. Ornek: /alias /t /test{RESET}")
                return
            for k, v in sorted(self.aliases.items()):
                print(f"  {k}  ->  {v}")
            return
        if parts[0] == "sil" and len(parts) > 1:
            name = parts[1].strip()
            if name not in self.aliases:
                print(f"{YELLOW}Bu takma ad yok: {name}{RESET}")
                return
            del self.aliases[name]
        else:
            if len(parts) < 2:
                print(f"{YELLOW}{t('usage_word')}: /alias <ad> <komut>  veya  /alias sil <ad>{RESET}")
                return
            name, target = parts[0], parts[1].strip()
            builtin = {c.split()[0] for c, _ in COMMAND_HELP} | {"/quit", "/exit", "/q"}
            if not name.startswith("/") or name in builtin:
                print(f"{YELLOW}Bu ad kullanilamaz. Ornek: /alias /t /test{RESET}")
                return
            if not target.startswith("/"):
                print(f"{YELLOW}Hedef bir komut olmali (/ ile baslamali).{RESET}")
                return
            self.aliases[name] = target
        cfg = load_config()
        cfg["aliases"] = self.aliases
        save_config(cfg)
        print(f"{GREEN}Takma adlar guncellendi.{RESET}")

    def cmd_context(self, _arg):
        chars = sum(len(c.parts[0].text or "") for c in self.history)
        system_chars = len(self.build_system())
        total = chars + system_chars
        print(f"{BOLD}Modele giden baglam{RESET}")
        print(f"  Saglayici: {self.provider}")
        if self.provider == "gemini":
            print(f"  Model: {self.model}")
        print(f"  Sohbet mesaji: {len(self.history)} ({chars} karakter)")
        print(f"  Yuklu dosyalar: {len(self.files)}")
        for name, content in self.files.items():
            print(f"    {name} ({len(content)} karakter)")
        print(f"  Sistem talimati: {system_chars} karakter")
        print(f"{GREY}  Tahmini token: ~{total // 4} (karakter / 4 yaklasimi){RESET}")

    def cmd_theme(self, arg):
        name = arg.strip().lower()
        if not name:
            print(f"{BOLD}Temalar{RESET}")
            current = load_config().get("theme", "varsayilan")
            for theme_name in THEMES:
                mark = f"{GREEN}AKTIF{RESET}" if theme_name == current else "     "
                print(f"  {mark}  {theme_name}")
            print(f"{GREY}{t('usage_word')}: /theme <ad>{RESET}")
            return
        if name not in THEMES:
            print(f"{YELLOW}Bilinmeyen tema. Secenekler: {', '.join(THEMES)}{RESET}")
            return
        apply_theme(name)
        cfg = load_config()
        cfg["theme"] = name
        save_config(cfg)
        print(f"{GREEN}Tema degisti: {name}{RESET}")

    def cmd_render(self, arg):
        path = arg.strip()
        if not path:
            print(f"{YELLOW}{t('usage_word')}: /render <dosya_yolu>{RESET}")
            return
        if not path.endswith(".py") or not os.path.exists(path):
            print(f"{RED}Python dosyasi bulunamadi: {path}{RESET}")
            return
        content = read_file(path)
        if content is None:
            return

        var_match = re.search(r"^(\w+)\s*=\s*Flask\(", content, re.M)
        if not var_match:
            print(f"{YELLOW}Bu dosyada Flask uygulamasi bulunamadi (app = Flask(...) satiri yok).{RESET}")
            return
        var = var_match.group(1)
        folder = os.path.dirname(os.path.abspath(path))
        folder_rel = os.path.relpath(folder)
        module = os.path.splitext(os.path.basename(path))[0]
        start_cmd = f"gunicorn {module}:{var} --bind 0.0.0.0:$PORT"

        # 1) Kod: app.run iceren __main__ blogunu kaldir
        new_content = content
        block = re.search(r'^if __name__ == ["\']__main__["\']:.*\Z', content, re.S | re.M)
        if block and "app.run" in block.group(0):
            new_content = content[:block.start()].rstrip() + "\n"

        # 2) requirements.txt: yoksa olustur, varsa eksikleri ekle
        req_path = os.path.join(folder, "requirements.txt")
        existing = ""
        if os.path.exists(req_path):
            existing = read_file(req_path) or ""
        names = {
            l.strip().split("==")[0].split(">=")[0].strip().lower()
            for l in existing.splitlines() if l.strip() and not l.strip().startswith("#")
        }
        missing = [p for p in ("Flask", "gunicorn") if p.lower() not in names]
        if missing:
            base = existing.rstrip() + "\n" if existing.strip() else ""
            if write_file(req_path, base + "".join(f"{p}\n" for p in missing)):
                print(f"{GREEN}requirements.txt guncellendi (eklenen: {', '.join(missing)}){RESET}")
        else:
            print(f"{GREY}requirements.txt zaten uygun.{RESET}")

        # 3) render.yaml: yoksa olustur
        yaml_path = os.path.join(folder, "render.yaml")
        if os.path.exists(yaml_path):
            print(f"{GREY}render.yaml zaten var, degistirilmedi.{RESET}")
        else:
            service = re.sub(r"[^a-z0-9-]", "-", os.path.basename(folder).lower()).strip("-") or "web-app"
            yaml_text = (
                "services:\n"
                "  - type: web\n"
                f"    name: {service}\n"
                "    runtime: python\n"
                "    plan: free\n"
                "    buildCommand: pip install -r requirements.txt\n"
                f"    startCommand: {start_cmd}\n"
            )
            if write_file(yaml_path, yaml_text):
                print(f"{GREEN}render.yaml olusturuldu: {yaml_path}{RESET}")

        # 4) Kod degisikligi: onayla ve yaz
        if new_content != content:
            print(f"\n{GREY}--- degisiklikler ---{RESET}")
            show_diff(content, new_content, path)
            if is_yes(input(f"{YELLOW}{path} Render icin guncellensin mi? [e/H]: {RESET}")):
                if os.path.exists(path):
                    try:
                        shutil.copy2(path, path + ".bak")
                        print(f"{GREY}Yedek alindi: {path}.bak{RESET}")
                    except OSError as e:
                        print(f"{YELLOW}Yedek alinamadi: {e}{RESET}")
                if write_file(path, new_content):
                    print(f"{GREEN}Kod guncellendi: {path}{RESET}")
                    check_syntax(path)
                    self.last_edit = {"path": path, "old": content, "new": new_content}
            else:
                print("Kod degistirilmedi.")
        else:
            print(f"{GREY}Kodda app.run blogu yok, degisiklik gerekmedi.{RESET}")

        print(f"\n{BOLD}Render ayarlari{RESET}")
        print(f"  Build command: pip install -r requirements.txt")
        print(f"  Start command: {start_cmd}")
        if folder_rel != ".":
            print(f"  {YELLOW}Root Directory: {folder_rel}  (Render panelinde bu klasoru secin){RESET}")
        print(f"{GREY}Not: Dosyalari GitHub'a yukleyin; Render depodan otomatik deploy eder.{RESET}\n")

    def cmd_vds(self, arg):
        path = arg.strip()
        if not path:
            print(f"{YELLOW}{t('usage_word')}: /vds <dosya_yolu>  (ornek: /vds main.py){RESET}")
            return
        if not path.endswith(".py") or not os.path.exists(path):
            print(f"{RED}Python dosyasi bulunamadi: {path}{RESET}")
            return
        content = read_file(path)
        if content is None:
            return

        folder = os.path.dirname(os.path.abspath(path))
        module = os.path.splitext(os.path.basename(path))[0]
        pkgs, flask_var, fastapi_var = build_project_files(content, folder)

        # requirements.txt: yoksa olustur, varsa eksikleri ekle
        req_path = os.path.join(folder, "requirements.txt")
        existing = read_file(req_path) if os.path.exists(req_path) else ""
        existing = existing or ""
        have = {
            l.strip().split("==")[0].split(">=")[0].strip().lower()
            for l in existing.splitlines() if l.strip() and not l.strip().startswith("#")
        }
        missing = [p for p in pkgs if p.lower() not in have]
        if missing or not existing:
            base = existing.rstrip() + "\n" if existing.strip() else ""
            write_file(req_path, base + "".join(f"{p}\n" for p in (missing or pkgs)))
        print(f"{GREEN}requirements.txt hazir ({len(pkgs)} paket){RESET}")

        # Procfile
        proc_path = os.path.join(folder, "Procfile")
        if flask_var:
            proc = f"web: gunicorn {module}:{flask_var.group(1)} --bind 0.0.0.0:$PORT"
        elif fastapi_var:
            proc = f"web: uvicorn {module}:{fastapi_var.group(1)} --host 0.0.0.0 --port $PORT"
        else:
            proc = f"worker: python {os.path.basename(path)}"
        if os.path.exists(proc_path):
            print(f"{GREY}Procfile zaten var, degistirilmedi.{RESET}")
        elif write_file(proc_path, proc + "\n"):
            print(f"{GREEN}Procfile olusturuldu: {proc}{RESET}")

        # Zip: Codex/projeler klasorune
        save_root = get_save_dir()
        if save_root is None:
            print(f"{RED}{t('storage_missing')}{RESET}")
            return
        projeler = os.path.join(save_root, "projeler")
        os.makedirs(projeler, exist_ok=True)
        zip_name = f"{safe_chat_name(module) or 'proje'}_{datetime.now():%Y%m%d_%H%M%S}.zip"
        zip_path = unique_path(projeler, zip_name)

        skip_dirs = {"__pycache__", "node_modules", "venv", ".venv", ".git"}
        projeler_abs = os.path.abspath(projeler)
        count = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for dirpath, dirnames, filenames in os.walk(folder):
                dirnames[:] = [
                    d for d in dirnames
                    if not d.startswith(".") and d not in skip_dirs
                    and os.path.abspath(os.path.join(dirpath, d)) != projeler_abs
                ]
                for fname in filenames:
                    if fname.endswith((".zip", ".bak", ".pyc")) or fname.startswith("."):
                        continue
                    full = os.path.join(dirpath, fname)
                    if os.path.getsize(full) > 20_000_000:
                        continue
                    z.write(full, os.path.relpath(full, folder))
                    count += 1

        print(f"{GREEN}Proje zip olarak kaydedildi ({count} dosya): {zip_path}{RESET}")
        print(f"\n{BOLD}VDS'te calistirmak icin{RESET}")
        print(f"  unzip {zip_path} -d proje && cd proje")
        print("  python3 -m venv venv && source venv/bin/activate")
        print("  pip install -r requirements.txt")
        if flask_var or fastapi_var:
            print(f"  {proc.split(': ', 1)[1]}")
        else:
            print(f"  python {os.path.basename(path)}")
        print(f"{GREY}Not: Procfile icin honcho ya da foreman, kalici calistirma icin systemd onerilir.{RESET}\n")

    def cmd_help(self, arg):
        key = arg.strip().lower()
        if not key:
            print(f"{BOLD}{t('help_title')}{RESET}")
            print(f"{GREY}{t('help_usage')}{RESET}\n")
            names = sorted(DETAILED_HELP)
            for i in range(0, len(names), 4):
                print("  " + "  ".join(f"{n:<14}" for n in names[i:i + 4]))
            print()
            return
        if not key.startswith("/"):
            key = "/" + key
        text = detailed_help_text(key)
        if text is None:
            print(f"{YELLOW}{t('help_none', key=key)}{RESET}")
            print(f"{GREY}{t('all_cmds_hint')}{RESET}")
            return
        print(f"{GREEN}{BOLD}{key}{RESET}")
        print(text)
        print()

    def cmd_cmds(self, _arg):
        print(f"{RED}{BOLD}{t('commands_title')}{RESET}")
        items = localized_commands()
        width = max(len(cmd) for cmd, _ in items) + 2
        for cmd, desc in items:
            print(f"  {GREEN}{cmd.ljust(width)}{RESET}{desc}")
        print()

    def cmd_limit(self, _arg):
        now = time.time()
        active = self.model
        print(f"{BOLD}Model limitleri{RESET}")
        for m in self.chain():
            t = self.exhausted.get(m)
            left = COOLDOWN_SECONDS - (now - t) if t is not None else 0
            used = self.usage.get(m, 0)
            if t is not None and left > 0:
                status = f"{RED}LIMIT DOLU{RESET}"
                info = f"yenilenme: {fmt_duration(left)}"
            elif m == active:
                status = f"{GREEN}AKTIF{RESET}"
                info = "kullanima hazir"
            else:
                status = f"{YELLOW}HAZIR{RESET}"
                info = "sirada bekliyor"
            print(f"  {m}\n    {status}  {GREY}{info} | bu oturumda {used} istek{RESET}")

        try:
            from zoneinfo import ZoneInfo
            from datetime import timedelta
            pt = datetime.now(ZoneInfo("America/Los_Angeles"))
            reset = (pt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            remaining = (reset - pt).total_seconds()
            local = reset.astimezone().strftime("%H:%M")
            print(f"\n{GREY}Gunluk kota sifirlanmasi: {fmt_duration(remaining)} sonra (yerel saat {local}){RESET}")
        except Exception:
            print(f"\n{GREY}Gunluk kota her gun Pasifik saatiyle gece yarisi sifirlanir.{RESET}")
        print(f"{GREY}Not: Gemini API kalan istek sayisini vermez. Sureler Codex'in kendi "
              f"takibidir (limit dolunca {COOLDOWN_SECONDS // 60} dk bekletilir).{RESET}\n")

    def _settings_show(self):
        color = SETTINGS["banner_color"]
        styles = ", ".join(SETTINGS["banner_styles"]) or "yok"
        print()
        print_logo()
        print(f"\n{BOLD}Ayarlar{RESET}")
        auto = "acik" if SETTINGS.get("auto_save") else "kapali"
        print(f"  Renk: {color}   Stil: {styles}   Otomatik kayit: {auto}\n")

    def _settings_color(self):
        names = list(BANNER_COLORS)
        for i, n in enumerate(names, 1):
            print(f"  {i}) {BANNER_COLORS[n]}{n}{RESET}")
        print(f"  {len(names) + 1}) 0-255 renk kodu gir")
        choice = input("Renk sec (bos = iptal): ").strip()
        if not choice:
            return
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            SETTINGS["banner_color"] = names[int(choice) - 1]
        elif choice.isdigit() and int(choice) == len(names) + 1:
            code = input("Kod (0-255): ").strip()
            if code.isdigit() and 0 <= int(code) <= 255:
                SETTINGS["banner_color"] = code
            else:
                print(f"{YELLOW}Gecersiz kod.{RESET}")
                return
        elif choice in BANNER_COLORS:
            SETTINGS["banner_color"] = choice
        else:
            print(f"{YELLOW}Gecersiz secim.{RESET}")
            return
        store_settings()

    def _settings_style(self):
        names = list(BANNER_STYLES)
        while True:
            for i, n in enumerate(names, 1):
                mark = "x" if n in SETTINGS["banner_styles"] else " "
                print(f"  {i}) [{mark}] {BANNER_STYLES[n]}{n}{RESET}")
            choice = input("Ac/kapat icin numara (bos = bitti): ").strip()
            if not choice:
                return
            if choice.isdigit() and 1 <= int(choice) <= len(names):
                n = names[int(choice) - 1]
                if n in SETTINGS["banner_styles"]:
                    SETTINGS["banner_styles"].remove(n)
                else:
                    SETTINGS["banner_styles"].append(n)
                store_settings()
                print()
                print_logo()
                print()
            else:
                print(f"{YELLOW}Gecersiz secim.{RESET}")

    def cmd_settings(self, arg):
        # Hizli kullanim: /settings renk mavi   |   /settings stil bold italic
        parts = arg.split()
        if parts and parts[0] == "renk" and len(parts) > 1:
            if parts[1] in BANNER_COLORS or (parts[1].isdigit() and 0 <= int(parts[1]) <= 255):
                SETTINGS["banner_color"] = parts[1]
                store_settings()
                print_header(self.model)
            else:
                print(f"{YELLOW}Renkler: {', '.join(BANNER_COLORS)} veya 0-255{RESET}")
            return
        if parts and parts[0] == "otomatik" and len(parts) > 1:
            value = parts[1].lower()
            if value in ("ac", "acik", "on", "e"):
                SETTINGS["auto_save"] = True
            elif value in ("kapat", "kapali", "off", "h"):
                SETTINGS["auto_save"] = False
            else:
                print(f"{YELLOW}{t('usage_word')}: /settings otomatik ac|kapat{RESET}")
                return
            store_settings()
            state = "acik" if SETTINGS["auto_save"] else "kapali"
            print(f"{GREEN}Otomatik kayit {state}.{RESET}")
            return
        if parts and parts[0] == "stil":
            wanted = [x for x in parts[1:] if x in BANNER_STYLES]
            SETTINGS["banner_styles"] = wanted
            store_settings()
            print_header(self.model)
            return

        while True:
            self._settings_show()
            print("  1) Banner rengi")
            print("  2) Banner stili (bold / italic / underline / dim)")
            print("  3) Otomatik kayit (kod yazinca Codex klasorune kaydet)")
            print("  4) Varsayilana don")
            print("  0) Cik")
            choice = input("Secim: ").strip()
            if choice == "1":
                self._settings_color()
            elif choice == "2":
                self._settings_style()
            elif choice == "3":
                SETTINGS["auto_save"] = not SETTINGS.get("auto_save", False)
                store_settings()
                state = "acildi" if SETTINGS["auto_save"] else "kapatildi"
                print(f"{GREEN}Otomatik kayit {state}.{RESET}")
            elif choice == "4":
                SETTINGS.update(DEFAULT_SETTINGS)
                SETTINGS["banner_styles"] = list(DEFAULT_SETTINGS["banner_styles"])
                store_settings()
            elif choice in ("0", ""):
                print_header(self.model)
                return

    def cmd_new(self, _arg):
        self.history = []
        self.files = {}
        self.last_reply = ""
        self.exhausted = {}
        self.usage = {}
        self.last_edit = None
        self.last_run = None
        print_header(self.model)
        print(f"{GREEN}{t('history_cleared')}{RESET}\n")

    def cmd_model(self, arg):
        labels = {
            "gemini": "Google Gemini (resmi API, /key ile anahtar gerekir)",
            "taklagpt": "TaklaGPT 1.0 (ta-kla-gpt-api)",
        }
        choice = arg.strip()
        lowered = choice.lower()

        if not choice:
            self.ensure_client()
            self.refresh_models(announce=True)
            print(f"{BOLD}Saglayicilar{RESET}")
            for name in PROVIDERS:
                mark = f"{GREEN}AKTIF{RESET}" if name == self.provider else "     "
                print(f"  {mark}  {name}  {GREY}{labels[name]}{RESET}")
            print(f"\n{BOLD}Gemini modelleri (API'den canli){RESET}")
            active = self.model
            for m in self.chain():
                if m == self.selected:
                    mark = f"{GREEN}SECILI{RESET}"
                elif m == active and self.selected is None:
                    mark = f"{GREEN}AKTIF {RESET}"
                else:
                    mark = "      "
                print(f"  {mark}  {m}")
            print(f"\n{GREY}Model secmek: /model <ad>   Otomatige donmek: /model auto{RESET}\n")
            return

        if lowered == "yenile":
            self.ensure_client()
            self.refresh_models(announce=True, force=True)
            return

        if lowered == "auto":
            self.clear_selected()
            self.set_provider("gemini")
            print(f"{GREEN}Model secimi otomatige alindi (Gemini).{RESET}")
            return

        if lowered in PROVIDERS:
            self.set_provider(lowered)
            print(f"{GREEN}Aktif saglayici: {labels[lowered]}{RESET}")
            if lowered == "taklagpt":
                print(f"{GREY}Not: TaklaGPT sohbet gecmisi ve dosya baglamini almaz; her istek bagimsizdir.{RESET}")
            return

        self.ensure_client()
        self.refresh_models()
        if choice in self.models:
            self.set_provider("gemini")
            self.set_selected(choice)
            print(f"{GREEN}Aktif model: {choice}{RESET}")
            return
        print(f"{YELLOW}Bilinmeyen model veya saglayici: {choice}. Liste icin /model yazin.{RESET}")

    def cmd_key(self, _arg):
        key = getpass.getpass(t("api_key_prompt")).strip()
        if not key:
            print(t("cancelled"))
            return
        cfg = load_config()
        cfg["api_key"] = key
        if save_config(cfg):
            print(f"{GREEN}{t('api_key_saved', path=CONFIG_PATH)}{RESET}")
        self._make_client(key)
        self.refresh_models()

    def cmd_list(self, arg):
        path = arg or "."
        try:
            entries = sorted(
                os.listdir(path),
                key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower()),
            )
        except OSError as e:
            print(f"{RED}Klasor listelenemedi: {e}{RESET}")
            return

        print(f"{BOLD}{os.path.abspath(path)}{RESET}")
        if not entries:
            print("  (bos)")
        for name in entries:
            full = os.path.join(path, name)
            if os.path.isdir(full):
                print(f"  {GREEN}{name}/{RESET}")
            else:
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = 0
                print(f"  {name}  {GREY}({size} B){RESET}")

    def cmd_open(self, arg):
        if not arg:
            print(f"{YELLOW}{t('usage_word')}: /open <dosya_yolu>{RESET}")
            return
        content = read_file(arg)
        if content is None:
            return
        if len(content) > MAX_FILE_CHARS:
            print(f"{YELLOW}Dosya cok buyuk; ilk {MAX_FILE_CHARS} karakter alindi.{RESET}")
            content = content[:MAX_FILE_CHARS]
        self.files[arg] = content
        print(f"{GREEN}Yuklendi: {arg} ({len(content)} karakter){RESET}")
        if self.provider == "taklagpt":
            print(f"{YELLOW}Uyari: TaklaGPT dosya baglamini kullanmaz. Bu dosya TaklaGPT "
                  f"yanitlarina dahil edilmeyecek. Dosya baglami icin /model gemini kullanin.{RESET}")

    def cmd_edit(self, arg):
        if not arg:
            print(f"{YELLOW}{t('usage_word')}: /edit <dosya_yolu>{RESET}")
            return
        content = read_file(arg)
        if content is None:
            return

        if self.provider == "taklagpt":
            print(f"{YELLOW}Uyari: TaklaGPT dosyayi guvenilir sekilde duzenleyemez. Dosya "
                  f"icerigi kisa degilse istek sinirini asabilir ve yanit dosyayi bozabilir. "
                  f"Duzenleme icin /model gemini kullanin.{RESET}")

        instruction = input("Talimat (ne degissin?): ").strip()
        if not instruction:
            print(t("cancelled"))
            return

        message = (
            f"Dosya: {arg}\n\nMevcut icerik:\n```\n{content}\n```\n\n"
            f"Istek: {instruction}\n\n"
            "Dosyanin tamamini degisiklikler uygulanmis halde TEK bir kod blogu "
            "icinde ver. Kod disinda kisa bir aciklama ekleyebilirsin."
        )
        reply = self.ask(message, offer_save=False)
        if not reply:
            return

        picked = pick_main_block(parse_code_blocks(reply))
        if not picked:
            print(f"{YELLOW}Yanitta kod blogu bulunamadi, dosya degistirilmedi.{RESET}")
            return
        new_code = add_signature(picked[1], os.path.splitext(arg)[1].lstrip(".").lower())

        print(f"\n{GREY}--- degisiklikler ---{RESET}")
        show_diff(content, new_code, arg)
        print(f"{GREY}--- onizleme sonu ---{RESET}")

        answer = input(f"{YELLOW}{arg} uzerine yazilsin mi? [e/H]: {RESET}")
        if not is_yes(answer):
            print(t("not_saved"))
            return

        if os.path.exists(arg):
            try:
                shutil.copy2(arg, arg + ".bak")
                print(f"{GREY}Yedek alindi: {arg}.bak{RESET}")
            except OSError as e:
                print(f"{YELLOW}Yedek alinamadi: {e}{RESET}")

        if write_file(arg, new_code):
            print(f"{GREEN}Dosya guncellendi: {arg}{RESET}")
            check_syntax(arg)
            self.last_edit = {"path": arg, "old": content, "new": new_code}

    def cmd_save(self, arg):
        picked = pick_main_block(parse_code_blocks(self.last_reply))
        if not picked:
            print(f"{YELLOW}Kaydedilecek kod blogu yok. Once bir istek yapin.{RESET}")
            return

        lang, code = picked
        ext = EXT_MAP.get(lang, "txt")
        folder = get_save_dir()
        if folder is None:
            print(f"{RED}{t('storage_missing')}{RESET}")
            return

        if arg:
            name = arg
        else:
            name = guess_filename(self.last_reply, ext)
        path = resolve_save_path(name, folder, ext)

        if arg and os.path.exists(path):
            if not is_yes(input(f"{YELLOW}{path} zaten var. Uzerine yazilsin mi? [e/H]: {RESET}")):
                print(t("not_saved"))
                return
        elif os.path.exists(path):
            path = unique_path(folder, os.path.basename(path))

        if write_file(path, add_signature(code, ext)):
            print_saved(path)

    def cmd_run(self, arg):
        if not arg:
            print(f"{YELLOW}{t('usage_word')}: /run <komut>{RESET}")
            return

        print(f"{GREY}$ {arg}{RESET}")
        try:
            result = subprocess.run(
                arg,
                shell=True,
                capture_output=True,
                text=True,
                timeout=RUN_TIMEOUT,
                cwd=os.getcwd(),
            )
        except subprocess.TimeoutExpired:
            print(f"{RED}Zaman asimi ({RUN_TIMEOUT} sn){RESET}")
            return
        except OSError as e:
            print(f"{RED}Komut calistirilamadi: {e}{RESET}")
            return

        output = ((result.stdout or "") + (result.stderr or "")).rstrip() or "(cikti yok)"
        self.last_run = {"cmd": arg, "code": result.returncode, "output": output}
        print(output)
        print(f"{GREY}cikis kodu: {result.returncode}{RESET}")

        self.ask(
            f"Su komutu calistirdim: `{arg}`\n"
            f"Cikis kodu: {result.returncode}\n"
            f"Cikti:\n```\n{output[:20000]}\n```\n"
            "Ciktiyi yorumla; hata varsa nedenini acikla ve cozum oner.",
            offer_save=False,
        )

    def cmd_paste(self, _arg):
        print(f"{GREY}Kodu yapistirin. Bitirmek icin yeni bir satira '.end' yazin.{RESET}")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == ".end":
                break
            lines.append(line)

        code = "\n".join(lines)
        if not code.strip():
            print("Bos icerik, iptal edildi.")
            return

        question = input("Bu kodla ne yapayim? (bos = analiz et): ").strip()
        question = question or "Bu kodu analiz et ve acikla."
        self.ask(f"```\n{code}\n```\n\n{question}")

    # ---------- Ana dongu ----------
    def run(self):
        load_settings()
        if not load_config().get("setup_done"):
            setup_wizard()
        load_locale()
        apply_theme(load_config().get("theme", "varsayilan"))
        print_header(self.model)
        if not self.ensure_client():
            print(f"{GREY}{t('need_key')}{RESET}\n")
        else:
            self.refresh_models()

        handlers = {
            "/new": self.cmd_new,
            "/paste": self.cmd_paste,
            "/edit": self.cmd_edit,
            "/open": self.cmd_open,
            "/run": self.cmd_run,
            "/save": self.cmd_save,
            "/list": self.cmd_list,
            "/limit": self.cmd_limit,
            "/settings": self.cmd_settings,
            "/key": self.cmd_key,
            "/model": self.cmd_model,
            "/tree": self.cmd_tree,
            "/find": self.cmd_find,
            "/diff": self.cmd_diff,
            "/undo": self.cmd_undo,
            "/history": self.cmd_history,
            "/export": self.cmd_export,
            "/save-chat": self.cmd_save_chat,
            "/load": self.cmd_load,
            "/test": self.cmd_test,
            "/fix": self.cmd_fix,
            "/explain": self.cmd_explain,
            "/usage": self.cmd_usage,
            "/ask-file": self.cmd_ask_file,
            "/run-file": self.cmd_run_file,
            "/lint": self.cmd_lint,
            "/format": self.cmd_format,
            "/commit": self.cmd_commit,
            "/todo": self.cmd_todo,
            "/secrets": self.cmd_secrets,
            "/template": self.cmd_template,
            "/snippet": self.cmd_snippet,
            "/alias": self.cmd_alias,
            "/context": self.cmd_context,
            "/theme": self.cmd_theme,
            "/render": self.cmd_render,
            "/vds": self.cmd_vds,
            "/help": self.cmd_help,
            "/cmds": self.cmd_cmds,
        }

        while True:
            try:
                raw = input(f"{RED}codex@termux > {RESET}").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{RED}{t('bye')}{RESET}")
                break

            if not raw:
                continue
            if raw in ("/quit", "/exit", "/q"):
                print(f"{RED}{t('bye')}{RESET}")
                break

            head = raw.partition(" ")[0]
            if head in self.aliases:
                raw = (self.aliases[head] + " " + raw[len(head):].strip()).strip()
            name, _, arg = raw.partition(" ")
            arg = arg.strip()

            try:
                if name.startswith("/"):
                    handler = handlers.get(name)
                    if handler:
                        handler(arg)
                    else:
                        print(f"{YELLOW}{t('unknown_cmd', cmd=name)}{RESET}")
                        print(f"{GREY}{t('all_cmds_hint')}{RESET}")
                else:
                    self.ask(raw)
            except KeyboardInterrupt:
                print(f"\n{YELLOW}{t('cancelled')}{RESET}")
            except Exception as e:
                print(f"{RED}Beklenmeyen hata: {e}{RESET}")


if __name__ == "__main__":
    CodexApp().run()
