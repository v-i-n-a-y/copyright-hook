import argparse
import os
import re
import sys

HEADER_SCAN_LIMIT = 15
COPYRIGHT_TEMPLATE = '"""\nCopyright {year} {holder}\n"""'

COPYRIGHT_RE = re.compile(
    r"Copyright\s+(?P<year>\d{4})\s+(?P<holder>.+)", re.IGNORECASE
)


def has_copyright(line: str) -> bool:
    return bool(COPYRIGHT_RE.search(line))


def parse_copyright(line: str):
    m = COPYRIGHT_RE.search(line)
    return m.groupdict() if m else None


def build_notice(year: str, holder: str) -> str:
    return COPYRIGHT_TEMPLATE.format(year=year, holder=holder)


def preview(filepath: str, old: str, new: str):
    print(f"\n--- {filepath}")
    print(f"- {old.rstrip()}")
    print(f"+ {new.rstrip()}")


def find_copyright(lines):
    for i in range(min(len(lines), HEADER_SCAN_LIMIT)):
        if has_copyright(lines[i]):
            return i, parse_copyright(lines[i])
    return None, None


def process_python_file(
    filepath: str,
    dry_run: bool,
    update_holder,
    update_year,
    default_year,
    default_holder,
):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    idx, info = find_copyright(lines)

    if idx is not None:
        if not update_holder and not update_year:
            return

        year = update_year or info["year"]
        holder = update_holder or info["holder"]

        new_notice = build_notice(year, holder) + "\n"

        if dry_run:
            preview(filepath, lines[idx], new_notice)
        else:
            lines[idx] = new_notice

    else:
        new_notice = build_notice(default_year, default_holder) + "\n\n"

        if dry_run:
            preview(filepath, "(no copyright)", new_notice.strip())
        else:
            lines.insert(0, new_notice)

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)


def process_directory(directory: str, args):
    for root, _, files in os.walk(directory):
        for name in files:
            if name.endswith(".py"):
                process_python_file(
                    os.path.join(root, name),
                    args.dry_run,
                    args.update_holder,
                    args.update_year,
                    args.year,
                    args.holder,
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")

    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--update-holder")
    parser.add_argument("--update-year")

    parser.add_argument("--year", required = True)
    parser.add_argument("--holder", required = True)

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        sys.exit("Invalid directory")

    process_directory(args.directory, args)


if __name__ == "__main__":
    main()
