#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
extract_docs_to_txt.py
Извлекает текст из всех документов в папке docs/ и сохраняет их в docs_text/.

Поддерживаемые форматы:
- PDF (pdfminer.six)
- DOCX, DOC (python-docx)
- RTF (чтение как текст)
- TXT (копируется как есть)

Результат:
- Для каждого документа создаётся .txt-файл с тем же названием.
- Все результаты сохраняются в папку docs_text/
"""

import os
import re
from pathlib import Path
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

# ----------- Настройки -----------
DOCS_DIR = Path("docs")
OUTPUT_DIR = Path("docs_text")
OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED = {".pdf", ".doc", ".docx", ".rtf", ".txt"}


# ----------- Утилиты -----------
def clean_text(s: str) -> str:
    """Удаляет лишние пробелы, повторяющиеся символы и невидимые артефакты"""
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\x0c", "").strip()
    return s


def extract_pdf(path: Path) -> str:
    try:
        return clean_text(pdf_extract_text(path))
    except Exception as e:
        print(f"⚠️ Ошибка PDF {path.name}: {e}")
        return ""


def extract_docx(path: Path) -> str:
    try:
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        return clean_text(text)
    except Exception as e:
        print(f"⚠️ Ошибка DOCX {path.name}: {e}")
        return ""


def extract_txt(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    except Exception as e:
        print(f"⚠️ Ошибка TXT {path.name}: {e}")
        return ""


def extract_rtf(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        text = re.sub(r"{\\[^}]+}", "", content)  # простое удаление тегов
        return clean_text(text)
    except Exception as e:
        print(f"⚠️ Ошибка RTF {path.name}: {e}")
        return ""


# ----------- Основная логика -----------
def main():
    files = [f for f in DOCS_DIR.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED]
    print(f"📂 Найдено файлов: {len(files)}")

    for file_path in files:
        ext = file_path.suffix.lower()
        print(f"📄 Обработка: {file_path.name}")

        if ext == ".pdf":
            text = extract_pdf(file_path)
        elif ext in {".doc", ".docx"}:
            text = extract_docx(file_path)
        elif ext == ".rtf":
            text = extract_rtf(file_path)
        elif ext == ".txt":
            text = extract_txt(file_path)
        else:
            print(f"⏭ Пропуск: неподдерживаемый формат {ext}")
            continue

        if not text.strip():
            print(f"⚠️ Пустой текст в {file_path.name}")
            continue

        # сохраняем
        output_file = OUTPUT_DIR / (file_path.stem + ".txt")
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(text)

    print("\n✅ Готово! Все тексты сохранены в папку docs_text/")


if __name__ == "__main__":
    main()
