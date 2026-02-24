import asyncio
from datetime import datetime
from itertools import count
from unittest.mock import AsyncMock, Mock, patch

from .views import VacancyListView

import pytest
from django.db import transaction
from django.test import RequestFactory, override_settings, TestCase, TransactionTestCase
from django.utils import timezone
from factory.faker import Faker

from app.services.vacancies.models import City, Company, Platform, Vacancy
from app.services.vacancies.utils.paginated_vacancies import (
    PLATFORM_VACANCIES_QTY,
    VACANCIES_PER_PAGE,
    get_paginated_vacancies,
    get_search_vacancies,
)


def vacancy_creator():
    vacancy_id = count(0)

    def get_vacancies( n=1,
        title=None,
        city="Moscow",
        company="Hexlet",
        platform=Platform.HH,
        description="No description"):
        platform = Platform.objects.get_or_create(name=platform)[0]

        if isinstance(city, (list, tuple)):
            cities = [City.objects.get_or_create(name=c)[0] for c in city]
        else:
            cities = [City.objects.get_or_create(name=city)[0]]

        if isinstance(company, (list, tuple)):
            companies = [Company.objects.get_or_create(name=c)[0] for c in company]
        else:
            companies = [Company.objects.get_or_create(name=company)[0]]

    
        vacancies = [
            Vacancy(
                platform=platform,
                company=companies[i % len(companies)],
                city=cities[i % len(cities)],
                platform_vacancy_id=next(vacancy_id),
                title=title[i]
                if isinstance(title, (list,)) and title[i]
                else f"Developer {i}",
                url=f"https://example.com/vacancy/{next(vacancy_id)}",
                salary="100000 RUB",
                experience="2-3 years",
                employment="Full-time",
                description=description,
                published_at=timezone.now(),
            )
            for i in range(n)
        ]
        Vacancy.objects.bulk_create(vacancies)

    return get_vacancies

import factory
from factory.django import DjangoModelFactory
from factory import Sequence, Trait, post_generation
from django.utils import timezone
from itertools import count



class PlatformFactory(DjangoModelFactory):
    class Meta:
        model = Platform
        django_get_or_create = ('name',)


class CityFactory(DjangoModelFactory):
    class Meta:
        model = City
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"City {n}")


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"Company {n}")


class VacancyFactory(DjangoModelFactory):
    class Meta:
        model = Vacancy

    # Core fields with sensible defaults
    platform = factory.SubFactory(PlatformFactory, name="HH")
    company = factory.SubFactory(CompanyFactory, name="Hexlet")
    city = factory.SubFactory(CityFactory, name="Moscow")
    
    # Unique ID using Sequence (auto-incrementing)
    platform_vacancy_id = Sequence(lambda n: n)
    
    title = factory.Sequence(lambda n: f"Developer {n}")
    url = factory.LazyAttribute(lambda o: f"https://example.com/vacancy/{o.platform_vacancy_id}")
    salary = "100000 RUB"
    experience = "2-3 years"
    employment = "Full-time"
    description = "No description"
    published_at = factory.LazyFunction(timezone.now)

    # 🔹 Trait: Python-focused vacancy


