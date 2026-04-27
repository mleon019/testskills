# Google Sheets CLI Demo

*2026-04-27T16:53:04Z by Showboat 0.6.1*
<!-- showboat-id: b0cd5207-e5a4-4a7f-a7f6-4c9a29cb4e0f -->

## Overview

This demo documents two Google Sheets CLI scripts in this workspace:

- `read_sheet.py`: reads non-empty values from a selected column, or a single cell by row.
- `write_sheet.py`: writes to a selected cell or applies formatting-only updates.

Both commands:

- authenticate via `gspread.service_account(filename="serviceaccount.json")`
- require `--spreadsheet-id`
- default to the first worksheet when no worksheet name is provided
- print actionable errors, including a hint for Google Sheets API permission/setup issues

## read_sheet.py key features

- Required positional arg: `column`
- Optional positional arg: `row_or_worksheet`
: if numeric, treated as 1-indexed row number; otherwise treated as worksheet name
- Optional positional arg: `worksheet`
: used only when `row_or_worksheet` is numeric
- Optional flag: `--json` for pretty JSON output
- Reads values with `worksheet.col_values(col_idx)` and filters to non-empty values only
- Output:
: default text format `{row}: {value}`
: JSON format `[ { "row": <int>, "value": <string> } ]`

## write_sheet.py key features

- Required positional args: `column`, `row`
- Optional positional args: `value`, `worksheet`
- Builds A1 notation from column + row (for example `I5`)
- If `value` is provided, writes using `worksheet.update(range_name=<addr>, values=[[value]])`
- If `value` is omitted, updates background formatting only and keeps existing cell value
- Success output: `Written to cell <A1>.`

## Example invocations

```powershell
python read_sheet.py --spreadsheet-id <SHEET_ID> A
python read_sheet.py --spreadsheet-id <SHEET_ID> A 2
python read_sheet.py --spreadsheet-id <SHEET_ID> A Sheet1
python read_sheet.py --spreadsheet-id <SHEET_ID> A 2 Sheet1
python read_sheet.py --spreadsheet-id <SHEET_ID> A 2 --json
python write_sheet.py --spreadsheet-id <SHEET_ID> I 5 Hello
python write_sheet.py --spreadsheet-id <SHEET_ID> I 5
```

```python
import subprocess; r=subprocess.run(['c:/GAISE/testskills/.venv/Scripts/python.exe','c:/GAISE/testskills/read_sheet.py','--help'],capture_output=True,text=True); print(r.stdout if r.stdout else r.stderr)
```

```output
usage: read_sheet.py [-h] --spreadsheet-id SPREADSHEET_ID [--json]
                     column [row_or_worksheet] [worksheet]

Read non-empty values from a specific Google Sheets column.

positional arguments:
  column                Column letter to read, for example A or I.
  row_or_worksheet      Optional row number (1-indexed) or worksheet/tab name.
  worksheet             Optional worksheet/tab name when row is provided.

options:
  -h, --help            show this help message and exit
  --spreadsheet-id SPREADSHEET_ID
                        Google Sheets spreadsheet ID.
  --json                Output rows as pretty-printed JSON.

```

```python
import subprocess; r=subprocess.run(['c:/GAISE/testskills/.venv/Scripts/python.exe','c:/GAISE/testskills/write_sheet.py','--help'],capture_output=True,text=True); print(r.stdout if r.stdout else r.stderr)
```

```output
usage: write_sheet.py [-h] --spreadsheet-id SPREADSHEET_ID
                      column row [value] [worksheet]

Write a value to a Google Sheets cell or only apply cell background
formatting.

positional arguments:
  column                Column letter, for example A or I.
  row                   1-indexed row number.
  value                 Optional value to write. If omitted, only background
                        formatting is changed.
  worksheet             Optional worksheet/tab name. Uses first worksheet if
                        omitted.

options:
  -h, --help            show this help message and exit
  --spreadsheet-id SPREADSHEET_ID
                        Google Sheets spreadsheet ID.

```

```python
import subprocess; r=subprocess.run(['c:/GAISE/testskills/.venv/Scripts/python.exe','c:/GAISE/testskills/read_sheet.py','--spreadsheet-id','1LZqrGGenKUehOPihCjnprbPde-KiLfwgtTHiLd0k3lc','A'],capture_output=True,text=True); print(r.stdout if r.stdout else r.stderr)
```

```output
1: Email
2: mleon019@ikasle.ehu.eus
3: lgesteira001@ikasle.ehu.eus
4: prcaj001@ikasle.ehu.eus
5: juanan.pereira@ehu.eus

```

```python
import subprocess; r=subprocess.run(['c:/GAISE/testskills/.venv/Scripts/python.exe','c:/GAISE/testskills/read_sheet.py','--spreadsheet-id','1LZqrGGenKUehOPihCjnprbPde-KiLfwgtTHiLd0k3lc','A','2'],capture_output=True,text=True); print(r.stdout if r.stdout else r.stderr)
```

```output
2: mleon019@ikasle.ehu.eus

```

## Writing studentA6 to cell A6

To write the value `studentA6` into cell `A6` with `write_sheet.py`, run:

```powershell
python write_sheet.py --spreadsheet-id 1LZqrGGenKUehOPihCjnprbPde-KiLfwgtTHiLd0k3lc A 6 studentA6
```

This maps to:

- `column = A`
- `row = 6`
- `value = studentA6`

Expected success output:

`Written to cell A6.`

```python
import subprocess; r=subprocess.run(['c:/GAISE/testskills/.venv/Scripts/python.exe','c:/GAISE/testskills/write_sheet.py','--spreadsheet-id','1LZqrGGenKUehOPihCjnprbPde-KiLfwgtTHiLd0k3lc','A','6','studentA6'],capture_output=True,text=True); print(r.stdout if r.stdout else r.stderr)
```

```output
Written to cell A6.

```
