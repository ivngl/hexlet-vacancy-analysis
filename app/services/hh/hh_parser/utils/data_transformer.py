import logging
import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from app.services.vacancies.models import City, Company, Platform

logger = logging.getLogger(__name__)

CURRENCY_PATTERN = re.compile(r"^(rub|rur)$", re.IGNORECASE)


def normalize_currency(currency: str) -> str:
    """Нормализует валюту к формату RUR (rub/rur -> RUR)."""
    if CURRENCY_PATTERN.match(currency):
        return "RUR"
    return currency


def format_salary(salary_data: Optional[dict[str, Any]]) -> str:
    """Форматирует данные о зарплате в читаемую строку."""
    if not salary_data:
        return "По договоренности"

    salary_from = salary_data.get("from")
    salary_to = salary_data.get("to")
    currency = salary_data.get("currency")

    has_valid_salary = isinstance(salary_from, int) or isinstance(salary_to, int)
    if not has_valid_salary:
        return "По договоренности"

    parts = []
    if isinstance(salary_from, int):
        parts.append(f"от {salary_from}")
    if isinstance(salary_to, int):
        parts.append(f"до {salary_to}")
    if currency:
        parts.append(normalize_currency(currency))

    return " ".join(parts) if parts else "По договоренности"


def format_list(items: Optional[list[dict[str, Any]]], key: str) -> str:
    """Форматирует список объектов в строку через запятую."""
    if not items:
        return ""
    return ", ".join(item[key] for item in items if item.get(key))


def extract_plain_text(html_content: Optional[str]) -> str:
    """Извлекает текст из HTML-контента."""
    if not html_content:
        return ""
    return BeautifulSoup(html_content, "html.parser").get_text(strip=True)


def safe_nested_get(data: Optional[dict[str, Any]], *keys: str) -> Any:
    """Безопасно извлекает значение из вложенной структуры словарей."""
    if not data:
        return None

    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None

    return current


def transform_hh_data(item: dict[str, Any]) -> dict[str, Any]:
    """Преобразует данные вакансии HH в формат модели."""
    platform, _ = Platform.objects.get_or_create(name=Platform.HH)
    company = extract_company(item)
    city, full_address = extract_city_and_address(item.get("address"))

    return {
        "platform": platform,
        "company": company,
        "city": city,
        "platform_vacancy_id": f"{Platform.HH}{item.get('id')}",
        "title": item.get("name"),
        "salary": format_salary(item.get("salary")),
        "url": item.get("alternate_url"),
        "experience": safe_nested_get(item, "experience", "name"),
        "schedule": safe_nested_get(item, "schedule", "name"),
        "work_format": format_list(item.get("work_format"), "name"),
        "skills": format_list(item.get("key_skills"), "name"),
        "education": safe_nested_get(item, "education", "level", "name"),
        "description": extract_plain_text(item.get("description")),
        "address": full_address,
        "employment": safe_nested_get(item, "employment", "name"),
        "contacts": item.get("contacts"),
        "published_at": item.get("published_at"),
    }


def extract_company(item: dict[str, Any]) -> Optional[Company]:
    """Извлекает компанию из данных вакансии."""
    employer_name = safe_nested_get(item, "employer", "name")
    if not employer_name:
        return None
    company, _ = Company.objects.get_or_create(name=employer_name)
    return company


def extract_city_and_address(
    address: Optional[dict[str, Any]],
) -> tuple[Optional[City], Optional[str]]:
    """Извлекает город и полный адрес из данных адреса."""
    if not address:
        return None, None

    city_name = address.get("city")
    city: Optional[City] = None
    if city_name:
        city, _ = City.objects.get_or_create(name=city_name)

    return city, address.get("raw")
