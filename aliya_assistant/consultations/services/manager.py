from .gpt_analyst import extract_facts
from .gpt_communicator import generate_final_answer

import logging
import openai

#добавляю следущую функцию что бы использовать запрос на тест из плоской папки стр 9-16

try:
    from .gpt_analyst import extract_facts
    from .gpt_communicator import generate_final_answer
except ImportError:
    # Фолбэк, если файлы лежат рядом без пакета 14 и 15 добавляю из-за запуска тестс
    from aliya_assistant.consultations.services.gpt_analyst import extract_facts
    from aliya_assistant.consultations.services.gpt_communicator import generate_final_answer
    from gpt_analyst import extract_facts
    from gpt_communicator import generate_final_answer

logger = logging.getLogger(__name__)

def process_query(questions_text: str) -> str:
    """
        Основной алгоритм работы нейросотрудника.
        Шаг 1: GPT-1 (Аналитик) 
        Шаг 2: GPT-2 (Коммуникатор)
    """
    try:
        facts = extract_facts(questions_text)
        if not facts:
            logger.warning("GPT-1 не вернул фактов")
            return (
                "Извините, ...."
                "Попробуйте переформулировать вопрос."
            )
            
        answer = generate_final_answer(facts)
        if not answer:
            logger.warning("GPT-2 не смог сформулировать ответ")
            return (
                "Произошла ошибка при формировании ответа. "
                "Попробуйте задать вопрос еще раз иначе. "
            )
            
        return answer.strip()
    
    except openai.AuthenticationError:
        logger.error("Ошибка авторизации: неверный или отсутствует OPENAI_API_KEY")
        return (
            "Ошибка подключения к модели. Проверьте корректность API-ключа OpenAI "
            "в файле .env (переменная OPENAI_API_KEY)."
        )

    except openai.APIConnectionError:
        logger.error("Ошибка соединения с OpenAI API.")
        return (
            "Сервис временно недоступен. Проверьте подключение к интернету "
            "или попробуйте позже."
        )

    except Exception as e:
        logger.exception("Неожиданная ошибка в pipeline: %s", e)
        return (
            "Возникла непредвиденная ошибка при обработке запроса. "
            "Попробуйте задать вопрос снова позже."
        )