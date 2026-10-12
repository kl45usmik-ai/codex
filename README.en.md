> Setup guide: [SETUP_GUIDE.md](SETUP_GUIDE.md) · Türkçe kurulum rehberi: [KURULUM_REHBERI.md](KURULUM_REHBERI.md)

# CODEX - AI Code Engine

A code assistant for the terminal, powered by Google Gemini (and optionally TaklaGPT). It writes, edits, runs, lints, formats, tests, commits and deploys code. Works on **Windows, Linux, macOS and Termux (Android)**.

> Türkçe: [README.md](README.md)

## Requirements

- Python 3.10 or newer
- git (optional, for `/commit`)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Installation

### Termux (Android) and Linux / macOS

```bash
git clone https://github.com/kl45usmik-ai/codex.git
cd codex
bash install.sh
```

On Termux, `pkg install python git` first. The script creates the commands `codex`, `Codex` and `CODEX`.
Linux is case-sensitive, so all three spellings are installed. On Termux they go to `$PREFIX/bin` (already in PATH). Elsewhere they go to `~/.local/bin`; if that folder is not in PATH, the script prints the line to add to your shell config.

### Windows

Install Python from python.org and tick **"Add python.exe to PATH"**. Then run `install.bat` (double-click or from cmd). It creates `codex.cmd` in `%LOCALAPPDATA%\Codex\bin`. Windows is case-insensitive, so `codex`, `Codex` and `CODEX` all work. If the folder is not in PATH, run the PowerShell command the script prints once.

After installation, type `codex` (or `Codex` / `CODEX`) in any folder.

> The commands only exist after the install script is run once. Cloning the repository alone does not install them.

## First run: language and platform

The first time you start the program it asks two questions, only once:

1. Language: `1` Türkçe, `2` English
2. Platform: `1` Windows, `2` Linux / macOS, `3` Termux (Android)

The answers are saved in `~/.codex_config.json` (`language` and `platform`). The platform decides how HTML files are opened, how commands are quoted and where files are saved (Termux uses `/storage/emulated/0/Codex`, other systems use `~/Codex`).

Then enter your API key with `/key`.

## Usage

Type a request in plain language, for example `create a notepad app`. The model writes the code, checks its syntax, and asks whether to save it to the Codex folder (or saves it automatically if auto-save is on).

Commands start with `/`. Type `/cmds` for the full list and `/help /command` for details. The main ones:

| Area | Commands |
|---|---|
| Chat | `/new` `/paste` `/history` `/export` `/save-chat` `/load` `/context` `/usage` |
| Files | `/open` `/edit` `/diff` `/undo` `/explain` `/ask-file` `/save` `/list` `/tree` `/find` |
| Run and test | `/run` `/run-file` `/test` `/fix` |
| Quality | `/lint` `/format` `/todo` `/secrets` |
| Git | `/commit` |
| Templates and snippets | `/template` `/snippet` `/alias` |
| Deploy | `/render` (Flask for Render) `/vds` (requirements, Procfile and zip) |
| Models and settings | `/model` `/limit` `/settings` `/theme` `/key` |
| Other | `/help` `/cmds` `/quit` |

### Common workflows

- **New code:** describe what you want. Save it with the prompt, or `/save name.py`.
- **Edit a file:** `/edit app.py`, describe the change, review the diff, approve. A `.bak` backup is made; `/undo` restores it.
- **Run and fix:** `/run python app.py`. If it fails, `/fix` sends the error to the model.
- **Check before publishing:** `/secrets` (look for leaked keys), `/lint`, `/format`.
- **Commit:** `/commit` shows changes, proposes a message, commits after approval. It never pushes.
- **Deploy Flask on Render:** `/render app.py` removes `app.run`, creates `requirements.txt` and `render.yaml`. Push to GitHub and connect the repository in Render.
- **Deploy on a VDS:** `/vds main.py` creates `requirements.txt` and a `Procfile` and zips the project into `Codex/projeler`.

## Models

Gemini models are read live from the API. Models that the API returns 404 for are removed from the list and remembered (`/model refresh` clears this). If the selected model becomes unavailable, the program switches to automatic selection. Rate-limit errors only pause a model for a while.

Each request waits at most `REQUEST_TIMEOUT` seconds (default 30); after that the next model is tried, so you never need Ctrl+C.

Select a model with `/model <name>`, use `/model auto` for automatic selection, or `/model taklagpt` for TaklaGPT.

## Files and privacy

- Your API key is stored only on your machine in `~/.codex_config.json` (permission 600). It is never in the repository. Do not commit that file.
- `.gitignore` already excludes `.bak` backups, `__pycache__` and config files.
- Use `/secrets` before pushing code to a public repository.

## Uninstall

Linux / Termux: `rm -f "$PREFIX/bin/"{codex,Codex,CODEX}` on Termux, or `rm -f ~/.local/bin/{codex,Codex,CODEX}` elsewhere.
Windows: delete `%LOCALAPPDATA%\Codex\bin\codex.cmd`.

## Limitations

- The Gemini free tier has rate limits. When a model is exhausted the program switches models, but heavy use may still run out.
- TaklaGPT does not receive chat history or files, and cannot edit files reliably.
- Not every platform-specific feature has been tested on every system. Please report errors with the full message.

## License

Personal project. Ask the author before reusing it.
