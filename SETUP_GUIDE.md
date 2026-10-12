# CODEX Setup Guide (English)

This guide explains how to install CODEX on **Termux (Android)**, **Linux** and **Windows**. Turkish guide: [KURULUM_REHBERI.md](KURULUM_REHBERI.md)

---

## Before you start

On every platform you need:

- **Python 3.10 or newer**
- **git** (optional, needed only for `/commit`)
- **A Gemini API key**: get one for free at [Google AI Studio](https://aistudio.google.com/apikey).

Clone the repository:

```bash
git clone https://github.com/kl45usmik-ai/codex.git
cd codex
```

> Replace `YOUR_USERNAME` with your GitHub username.

---

## 1. Termux (Android)

### Installation

1. Install Termux from **F-Droid** (the Play Store version is outdated).
2. Install the packages:

   ```bash
   pkg update && pkg upgrade
   pkg install python git
   ```

3. Clone the repository and run the install script:

   ```bash
   git clone https://github.com/kl45usmik-ai    /codex.git
   cd codex
   bash install.sh
   ```

4. The commands `codex`, `Codex` and `CODEX` are created. Termux's `$PREFIX/bin` is already in PATH, so nothing else is needed.

### Storage permission for saving files

Run this once so generated code can be saved to a `Codex` folder on your phone:

```bash
termux-setup-storage
```

Tap **Allow** in the permission dialog. Files are saved to `/storage/emulated/0/Codex`.

### First start

```bash
codex
```

The program asks two questions:

- Language: `2` (English) or `1` (Türkçe)
- Platform: `3` (Termux)

Then enter your API key:

```
/key
```

The key is typed in hidden and stored only on your device.

---

## 2. Linux

This guide applies to Ubuntu, Debian, Fedora, Arch and similar distributions. It is also similar on macOS.

### Installation

1. Check that Python and git are installed:

   ```bash
   python3 --version
   git --version
   ```

   If not, install them with your package manager, for example `sudo apt install python3 python3-pip git` on Ubuntu/Debian.

2. Clone the repository and run the install script:

   ```bash
   git clone https://github.com/kl45usmik-ai/codex.git
   cd codex
   bash install.sh
   ```

3. Commands are installed to `~/.local/bin`. If that folder is not in PATH, the script prints the line to add. For example, add this to the end of `~/.bashrc`:

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

   Then open a new terminal or run `source ~/.bashrc`.

### About Python packages

The program installs `google-genai` itself on first run. Recent Debian/Ubuntu versions may block direct pip installs into the system Python. The program retries with `--break-system-packages` automatically. If that still fails, use a virtual environment:

```bash
python3 -m venv ~/codex-venv
source ~/codex-venv/bin/activate
pip install google-genai
```

Then run `codex` from that environment.

### First start

```bash
codex
```

- Language: `2` (English) or `1` (Türkçe)
- Platform: `2` (Linux / macOS)

Then enter your key with `/key`.

---

## 3. Windows

### Installation

1. **Install Python:** download Python 3 from [python.org/downloads](https://www.python.org/downloads/).
   **On the installer screen, tick "Add python.exe to PATH".**

2. **Install git (optional):** [git-scm.com](https://git-scm.com/download/win). Needed only for `/commit`.

3. Clone the repository in PowerShell or Command Prompt:

   ```powershell
   git clone https://github.com/kl45usmik-ai/codex.git
   cd codex
   ```

   Without git, open the repository page on GitHub and choose **Code → Download ZIP**, then extract it.

4. Run the install script. Double-click **`install.bat`** in the folder, or run it in cmd:

   ```
   install.bat
   ```

5. The script installs `codex.cmd` to `%LOCALAPPDATA%\Codex\bin`. If that folder is not in PATH, the script shows a PowerShell command. Run it **once**:

   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:LOCALAPPDATA\Codex\bin", "User")
   ```

   Then open a new Command Prompt or PowerShell window.

### First start

In a new window:

```
codex
```

- Language: `2` (English) or `1` (Türkçe)
- Platform: `1` (Windows)

Then enter your key with `/key`.

> Windows is case-insensitive, so `codex`, `Codex` and `CODEX` all start the program.

---

## First use

After installing and entering your key, try:

```
create a notepad app
```

The model writes the code and checks its syntax, then asks whether to save it. To save automatically:

```
/settings auto on
```

Help:

- `/cmds`: all commands
- `/help /command`: details for one command, for example `/help /edit`

Common commands:

| Command | What it does |
|---|---|
| `/edit file.py` | Changes a file with the model, shows the diff, writes it after approval |
| `/run python file.py` | Runs a command and sends the result to the model |
| `/fix` | Asks the model to fix the last error |
| `/model` | Lists Gemini models; `/model <name>` selects one |
| `/settings` | Language, colors and auto-save settings |

---

## Troubleshooting

**`codex: command not found` (Linux / Termux)**
Did you run `bash install.sh`? Check that the files exist: `ls ~/.local/bin` on Linux, `ls $PREFIX/bin/codex` on Termux. On Linux, `~/.local/bin` must be in PATH.

**`'codex' is not recognized` (Windows)**
Open a new window after changing PATH. If it still fails, run the PowerShell command again and check it.

**Python not found (Windows)**
Was "Add python.exe to PATH" ticked during installation? If not, uninstall Python and install it again with that option.

**Files are not saved (Termux)**
Did you run `termux-setup-storage`? Without storage permission the `Codex` folder cannot be created.

**API error or "all models are rate limited"**
The free Gemini quota is limited. Wait a few minutes or pick another model with `/model`. To enter the key again, use `/key`.

**A model does not respond**
Each request waits 30 seconds, then the next model is tried. You can change this with `REQUEST_TIMEOUT` in `main.py`.

**I chose the wrong language or platform**
Edit `language` (`tr` or `en`) and `platform` (`windows`, `linux` or `termux`) in `~/.codex_config.json`. If the file does not exist, the program asks again on first start.

**`/key` seems to do nothing**
The characters you type are hidden, which is normal. Paste the key and press Enter.

---

## Uninstall

**Termux:**
```bash
rm -f "$PREFIX/bin/"{codex,Codex,CODEX}
```

**Linux / macOS:**
```bash
rm -f ~/.local/bin/{codex,Codex,CODEX}
```

**Windows:** delete the `%LOCALAPPDATA%\Codex` folder and remove the line you added to PATH.

To remove saved settings and data: `~/.codex_config.json`, `~/.codex_chats`, `~/.codex_snippets.json`.

---

## Security

- Never upload your API key to GitHub. It is stored in `~/.codex_config.json` (permission 600 on Linux and Termux).
- Before sharing your code, run `/secrets` to check for keys or passwords left in the files.
