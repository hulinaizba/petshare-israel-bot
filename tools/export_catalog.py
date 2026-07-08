"""Выгрузка публичного каталога для Mini App (docs/app/catalog.json).

Только публичные поля — никаких телефонов и tg_id.
Запуск: ./venv/bin/python tools/export_catalog.py  (потом git push)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sheets  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "app" / "catalog.json"


def public_photo(value):
    """Отдаём только прямые ссылки на картинки (не телеграмные file_id)."""
    value = str(value or "").strip()
    return value if value.startswith("http") else ""


def main():
    items = []
    for a in sheets.get_animals():
        avg, count = sheets.get_rating(a.get("id", ""))
        items.append({
            "id": str(a.get("id", "")),
            "kind": "animal",
            "name": str(a.get("имя", "")),
            "category": str(a.get("категория", "")),
            "breed": str(a.get("порода", "")),
            "age": str(a.get("возраст", "")),
            "city": str(a.get("город", "")),
            "price_hour": str(a.get("цена_час", "")),
            "price_event": str(a.get("цена_событие", "")),
            "kids": str(a.get("можно_детям", "")),
            "desc": str(a.get("описание", "")),
            "photo": public_photo(a.get("фото_url")),
            "rating": avg,
            "reviews": count,
        })
    for h in sheets.get_horses():
        avg, count = sheets.get_rating(h.get("id", ""))
        items.append({
            "id": str(h.get("id", "")),
            "kind": "horse",
            "name": str(h.get("кличка", "")),
            "category": "Лошади",
            "breed": str(h.get("порода", "")),
            "age": str(h.get("возраст", "")),
            "city": str(h.get("город", "")),
            "price_hour": str(h.get("цена_час", "")),
            "price_event": str(h.get("цена_закат", "")),
            "kids": str(h.get("новичкам", "")),
            "desc": str(h.get("характер", "")),
            "photo": public_photo(h.get("фото")),
            "rating": avg,
            "reviews": count,
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"каталог выгружен: {len(items)} карточек → {OUT}")


if __name__ == "__main__":
    main()
