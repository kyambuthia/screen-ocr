# Screen OCR -> Codex CLI

Small local CLI tool to:
1. Capture the current screen
2. Send the image to a DeepInfra vision model for OCR
3. Print extracted text to stdout so you can pipe into Codex CLI

## Quick start (Windows PowerShell)

```powershell
cd "C:\Users\classic springs\screen-ocr-codex"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# edit .env and set DEEPINFRA_API_TOKEN
python src/capture_ocr.py --copy --save last_ocr.txt
```

## Use with Codex CLI

```powershell
python src/capture_ocr.py | codex
```

or:

```powershell
$txt = python src/capture_ocr.py
codex "$txt"
```

## Notes

- Default model: `Qwen/Qwen2.5-VL-72B-Instruct`
- You can override with env var `DEEPINFRA_MODEL`.
- The tool captures the **primary monitor** by default.
