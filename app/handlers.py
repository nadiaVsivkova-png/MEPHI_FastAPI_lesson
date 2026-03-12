"""Эндпоинты API для FastAPI приложения."""

from fastapi import APIRouter, Body

from .forms import UserNameParts
from .query import getIp

import requests
from fastapi import HTTPException
from datetime import date
from .forms import BirthDate

router = APIRouter()


@router.get("/")
async def index() -> dict[str, str]:
    """Корневой эндпоинт для проверки работы сервера."""
    return {"status": "Ok"}


@router.get("/users/{username}", name="Hello user")
async def read_user(username: str) -> dict[str, str]:
    """Возвращает приветствие для пользователя.

    Args:
        username: Имя пользователя из пути

    Returns:
        Словарь с сообщением приветствия
    """
    return {"message": f"Hello {username}"}


@router.post("/users/full-name", name="Full name")
async def full_name(user_from: UserNameParts = Body(..., embed=True)) -> dict[str, str]:
    """Возвращает полное имя из частей.

    Args:
        user_from: Модель с частями имени

    Returns:
        Словарь с полным именем
    """
    return {
        "fullName": f"{user_from.lastName.strip()} {user_from.firstName.strip()} {user_from.middleName.strip()}"
    }


@router.get("/users/current/ip", name="Получить текущий ip")
async def current_ip() -> str:
    """Возвращает текущий IP-адрес клиента.

    Returns:
        Строка с IP-адресом
    """
    ip = getIp()
    return ip


@router.get("/users/current/full-time", name="Получить текущее время")
async def current_full_time() -> dict:
    """Получает текущее время по IP-адресу."""
    # 1. Получаем IP
    client_ip = getIp()

    # 2. Формируем URL для запроса к timeapi.io
    url = f"https://timeapi.io/api/Time/current/ip?ipAddress={client_ip}"

    try:
        # 3. Отправляем GET-запрос с таймаутом 5 секунд
        response = requests.get(url, timeout=5)
        # 4. Если статус не 2xx, вызываем исключение
        response.raise_for_status()
        # 5. Возвращаем данные в виде словаря
        return response.json()
    except requests.exceptions.RequestException as e:
        # 6. В случае ошибки выбрасываем HTTP-исключение с кодом 503
        raise HTTPException(status_code=503, detail=f"Ошибка внешнего API: {str(e)}")


def get_zodiac_sign(birth_date: date) -> str:
    month = birth_date.month
    day = birth_date.day

    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "aquarius"
    else:  # month == 2 and day >= 19) or (month == 3 and day <= 20
        return "pisces"


@router.post("/horoscope", name="Получить гороскоп")
async def horoscope(birth_data: BirthDate) -> dict[str, str]:
    """Возвращает знак зодиака и гороскоп по дате рождения."""
    # 1. Определяем знак по дате
    sign = get_zodiac_sign(birth_data.birthDate)

    # 2. Формируем URL для Horoscope API
    url = f"https://www.ohmanda.com/api/horoscope/{sign}/"

    try:
        # 3. Делаем запрос
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()  # ожидаем, что API вернёт JSON
        # 4. Добавляем знак в ответ (на случай, если API его не возвращает)
        data["sign"] = sign
        return data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Ошибка Horoscope API: {str(e)}")