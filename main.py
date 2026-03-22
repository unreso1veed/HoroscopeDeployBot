import argparse
import csv
import datetime
import sys
from pathlib import Path

import requests


API_ENDPOINTS = {
    "day": "https://deployhoroscope.ru/api/v1/day",
    "month": "https://deployhoroscope.ru/api/v1/month",
}


def fetch_horoscope(endpoint_type: str = "day") -> dict:
    if endpoint_type not in API_ENDPOINTS:
        raise ValueError(f"Unknown endpoint: {endpoint_type}")
    
    url = API_ENDPOINTS[endpoint_type]
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def format_date(result: dict) -> str:
    year = result.get("year")
    month = result.get("month", {})
    day = result.get("day")
    
    month_id = month.get("id") if isinstance(month, dict) else month
    
    try:
        if day:
            return datetime.date(int(year), int(month_id), int(day)).isoformat()
        return datetime.date(int(year), int(month_id), 1).isoformat()
    except (ValueError, TypeError):
        return f"{year}-{month_id}-{day}" if day else f"{year}-{month_id}"


def write_csv(path: Path, date: str, signs: list[dict], endpoint_type: str = "day") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if endpoint_type == "day":
        fieldnames = ["date", "id", "name_en", "name_ru", "status", "comment"]
    else:
        fieldnames = ["date", "id", "name_en", "name_ru"]
        if signs:
            fieldnames += [k for k in signs[0].keys() if k not in fieldnames]
    
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for sign in signs:
            row = {
                "date": date,
                "id": sign.get("id"),
                "name_en": sign.get("name_en"),
                "name_ru": sign.get("name_ru"),
            }
            
            if endpoint_type == "day":
                row["status"] = sign.get("status")
                row["comment"] = sign.get("comment")
            else:
                for key in sign.keys():
                    if key not in row:
                        row[key] = sign.get(key)
            
            writer.writerow(row)


def print_sign(sign: dict) -> None:
    status = sign.get("status", "")
    comment = sign.get("comment", "")
    if status or comment:
        print(f"- {sign.get('name_ru')} ({sign.get('id')}): {status}")
        if comment:
            print(f"  {comment}")
    else:
        print(f"- {sign.get('name_ru')} ({sign.get('id')})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch horoscope from API")
    parser.add_argument(
        "--type",
        choices=["day", "month"],
        default="day",
        help="Horoscope type: 'day' or 'month' (default: day)",
    )
    parser.add_argument(
        "--out",
        help="Output CSV file path (default: day.csv or month.csv)",
    )
    parser.add_argument(
        "--sign",
        help="Filter by zodiac sign (id, name_en, or name_ru)",
    )
    args = parser.parse_args(argv)
    
    if not args.out:
        args.out = f"{args.type}.csv"
    
    try:
        payload = fetch_horoscope(endpoint_type=args.type)
    except Exception as e:
        print(f"Error fetching API: {e}", file=sys.stderr)
        return 1
    
    result = payload.get("result") or {}
    date_str = format_date(result)
    signs = result.get("signs") or []
    
    if not signs:
        print("No horoscope data in response", file=sys.stderr)
        return 1
    
    print(f"Horoscope for {date_str} ({args.type})")
    
    if args.sign:
        key = args.sign.strip().lower()
        found = next(
            (s for s in signs if key in {
                s.get("id", ""),
                s.get("name_en", "").lower(),
                s.get("name_ru", "").lower(),
            }),
            None,
        )
        if found:
            print_sign(found)
        else:
            print(f"Sign '{args.sign}' not found", file=sys.stderr)
            return 1
    else:
        for sign in signs:
            print_sign(sign)
    
    write_csv(Path(args.out), date_str, signs, endpoint_type=args.type)
    print(f"Saved to: {args.out}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