class SearchVacanciesTests(TransactionTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        VacancyFactory.create_batch(
            2,
            title=factory.Iterator(["Python Developer", "Java Engineer"]),
            city=factory.Iterator([CityFactory(name="Moscow"), CityFactory(name="SPB")]),
            company=factory.Iterator([CompanyFactory(name="Hexlet"), CompanyFactory(name="Google")]),
        )


    def test_vacancies_created(self):
        self.assertEqual(Vacancy.objects.count(), 2)
    
    @patch("app.services.vacancies.views.inertia_render")
    @patch(
        "app.services.vacancies.views.get_paginated_vacancies",
        new_callable=AsyncMock,
    )
    @override_settings(SECRET_KEY="a-test-secret")
    async def test_fetch_vacancies(self, 
    mock_get_paginated_vacancies, mock_inertia_render):
        request = self.factory.get("/vacancies/")
        mock_paginated_data = {
            "vacancies": [{"id": 1, "title": "Test Vacancy"}],
            "pagination": {"page": 1, "has_next": False},
        }
        mock_get_paginated_vacancies.return_value = mock_paginated_data
        mock_inertia_render.return_value = "Mocked Inertia Response"

        view = VacancyListView()
        response = await view.get(request)

       
        print(response)
   
        

    def test_vacancy_titles(self):
        titles = [v.title for v in Vacancy.objects.all()]

        self.assertIn("Python Developer", titles)
        self.assertIn("Java Engineer", titles)

    def test_get_all_vacancies_empty_search(self):
        result = asyncio.run(get_search_vacancies(""))
        
        self.assertEqual(len(result), Vacancy.objects.count())
        self.assertEqual(result[-1]["title"], "Python Developer")
        self.assertEqual(result[-1]["company"], "Hexlet")


    def test_search_by_title(self):
        result = asyncio.run(get_search_vacancies("Python"))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Python Developer")

    def test_search_by_company_name(self):
        result = asyncio.run(get_search_vacancies("Google"))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["company"], "Google")

    def test_search_by_city(self):
        result = asyncio.run(get_search_vacancies("SPB"))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["city"], "SPB")

    def test_search_by_description(self):
        VacancyFactory.create(description="We need Django expertise")
        result = asyncio.run(get_search_vacancies("Django"))

        self.assertEqual(len(result), 1)
        self.assertIn("Django", result[0]["description"])

    def test_search_multiple_terms(self):
        result = asyncio.run(get_search_vacancies("Python Moscow"))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Python Developer")

    def test_search_case_insensitive(self):
        result_lower = asyncio.run(get_search_vacancies("python"))
        result_upper = asyncio.run(get_search_vacancies("PYTHON"))

        self.assertEqual(len(result_lower), 1)
        self.assertEqual(len(result_upper), 1)


    def test_first_page_pagination(self):
        VacancyFactory.build_batch(10)

        request = self.factory.get("/vacancies?page=1")
        result = asyncio.run(get_paginated_vacancies(request))

        self.assertEqual(len(result["vacancies"]), VACANCIES_PER_PAGE)
        self.assertEqual(result["pagination"]["current_page"], 1)
        self.assertTrue(result["pagination"]["has_next"])
        self.assertFalse(result["pagination"]["has_previous"])


    def test_last_page_pagination(self):
        VacancyFactory.create_batch(12)

        request = self.factory.get("/vacancies?page=3")

        with patch(
            "app.services.vacancies.utils.paginated_vacancies.hh_vacancy_parse"
        ) as mock_hh:
            with patch(
                "app.services.vacancies.utils.paginated_vacancies.superjob_vacancy_parse"
            ) as mock_sj:
                mock_hh.return_value = AsyncMock(status_code=200)
                mock_sj.return_value = AsyncMock(status_code=200)

                result = asyncio.run(get_paginated_vacancies(request))

        self.assertEqual(result["pagination"]["current_page"], 3)
        self.assertFalse(result["pagination"]["has_next"])
        self.assertTrue(result["pagination"]["has_previous"])

    def test_default_page_number(self):
        request = self.factory.get("/vacancies")
        result = asyncio.run(get_paginated_vacancies(request))

        self.assertEqual(result["pagination"]["current_page"], 1)

    def test_pagination_with_search_query(self):
        VacancyFactory.create_batch(5, title="Python Developer")
        VacancyFactory.create_batch(5, title="Java Developer")

        request = self.factory.get("/vacancies?page=1&search=Python")
        result = asyncio.run(get_paginated_vacancies(request))

        self.assertEqual(result["pagination"]["current_page"], 1)
        
        for vacancy in result["vacancies"]:
            self.assertIn("Python", vacancy["title"])

    def test_pagination_structure(self):
        request = self.factory.get("/vacancies?page=1")
        result = asyncio.run(get_paginated_vacancies(request))

        self.assertIn("pagination", result)
        self.assertIn("vacancies", result)

        pagination = result["pagination"]
        self.assertIn("current_page", pagination)
        self.assertIn("total_pages", pagination)
        self.assertIn("has_next", pagination)
        self.assertIn("has_previous", pagination)


from unittest.mock import AsyncMock, patch

from django.test import RequestFactory, SimpleTestCase, override_settings

from .views import VacancyListView


class VacancyListViewTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("app.services.vacancies.views.inertia_render")
    @patch(
        "app.services.vacancies.views.get_paginated_vacancies",
        new_callable=AsyncMock,
    )
    @override_settings(SECRET_KEY="a-test-secret")
    async def test_get_vacancy_list(
        self, mock_get_paginated_vacancies, mock_inertia_render
    ):
        request = self.factory.get("/vacancies/")
        mock_paginated_data = {
            "vacancies": [{"id": 1, "title": "Test Vacancy"}],
            "pagination": {"page": 1, "has_next": False},
        }
        mock_get_paginated_vacancies.return_value = mock_paginated_data
        mock_inertia_render.return_value = "Mocked Inertia Response"

        view = VacancyListView()
        response = await view.get(request)

        self.assertEqual(response, "Mocked Inertia Response")
        mock_get_paginated_vacancies.assert_awaited_once_with(request)
        mock_inertia_render.assert_called_once_with(
            request, "VacanciesPage", props=mock_paginated_data
        )

        with patch("app.services.hh.hh_parser.utils.vacancy_service.fetch_vacancies") as hh_fetch:
            hh_fetch.return_value = {"data": "uuu"}
                
            result = asyncio.run(get_paginated_vacancies(request))

