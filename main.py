import argparse
import csv
import datetime
import json
import sys
from pathlib import Path

import requests


API_URL = "https://deployhoroscope.ru/api/v1/day"

#Запрос, возвращающий гороскоп на текущий день
def fetch_day_horoscope() -> dict:
    r = requests.get(API_URL, timeout=10)
    r.raise_for_status()
    return r.json()

#Собираем дату
def format_date(result: dict) -> str:
    year = result.get("year")
    month = result.get("month", {}).get("id")
    day = result.get("day")

    try:
        return datetime.date(int(year), int(month), int(day)).isoformat()
    except Exception:
        return f"{year}-{month}-{day}"

#Записываем данные в .csv
def write_csv(path: Path, date: str, signs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["date", "id", "name_en", "name_ru", "status", "comment"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for sign in signs:
            writer.writerow(
                {
                    "date": date,
                    "id": sign.get("id"),
                    "name_en": sign.get("name_en"),
                    "name_ru": sign.get("name_ru"),
                    "status": sign.get("status"),
                    "comment": sign.get("comment"),
                }
            )

#главная функция, получающая аргументы, обрабатывающая их и сохраняющая в .csv
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Получить гороскоп")
    parser.add_argument(
        "--out",
        default="horoscopes.csv",
        help="Путь для сохранения CSV (по умолчанию horoscopes.csv)",
    )
    parser.add_argument(
        "--sign",
        help="Показать гороскоп только для одного знака (id, name_en или name_ru)",
    )
    args = parser.parse_args(argv)

    try:
        payload = fetch_day_horoscope()
    except Exception as e:
        print("Не удалось получить данные из API:", e, file=sys.stderr)
        return 1

    result = payload.get("result") or {}
    date_str = format_date(result)
    signs = result.get("signs") or []

    if not signs:
        print("В ответе от API нет списка знаков.")
        return 1

    print(f"Гороскоп на {date_str}")

    def print_sign(sign: dict) -> None:
        status = sign.get("status", "")
        comment = sign.get("comment", "")
        print(f"- {sign.get('name_ru')} ({sign.get('id')}): {status}\n  {comment}\n")

    if args.sign:
        key = args.sign.strip().lower()
        found = None
        for sign in signs:
            if key in {sign.get("id", ""), sign.get("name_en", "").lower(), sign.get("name_ru", "").lower()}:
                found = sign
                break
        if found:
            print_sign(found)
        else:
            print(f"Знак '{args.sign}' не найден в ответе API.")
    else:
        for sign in signs:
            print_sign(sign)

    write_csv(Path(args.out), date_str, signs)
    print(f"Сохранено: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


