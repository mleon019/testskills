import argparse
import sys
from typing import Optional

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


def _normalize_column_letter(column_letter: str) -> str:
    cleaned = column_letter.strip().upper()
    if not cleaned or not cleaned.isalpha():
        raise ValueError(f"Invalid column letter: {column_letter!r}")
    return cleaned


def write_cell_value(
    spreadsheet_id: str,
    column_letter: str,
    row_number: int,
    value: Optional[str],
    worksheet_name: Optional[str] = None,
) -> str:
    """
    Write a value to a specific cell or, when value is None, only change background formatting.

    Returns the target A1 address (for example I5).
    """
    if row_number < 1:
        raise ValueError("row_number must be >= 1")

    normalized_column = _normalize_column_letter(column_letter)
    cell_address = f"{normalized_column}{row_number}"

    client = gspread.service_account(filename="serviceaccount.json")
    spreadsheet = client.open_by_key(spreadsheet_id)

    if worksheet_name:
        worksheet = spreadsheet.worksheet(worksheet_name)
    else:
        worksheet = spreadsheet.get_worksheet(0)
        if worksheet is None:
            raise ValueError("The spreadsheet does not contain any worksheets.")

    if value is not None:
        worksheet.update(range_name=cell_address, values=[[value]])
    else:
        # Apply a visible highlight without overwriting the cell value.
        worksheet.format(
            cell_address,
            {
                "backgroundColor": {
                    "red": 1.0,
                    "green": 0.95,
                    "blue": 0.8,
                }
            },
        )

    return cell_address


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a value to a Google Sheets cell or only apply cell background formatting."
    )
    parser.add_argument(
        "--spreadsheet-id",
        required=True,
        help="Google Sheets spreadsheet ID.",
    )
    parser.add_argument(
        "column",
        help="Column letter, for example A or I.",
    )
    parser.add_argument(
        "row",
        type=int,
        help="1-indexed row number.",
    )
    parser.add_argument(
        "value",
        nargs="?",
        default=None,
        help="Optional value to write. If omitted, only background formatting is changed.",
    )
    parser.add_argument(
        "worksheet",
        nargs="?",
        default=None,
        help="Optional worksheet/tab name. Uses first worksheet if omitted.",
    )

    args = parser.parse_args()

    try:
        address = write_cell_value(
            spreadsheet_id=args.spreadsheet_id,
            column_letter=args.column,
            row_number=args.row,
            value=args.value,
            worksheet_name=args.worksheet,
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

    print(f"Written to cell {address}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
