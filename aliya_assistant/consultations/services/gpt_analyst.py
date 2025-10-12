import openai

def extract_facts(questions_text: str) -> str:
    """GPT-1: извлекает факты из базы знаний министерства"""
    client = openai.OpenAI()
    system_prompt = (
        "Ты - аналитическая модель Министерства алии и интеграции. "
        "Выдели из запроса пользователя только ключевые факты и пункты, "
        "без пояснений, в виде краткого списка. "
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": questions_text},
        ],
        temperature=0.0,
    )
    
    content = getattr(response.choices[0].message, "content", None)
    
    if isinstance(content, list):
        text = content[0].text
    elif isinstance(content, str):
        text = content
    else:
        text = ""
        
    return text.strip()
    
    
    
    