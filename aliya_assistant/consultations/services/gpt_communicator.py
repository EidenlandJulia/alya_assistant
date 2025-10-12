import openai

def generate_final_answer(facts: str) -> str:
    """GPT-2: формирует вежливый и понятный ответ для пользователя."""
    client = openai.OpenAI()

    system_prompt = (
        "Ты — нейро-сотрудник Министерства алии и интеграции. "
        "На основе предоставленного списка фактов составь официальный, "
        "но дружелюбный ответ для репатрианта. "
        "Добавь приветствие, структурируй пункты и избегай воды."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": facts},
        ],
        temperature=0.0,
    )

    # Новый SDK возвращает строку
    text = getattr(response.choices[0].message, "content", "")
    return text.strip() if isinstance(text, str) else ""
