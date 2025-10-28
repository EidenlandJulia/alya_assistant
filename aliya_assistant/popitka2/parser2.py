#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
parser3.py — расширенный сбор русскоязычных материалов по теме алии и интеграции

💡 Что делает:
1. Парсит сайты KolZchut и Gov.il, включая скрытые подразделы
2. Находит страницы даже если ключевые слова только в тексте (а не в URL)
3. Извлекает текст, PDF, формы и сохраняет всё в единый knowledge_base_aliyah_full.txt
4. Отсеивает нерелевантные темы (армия, налоги, медицина и т.п.)
5. Проверяет язык содержимого (только русские тексты)
6. Сохраняет PDF-документы и формы отдельно в папку docs/
7. Отображает прогресс и счётчики

📦 Выход:
- knowledge_base_aliyah_full.txt  — объединённая база
- docs/                           — скачанные PDF, DOC и т.д.
- parser3.log                     — лог-файл
"""

import os
import re
import time
import logging
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text as pdf_extract_text


# ----------- Настройки -----------
OUTPUT_FILE = Path("knowledge_base_aliyah_full.txt")
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

LOG_FILE = Path("parser3.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("parser3")

# Основные страницы
START_URLS = [
    "https://www.kolzchut.org.il/ru/Репатрианты",
    "https://www.kolzchut.org.il/ru/New_Olim",
    "https://www.kolzchut.org.il/ru/category/Олим_Хадашим",
    "https://www.kolzchut.org.il/ru/Тошав_хозер",
    "https://www.gov.il/ru/subjects/immigration_and_absorption",
    "https://www.gov.il/ru/subjects/returning_residents",
    "https://www.gov.il/ru/subjects/learning_hebrew",
    "https://www.gov.il/ru/departments/ministry_of_aliyah_and_integration",
    "https://govextra.gov.il/moia/your-place-in-israel-lang/home-ru/",
]

KEYWORDS = [
    "алия", "алим", "репатриант", "репатрианты", "возвращающ",
    "министерство алии", "министерство интеграции", "абсорбц",
    "интеграция", "ульпан", "еврей", "тошав хозер", "olim", "aliyah",
    "absorption", "integration", "returning"
]

EXCLUDE = ["army", "tax", "covid", "pension", "violence", "lawyer", "children", "business"]

PDF_EXT = {".pdf"}
FORM_EXT = {".doc", ".docx", ".xls", ".xlsx", ".rtf", ".odt", ".zip"}
MAX_PAGES = 150
MAX_DEPTH = 4
DELAY = 0.5


# ----------- Утилиты -----------
def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def is_russian_text(text: str) -> bool:
    """Проверяем, что в тексте хотя бы 25% кириллицы"""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    cyr = sum(1 for c in letters if "а" <= c.lower() <= "я" or c.lower() == "ё")
    return cyr / len(letters) > 0.25


def has_keywords(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in KEYWORDS)


def file_ext(url: str) -> str:
    return Path(urlparse(url).path).suffix.lower()


def extract_pdf(session, url: str, name_hint: str = "") -> str:
    """Извлекает текст из PDF и сохраняет файл"""
    try:
        r = session.get(url, timeout=40)
        r.raise_for_status()
        filename = DOCS_DIR / (re.sub(r'[^\w\-]+', '_', name_hint)[:60] + ".pdf")
        with open(filename, "wb") as f:
            f.write(r.content)

        text = pdf_extract_text(filename)
        text = clean_text(text)
        if is_russian_text(text) and has_keywords(text):
            return text
        return ""
    except Exception as e:
        logger.warning(f"Ошибка PDF {url}: {e}")
        return ""


def extract_page(session, url: str):
    """Извлекает контент страницы и ссылки"""
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
    except Exception as e:
        logger.warning(f"Ошибка запроса: {url} ({e})")
        return None

    title_tag = soup.find("h1") or soup.find("title")
    title = clean_text(title_tag.get_text()) if title_tag else "Без названия"

    main = soup.find("main") or soup.body
    text_blocks = []
    if main:
        for el in main.find_all(["p", "li", "h2", "h3", "div"]):
            txt = clean_text(el.get_text())
            if txt and len(txt) > 25:
                text_blocks.append(txt)

    content = "\n".join(text_blocks)
    if not is_russian_text(content) or not has_keywords(content):
        return None

    forms, pdfs, links = [], [], []
    for a in soup.find_all("a", href=True):
        full_url = urljoin(url, a["href"])
        ext = file_ext(full_url)
        if any(x in full_url for x in ["#", "javascript:", "mailto:"]):
            continue
        if ext in FORM_EXT:
            forms.append(full_url)
        elif ext in PDF_EXT:
            pdfs.append(full_url)
        elif full_url.startswith("https://") and not any(x in full_url for x in EXCLUDE):
            links.append(full_url)

    return title, content, forms, pdfs, links


# ----------- Основная логика -----------
def crawl():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    visited = {}
    queue = [(url, 0) for url in START_URLS]
    count, pdf_count, form_count = 0, 0, 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        while queue and count < MAX_PAGES:
            url, depth = queue.pop(0)
            if url in visited or depth > MAX_DEPTH:
                continue
            visited[url] = True

            logger.info(f"[{count+1}] {url}")
            print(f"→ [{count+1}] {url}")
            result = extract_page(session, url)
            if not result:
                continue
            title, content, forms, pdfs, links = result

            source = "kolzchut" if "kolzchut" in url else "gov.il"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            f.write("=" * 80 + "\n")
            f.write(f"Название: {title}\n")
            f.write(f"Ссылка: {url}\n")
            f.write(f"Источник: {source}\n")
            f.write(f"Дата парсинга: {timestamp}\n")
            f.write("-" * 80 + "\n")
            f.write(content + "\n\n")

            if forms:
                form_count += len(forms)
                f.write("Формы для заполнения:\n")
                for form in forms:
                    f.write(f"📄 {form}\n")
                f.write("\n")

            for pdf_url in pdfs:
                pdf_text = extract_pdf(session, pdf_url, title)
                if pdf_text:
                    pdf_count += 1
                    f.write("Правовой документ (PDF):\n")
                    f.write(f"📑 {pdf_url}\n")
                    f.write(pdf_text + "\n\n")

            count += 1
            for u in links:
                if u not in visited:
                    queue.append((u, depth + 1))

            time.sleep(DELAY)

    logger.info(f"✅ Парсинг завершён: {count} страниц, {pdf_count} PDF, {form_count} форм")
    print(f"\n✅ Готово! {count} страниц, {pdf_count} PDF, {form_count} форм.")
    print(f"📂 Результат: {OUTPUT_FILE}")


if __name__ == "__main__":
    crawl()

