# -*- coding: utf-8 -*-
"""
CLI для трёхуровневого бота:
- GPT-Аналитик (сухие факты из БЗ)
- GPT-Коммуникатор (человеческий ответ)
- Менеджер (сквозной пайплайн, финальный ответ)

Файл устойчив к двум способам запуска:
  A) python -m aliya_assistant.consultations.tests      (из корня проекта)
  B) python aliya_assistant/consultations/tests.py      (из корня проекта)
"""
from __future__ import annotations

import os
import sys
import logging

# ---------- УСТОЙЧИВЫЕ ИМПОРТЫ ПОД ТЕКУЩУЮ СТРУКТУРУ ----------
# Структура:
# diplom3/
#   aliya_assistant/
#     consultations/
#       services/
#         gpt_analyst.py
#         gpt_communicator.py
#         manager.py
#       tests.py  ← этот файл

HERE = os.path.abspath(os.path.dirname(__file__))         # .../aliya_assistant/consultations
PKG_ROOT = os.path.dirname(HERE)                          # .../aliya_assistant
PROJECT_ROOT = os.path.dirname(PKG_ROOT)                  # .../diplom3

# Добавим корень проекта в sys.path — чтобы запуск "файлом" тоже работал
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    # Абсолютные импорты — работают и при запуске модулем, и файлом (после sys.path)
    from aliya_assistant.consultations.services.manager import process_query
    from aliya_assistant.consultations.services.gpt_analyst import extract_facts
    from aliya_assistant.consultations.services.gpt_communicator import generate_final_answer
except Exception:
    # Резерв (если запущено строго как модуль и окружение уже пакетное)
    from .services.manager import process_query            # type: ignore
    from .services.gpt_analyst import extract_facts        # type: ignore
    from .services.gpt_communicator import generate_final_answer  # type: ignore
# ---------------------------------------------------------------

# Настройка логов, чтобы видеть предупреждения из manager.py и т.п.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

BANNER = """
==============================================
  Нейро-сотрудник (CLI)
  Модели: GPT-Аналитик → GPT-Коммуникатор → Менеджер
  Введите вопрос (или пустую строку для выхода)
==============================================
"""

def print_block(title: str, text: str) -> None:
    line = "=" * 60
    print(f"\n{line}\n{title}\n{line}")
    if not text:
        print("(пусто)")
    else:
        # Убираем случайные начальные/конечные переносы
        print(str(text).strip())

def main() -> None:
    # Подсказка про ключ — чтобы было понятно до первого вызова API
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Переменная окружения OPENAI_API_KEY не задана. "
              "Установи её перед запуском (или в .env).")

    print(BANNER)
    while True:
        try:
            question = input("Вопрос: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход.")
            break

        if not question:
            print("Выход.")
            break

        # 1) GPT-Аналитик: сухие факты
        try:
            facts = extract_facts(question)
        except Exception as e:
            facts = ""
            print_block("Ошибка в GPT-Аналитике", f"{e}")
        print_block("GPT-Аналитик: извлечённые факты", facts or "")

        # 2) GPT-Коммуникатор: понятный ответ из фактов
        try:
            comm_answer = generate_final_answer(facts or question)
        except Exception as e:
            comm_answer = ""
            print_block("Ошибка в GPT-Коммуникаторе", f"{e}")
        print_block("GPT-Коммуникатор: понятный ответ", comm_answer or "")

        # 3) Менеджер: сквозной пайплайн
        try:
            manager_answer = process_query(question)
        except Exception as e:
            manager_answer = ""
            print_block("Ошибка Менеджера (пайплайн)", f"{e}")
        print_block("Менеджер: финальный ответ", manager_answer or "")

        print("\n(Пустая строка — выход)")

if __name__ == "__main__":
    main()
