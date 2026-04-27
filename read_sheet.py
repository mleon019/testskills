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
) -> List[Tuple[int, str]]:
    """
    Return non-empty values from a sheet column as (row_number, value) tuples.

    Row numbers are 1-indexed.
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

    values = worksheet.col_values(col_idx)

    if row_number is not None:
        if row_number < 1:
            raise ValueError("row_number must be >= 1")

        if row_number <= len(values):
            value = values[row_number - 1]
            if value.strip() != "":
                return [(row_number, value)]
        return []

    results: List[Tuple[int, str]] = []
    for row_number, value in enumerate(values, start=1):
        if value.strip() != "":
            results.append((row_number, value))

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
        payload = [{"row": row, "value": value} for row, value in rows]
        print(json.dumps(payload, indent=2))
    else:
        for row, value in rows:
            print(f"{row}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
