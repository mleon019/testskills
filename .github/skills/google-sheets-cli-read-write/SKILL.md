---
name: google-sheets-cli-read-write
description: 'Read and write Google Spreadsheet values using read_sheet.py and write_sheet.py. Use when you need to read a column, read a single cell, write a cell value, apply format-only updates, and verify results with service-account auth.'
argument-hint: 'Operation, spreadsheet id, target column/cell, optional worksheet'
---

# Google Sheets CLI Read/Write

Use this skill to run a repeatable workflow for reading and writing Google Sheets values with the workspace scripts.

## When to Use
- Read non-empty values from a column.
- Read one specific cell value (for example A2).
- Write a value to a specific cell.
- Apply background formatting without overwriting the existing value.
- Verify write operations with a read-back check.

## Required Inputs
- Spreadsheet ID.
- Column letter (A, I, AA, etc.).
- Optional row number for single-cell reads.
- Optional worksheet/tab name.
- Optional value for write operations.

## Preconditions
1. Confirm these files exist in workspace root:
   - `read_sheet.py`
   - `write_sheet.py`
   - `serviceaccount.json`
2. Ensure dependencies are installed:
   - `python -m pip install -r requirements.txt`
3. Ensure the service account has access to the target sheet.
4. Ensure Google Sheets API is enabled for the service account project.

## Procedure
1. Determine operation type.
   - Read full column: use `read_sheet.py` with column only.
   - Read single cell: use `read_sheet.py` with column + row.
   - Write value: use `write_sheet.py` with column + row + value.
   - Format-only update: use `write_sheet.py` with column + row and omit value.
2. Build the command.
   - Read full column:
     - `python read_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> [WORKSHEET]`
   - Read single cell:
     - `python read_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW> [WORKSHEET]`
   - Read as JSON:
     - `python read_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> [ROW_OR_WORKSHEET] [WORKSHEET] --json`
   - Write value:
     - `python write_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW> <VALUE> [WORKSHEET]`
   - Format-only update:
     - First worksheet: `python write_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW>`
     - Named worksheet: `python write_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW> "" <WORKSHEET>`
3. Execute command and inspect output.
4. For writes, verify by reading back the target cell.
   - `python read_sheet.py --spreadsheet-id <SHEET_ID> <COLUMN> <ROW> [WORKSHEET]`
5. If documenting work, capture commands/output in `demo.md` using Showboat.

## Decision Rules
- If the second positional arg for `read_sheet.py` is numeric, treat it as row.
- If the second positional arg for `read_sheet.py` is non-numeric, treat it as worksheet.
- If writing and you must preserve existing text, omit value to trigger format-only behavior.
- If writing format-only to a named worksheet, pass an empty value (`""`) before worksheet.
- If output is needed for automation or parsing, use `--json`.

## Troubleshooting
- Error with API/permission message:
  - Enable Google Sheets API for the service account project.
  - Share the sheet with the service account email in `serviceaccount.json`.
- `ModuleNotFoundError: gspread`:
  - Install requirements in the active environment.
- Unexpected read target:
  - Re-check whether the second positional argument was interpreted as row or worksheet.

## Completion Checks
- Command exits with code 0.
- Read operations return expected row/value pairs.
- Write operations print `Written to cell <A1>.`.
- Post-write read-back confirms the new value in the intended cell.

## Example Prompts
- "Use google-sheets-cli-read-write to read column A from spreadsheet <ID>."
- "Use google-sheets-cli-read-write to read A2 from spreadsheet <ID>."
- "Use google-sheets-cli-read-write to write studentA6 into A6 in spreadsheet <ID>."
- "Use google-sheets-cli-read-write to apply format-only update to B7 without changing value."
