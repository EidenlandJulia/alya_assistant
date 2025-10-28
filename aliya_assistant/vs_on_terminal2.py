# -*- coding: utf-8 -*-
import os, re, sys
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv
from colorama import Fore, Style, init
import openai

# ========== НАСТРОЙКИ ==========
CLEAR = False  # не очищаем экран
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
KB_PATH = os.getenv("KB_PATH", "knowledge_base_aliyah_full.txt")

# ========== ИНИЦИАЛИЗАЦИЯ ==========
init(autoreset=True)
load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

def clear():
    if CLEAR:
        os.system("cls" if os.name == "nt" else "clear")

def load_kb(path: str) -> str:
    print(f"📄 Загружаю базу знаний: {os.path.abspath(path)}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ KB not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    return re.sub(r"\r\n?", "\n", txt)

def split_paragraphs(text: str):
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if len(p.strip()) > 40]

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9\-']+")
def tok(s: str): return [t.lower() for t in TOKEN_RE.findall(s)]

def retrieve(kb: str, question: str) -> str:
    print("🔍 Выбираю релевантный контекст...")
    paras = split_paragraphs(kb)
    q = tok(question)
    qset = set([t for t in q if len(t) > 2])
    scored = []
    for p in paras:
        pt = tok(p)
        score = sum(1 for t in pt if t in qset)
        if score > 0:
            scored.append((score, p))
    selected = [p for _, p in sorted(scored, key=lambda x:x[0], reverse=True)[:10]]
    ctx = "\n\n".join(selected)
    print(f"📌 Контекст выбран: {len(ctx)} символов")
    return ctx

def call_model(role: str, question: str, context: str, previous: str = None):
    prompts = {
        "analyst": (
            "Ты — АНАЛИТИК Министерства алии и интеграции. "
            "Извлеки из КОНТЕКСТА только ключевые факты в виде списка. Никаких лишних слов."
        ),
        "communicator": (
            "Ты — КОММУНИКАТОР. Возьми **факты аналитика** и объясни их простым языком "
            "короткими абзацами. Добавь: краткое объяснение + что делать дальше (чек-лист)."
        ),
        "manager": (
            "Ты — МЕНЕДЖЕР. Объедини **факты** и **объяснение** в финальный "
            "10-строчный ответ для пользователя + чёткий план действий."
        )
    }

    messages = [
        {"role": "system", "content": "Используй только предоставленный КОНТЕКСТ."},
        {"role": "system", "content": f"КОНТЕКСТ:\n{context}"},
        {"role": "system", "content": prompts[role]},
        {"role": "user", "content": question}
    ]

    if previous:
        messages.append({"role": "system", "content": previous})

    print(f"⏳ Отправляю запрос роли: {role.upper()}...")

    try:
        r = client.chat.completions.create(model=MODEL, messages=messages)
        text = r.choices[0].message.content.strip()
        print(f"✅ {role.upper()} ответил.\n")
        return text
    except Exception as e:
        print(f"❌ Ошибка у роли {role.upper()}: {e}")
        return f"Ошибка у роли {role.upper()}: данных недостаточно."

def main():
    try:
        kb = load_kb(KB_PATH)
    except Exception as e:
        print(f"Ошибка загрузки KB: {e}")
        sys.exit(1)

    while True:
        print("\n==================================================================")
        question = input(Fore.WHITE + "Введите ваш вопрос:\n> ").strip()
        if not question:
            print("⚠ Пустой вопрос, попробуйте снова.")
            continue

        context = retrieve(kb, question)
        if not context:
            print("⚠ Нет данных по вопросу.")
            continue

        # --- 3 модели последовательно ---
        a_text = call_model("analyst", question, context)
        c_text = call_model("communicator", a_text, context)
        m_text = call_model("manager", question, context, f"Факты:\n{a_text}\n\nОбъяснение:\n{c_text}")

        print("\n🔎 РЕЗУЛЬТАТ:\n")
        print(Fore.MAGENTA + "=== АНАЛИТИК ===\n" + a_text + "\n")
        print(Fore.GREEN + "=== КОММУНИКАТОР ===\n" + c_text + "\n")
        print(Fore.YELLOW + "=== МЕНЕДЖЕР (финальный) ===\n" + m_text + "\n")

        with open("report.txt", "a", encoding="utf-8") as f:
            f.write(f"\nВопрос:\n{question}\n")
            f.write("\nАНАЛИТИК:\n" + a_text + "\n")
            f.write("\nКОММУНИКАТОР:\n" + c_text + "\n")
            f.write("\nМЕНЕДЖЕР:\n" + m_text + "\n")
            f.write("=" * 80 + "\n")

        print("✅ Сохранено в report.txt\n")

if __name__ == "__main__":
    main()
