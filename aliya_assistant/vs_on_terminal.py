import os
import sys
import openai
from dotenv import load_dotenv
from datetime import datetime
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)

# === Очистка терминала ===
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# === Настройки ===
load_dotenv()
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

MODELS = {
    "1": "gpt-4o-mini",
    "2": "gpt-4o",
    "3": "gpt-3.5-turbo",
}

LANGUAGES = {
    "1": ("ru", "Русский 🇷🇺"),
    "2": ("en", "English 🇬🇧"),
    "3": ("he", "עברית 🇮🇱"),
}

# === Заголовок ===
def print_header():
    print(Fore.CYAN + Style.BRIGHT + "=" * 70)
    print(Fore.YELLOW + Style.BRIGHT + "  Н Е Й Р О К О Н С У Л Ь Т А Н Т   —  Министерство алии и интеграции")
    print(Fore.CYAN + Style.BRIGHT + "=" * 70 + "\n")

# === Выбор модели ===
def choose_model():
    print(Fore.GREEN + "Выберите модель OpenAI:\n")
    for key, model in MODELS.items():
        print(f"{Fore.WHITE}[{key}] {Fore.LIGHTBLUE_EX}{model}")
    return MODELS.get(input(Fore.WHITE + "\nВведите номер модели (1–3): ").strip())

# === Выбор языка ===
def choose_language():
    clear()
    print_header()
    print(Fore.GREEN + "Выберите язык взаимодействия:\n")
    for key, (code, name) in LANGUAGES.items():
        print(f"{Fore.WHITE}[{key}] {Fore.LIGHTYELLOW_EX}{name}")
    choice = input(Fore.WHITE + "\nВведите номер языка (1–3): ").strip()
    return LANGUAGES.get(choice, LANGUAGES["1"])  # по умолчанию русский

# === Запрос к модели ===
def generate_response(model, lang_code, question):
    system_prompts = {
        "ru": "Ты — сотрудник Министерства алии и интеграции Израиля. Отвечай кратко, вежливо и по делу на русском языке.",
        "en": "You are an employee of the Ministry of Aliyah and Integration. Respond briefly and politely in English.",
        "he": "אתה עובד משרד העלייה והקליטה. ענה בקצרה ובנימוס בעברית.",
    }

    start_time = datetime.now()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompts[lang_code]},
            {"role": "user", "content": question},
        ],
    )
    duration = (datetime.now() - start_time).total_seconds()
    answer = (response.choices[0].message.content or "").strip()
    return answer, duration

# === Основной цикл ===
def main():
    while True:
        clear()
        print_header()

        lang_code, lang_name = choose_language()
        clear()
        print_header()
        print(Fore.CYAN + f"Текущий язык: {lang_name}\n")

        model = choose_model()
        if not model:
            print(Fore.RED + "Ошибка: неверный выбор модели.")
            sys.exit(1)

        # Вечный цикл вопросов
        while True:
            clear()
            print_header()
            print(Fore.LIGHTCYAN_EX + f"Модель: {model}")
            print(Fore.LIGHTYELLOW_EX + f"Язык: {lang_name}\n")

            question = input(Fore.WHITE + Style.BRIGHT + "Введите ваш вопрос:\n> ").strip()
            if not question:
                print(Fore.RED + "Ошибка: вопрос не может быть пустым.")
                continue

            clear()
            print_header()
            print(Fore.CYAN + f"Отправка запроса к модели {model}...\n")

            try:
                answer, duration = generate_response(model, lang_code, question)


                # === Формирование отчёта ===
                report = (
                    f"ОТЧЁТ О РАБОТЕ МОДЕЛИ\n"
                    f"{'='*60}\n"
                    f"Дата и время: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
                    f"Модель: {model}\n"
                    f"Язык: {lang_name}\n"
                    f"Время отклика: {duration:.2f} секунд\n"
                    f"{'-'*60}\n"
                    f"Вопрос:\n{question}\n\n"
                    f"Ответ:\n{answer}\n"
                    f"{'='*60}\n"
                )
                with open("report.txt", "a", encoding="utf-8") as f:
                    f.write(report + "\n\n")

                print(Fore.GREEN + "✅ Ответ получен и добавлен в report.txt\n")
                print(Fore.WHITE + Style.BRIGHT + "Ответ модели:\n")
                print(Fore.LIGHTYELLOW_EX + answer + "\n")

            except Exception as e:
                print(Fore.RED + f"❌ Ошибка при обращении к API: {e}")

            # Меню после ответа
            print(Fore.CYAN + "\nЧто вы хотите сделать дальше?\n")
            print(Fore.WHITE + "[1]" + Fore.LIGHTGREEN_EX + " Задать новый вопрос")
            print(Fore.WHITE + "[2]" + Fore.LIGHTBLUE_EX + " Сменить модель / язык")
            print(Fore.WHITE + "[3]" + Fore.RED + " Выйти\n")

            next_action = input(Fore.WHITE + "Ваш выбор (1–3): ").strip()

            if next_action == "3":
                print(Fore.YELLOW + "\nДо свидания! 👋")
                sys.exit(0)
            elif next_action == "2":
                break
            elif next_action == "1":
                continue
            else:
                print(Fore.RED + "Неверный выбор. Возврат в меню.")
                break

if __name__ == "__main__":
    main()
