import re
from pathlib import Path

# === НАСТРОЙКИ ===
INPUT_FILE = "knowledge_base_aliyah_full.txt"   # исходный файл
OUTPUT_FILE = "cleaned_base.txt"                # выходной файл
MIN_LENGTH = 10                                 # минимальная длина строки

# Подстроки, которые нужно удалить (строки с ними не попадут в результат)
EXCLUDE_SUBSTRINGS = [
    "Ссылка:",
    "Дата Парсинга",
    "На этом портале собрана информация",
    "Смотрите также",
    "Вернувшиеся жители",
    "Выходцы из Эфиопии",
    "Узники Сиона",
]

# --- 1. Функции фильтрации ---

def clean_line(line: str) -> str:
    """
    Удаляет все символы, кроме русских букв, цифр, пробелов и базовых знаков препинания.
    """
    cleaned = re.sub(r"[^А-Яа-яЁё0-9\s\.,!\?\-:;\"'()\[\]]+", "", line)
    return cleaned.strip()


def should_exclude(line: str) -> bool:
    """
    Проверяет, содержит ли строка нежелательные подстроки.
    """
    for substr in EXCLUDE_SUBSTRINGS:
        if substr.lower() in line.lower():
            return True
    return False


def is_valid_line(line: str) -> bool:
    """
    Проверяет, что строка подходит под все критерии:
    - содержит кириллицу
    - не короткая
    - не содержит запрещённых подстрок
    """
    if not line or len(line) < MIN_LENGTH:
        return False
    if not re.search(r"[А-Яа-яЁё]", line):
        return False
    if should_exclude(line):
        return False
    return True


# --- 2. Основная функция очистки ---

def clean_file(input_path: str, output_path: str):
    seen = set()
    cleaned_lines = []

    # Проверяем существование исходного файла
    if not Path(input_path).exists():
        print(f"❌ Ошибка: файл '{input_path}' не найден.")
        return

    # Чтение и очистка
    with open(input_path, "r", encoding="utf-8") as infile:
        for raw_line in infile:
            line = clean_line(raw_line)
            if not is_valid_line(line):
                continue
            if line not in seen:
                seen.add(line)
                cleaned_lines.append(line)

    # Запись результата
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(cleaned_lines))

    print("✅ Очистка завершена.")
    print(f"📄 Исходный файл: {input_path}")
    print(f"💾 Очищенный файл: {output_path}")
    print(f"📊 Итог: {len(cleaned_lines)} строк сохранено.")


# --- 3. Точка входа ---

if __name__ == "__main__":
    clean_file(INPUT_FILE, OUTPUT_FILE)
