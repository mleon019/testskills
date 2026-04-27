---
name: google-sheets-cli-read-write
description: 'Agent-only workflow: read/write sheet values; read returns background_color; write accepts --bg-color.'
argument-hint: 'spreadsheet-id, column, [row], [value], [--bg-color], [worksheet]'
user-invocable: false
---

# google-sheets-cli-read-write

Assets: `./scripts/read_sheet.py`, `./scripts/write_sheet.py`, `./scripts/requirements.txt`, `./scripts/serviceaccount.json`

Procedure:
1. Install deps: `python -m pip install -r .github/skills/google-sheets-cli-read-write/scripts/requirements.txt`
2. Read
   - Full column: `python ./scripts/read_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> [WORKSHEET]`
   - Single cell: `python ./scripts/read_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW> [WORKSHEET]`
   - JSON: `python ./scripts/read_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> [ROW_OR_WORKSHEET] [WORKSHEET] --json`
     - JSON objects include `background_color` (hex string or null).
3. Write
   - Write value: `python ./scripts/write_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW> <VALUE> [WORKSHEET]`
   - Set background color:`python ./scripts/write_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW> [VALUE] --bg-color "#rrggbb" [WORKSHEET]`
   - To change only color on a named worksheet, pass an empty value before worksheet: `""`.

Routing:
- `read_sheet.py`: second positional numeric => row, else worksheet
- `read_sheet.py` returns rows with `background_color` (hex or null)
- `write_sheet.py` supports `--bg-color` (hex) and preserves value when `value` omitted

Completion checks:
- Read JSON includes `background_color` entries
- Write prints `Written to cell <A1>.` and read-back confirms color/value

Troubleshooting:
- Enable Sheets API and share sheet with service account
- Install `gspread` from bundled requirements
