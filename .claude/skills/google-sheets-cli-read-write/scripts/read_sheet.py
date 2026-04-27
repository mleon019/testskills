import argparse
import json
import sys
from typing import List, Optional, Tuple

import gspread


def _format_exception_message(exc: Exception) -> str:
    """Return a useful error message, including chained causes when needed."""
    message = str(exc).strip()
    if message:
        return message

    cause = exc.__cause__
    while cause is not None:
        cause_message = str(cause).strip()
        if cause_message:
            return cause_message
        cause = cause.__cause__

    return f"{type(exc).__name__} (no additional details provided)"


def column_letter_to_index(column_letter: str) -> int:
    """Convert a spreadsheet column letter (e.g. A, I, AA) to a 1-based index."""
    cleaned = column_letter.strip().upper()
    if not cleaned or not cleaned.isalpha():
        raise ValueError(f"Invalid column letter: {column_letter!r}")

    index = 0
    for char in cleaned:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index


def get_column_values(
    spreadsheet_id: str,
    column_letter: str,
    worksheet_name: Optional[str] = None,
    row_number: Optional[int] = None,
) -> List[Tuple[int, str, Optional[str]]]:
    """
    Return values and background colours from a sheet column as
    (row_number, value, background_hex) tuples. Row numbers are 1-indexed.

    Includes rows that are empty but have a background colour set.
    """
    col_idx = column_letter_to_index(column_letter)

    client = gspread.service_account(filename="serviceaccount.json")
    spreadsheet = client.open_by_key(spreadsheet_id)

    if worksheet_name:
        worksheet = spreadsheet.worksheet(worksheet_name)
    else:
        worksheet = spreadsheet.get_worksheet(0)
        if worksheet is None:
            raise ValueError("The spreadsheet does not contain any worksheets.")

    # Fetch sheet metadata with grid data to obtain background colours
    metadata = spreadsheet.fetch_sheet_metadata(params={"includeGridData": True})

    # Find matching sheet metadata by title
    sheet_meta = None
    for s in metadata.get("sheets", []):
        props = s.get("properties", {})
        if props.get("title") == worksheet.title:
            sheet_meta = s
            break

    # Row data may be missing when sheet has no grid data; default to empty
    row_data = []
    if sheet_meta is not None:
        data = sheet_meta.get("data", [])
        if data:
            row_data = data[0].get("rowData", [])

    def _cell_background_hex(cell: dict) -> Optional[str]:
        fmt = cell.get("userEnteredFormat", {})
        bg = fmt.get("backgroundColor")
        if not bg:
            return None
        # backgroundColor values are floats 0..1
        def to_255(f):
            return max(0, min(255, int(round(f * 255))))

        r = to_255(bg.get("red", 0))
        g = to_255(bg.get("green", 0))
        b = to_255(bg.get("blue", 0))
        return f"#{r:02x}{g:02x}{b:02x}"

    results: List[Tuple[int, str, Optional[str]]] = []

    # If a specific row was requested, retrieve only that row
    if row_number is not None:
        if row_number < 1:
            raise ValueError("row_number must be >= 1")

        idx = row_number - 1
        cell = {}
        if idx < len(row_data):
            values = row_data[idx].get("values", [])
            if len(values) >= col_idx:
                cell = values[col_idx - 1]

        value = cell.get("formattedValue") or ""
        bg_hex = _cell_background_hex(cell) if cell else None
        if value.strip() != "" or bg_hex is not None:
            results.append((row_number, value, bg_hex))
        return results

    # No specific row: iterate all available rows from metadata
    for i, rd in enumerate(row_data):
        rownum = i + 1
        values = rd.get("values", [])
        cell = values[col_idx - 1] if len(values) >= col_idx else {}
        value = cell.get("formattedValue") or ""
        bg_hex = _cell_background_hex(cell) if cell else None
        if value.strip() != "" or bg_hex is not None:
            results.append((rownum, value, bg_hex))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read non-empty values from a specific Google Sheets column."
    )
    parser.add_argument(
        "--spreadsheet-id",
        required=True,
        help="Google Sheets spreadsheet ID.",
    )
    parser.add_argument(
        "column",
        help="Column letter to read, for example A or I.",
    )
    parser.add_argument(
        "row_or_worksheet",
        nargs="?",
        default=None,
        help="Optional row number (1-indexed) or worksheet/tab name.",
    )
    parser.add_argument(
        "worksheet",
        nargs="?",
        default=None,
        help="Optional worksheet/tab name when row is provided.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output rows as pretty-printed JSON.",
    )

    args = parser.parse_args()

    row_number: Optional[int] = None
    worksheet_name: Optional[str] = None

    if args.row_or_worksheet is not None:
        if args.row_or_worksheet.isdigit():
            row_number = int(args.row_or_worksheet)
            worksheet_name = args.worksheet
        else:
            if args.worksheet is not None:
                print(
                    "Error: If the second positional argument is a worksheet name, do not provide a third positional argument.",
                    file=sys.stderr,
                )
                return 1
            worksheet_name = args.row_or_worksheet

    try:
        rows = get_column_values(
            spreadsheet_id=args.spreadsheet_id,
            column_letter=args.column,
            worksheet_name=worksheet_name,
            row_number=row_number,
        )
    except Exception as exc:
        print(f"Error: {_format_exception_message(exc)}", file=sys.stderr)
        if isinstance(exc, PermissionError):
            print(
                "Hint: Enable the Google Sheets API for the service account project and "
                "share the sheet with the service account email.",
                file=sys.stderr,
            )
        return 1

    if args.as_json:
        payload = [
            {"row": row, "value": value, "background_color": bg}
            for row, value, bg in rows
        ]
        print(json.dumps(payload, indent=2))
    else:
        for row, value, bg in rows:
            display = value if value.strip() != "" else "(empty)" if bg is not None else ""
            if bg is not None:
                print(f"{row}: {display} [{bg}]")
            else:
                print(f"{row}: {display}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())