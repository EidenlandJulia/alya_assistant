import openai
import os
from dotenv import load_dotenv
from django.shortcuts import render

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
