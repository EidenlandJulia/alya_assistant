import openai
import os
from dotenv import load_dotenv
from django.shortcuts import render
import sys

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import threading
from popitka2.parser2 import crawl  # импорт функции из твоего парсера

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
from django.http import JsonResponse

parser_status = {"running": False, "done": False}

def crawl_wrapper():
    from popitka2 import crawl  # или откуда у тебя парсер
    parser_status["running"] = True
    parser_status["done"] = False
    try:
        crawl()
    finally:
        parser_status["running"] = False
        parser_status["done"] = True


@csrf_exempt
def start_parser(request):
    if request.method == "POST":
        if parser_status["running"]:
            return JsonResponse({"status": "already_running"})
        thread = threading.Thread(target=crawl_wrapper)
        thread.start()
        return JsonResponse({"status": "started"})
    return JsonResponse({"error": "Invalid method"}, status=405)


def parser_status_view(request):
    return JsonResponse(parser_status)



@csrf_exempt
def start_parser(request):
    if request.method == "POST":
        thread = threading.Thread(target=crawl)
        thread.start()
        return JsonResponse({"status": "started"})
    return JsonResponse({"error": "Invalid method"}, status=405)

load_dotenv()

def index(request):
    return render(request, "consultations/index.html")

def ask_question(request):
    if request.method == "POST":
        question = request.POST.get("question_text")

        # создаем клиент OpenAI
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — сотрудник Министерства алии и интеграции, отвечай кратко и по делу."},
                {"role": "user", "content": question},
            ],
        )

        answer = response.choices[0].message.content
        return render(request, "consultations/result.html", {"question": question, "answer": answer})

    return render(request, "consultations/index.html")
