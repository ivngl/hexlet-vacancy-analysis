import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from django.test import TestCase, TransactionTestCase, RequestFactory
from django.utils import timezone
from datetime import datetime
from django.db import transaction
from app.services.vacancies.models import Platform, Company, City, Vacancy
from app.services.vacancies.utils.paginated_vacancies import (
    get_search_vacancies,
    get_paginated_vacancies,
    VACANCIES_PER_PAGE,
    PLATFORM_VACANCIES_QTY,
)


def create_vacancies(n, titles=None, city="Moscow", companies="Hexlet", platform=Platform.HH):
    platform = Platform.objects.get_or_create(name=platform)[0]
    companies = [Company.objects.get_or_create(name=company)[0] for company in companies]
    city = City.objects.get_or_create(name=city)[0]

    count = len(titles) if isinstance(titles, list) else titles 

    vacancies = [Vacancy(
        platform=platform,
        company=company,
        city=city,
        platform_vacancy_id=f"id_{i}",
        title=titles[i] if isinstance(titles, (list,)) and titles[i] else f"Developer {i}",
        url=f"https://example.com/vacancy/{i}",
        salary="100000 RUB",
        experience="2-3 years",
        employment="Full-time",
        published_at=timezone.now()
    ) for i in range(count)]

    Vacancy.objects.bulk_create(vacancies)

class SearchVacanciesTests(TransactionTestCase):
    """Tests for get_search_vacancies function."""

    @classmethod
    def setUpClass(cls):
        cls.total_vacancies = 2
        create_vacancies(cls.total_vacancies, title=["Python Developer", "Java Engineer"],
        ["Hexlet", "Google"])
        

    def test_get_all_vacancies_empty_search(self):
        
        result = asyncio.run(get_search_vacancies(""))
        
        self.assertEqual(len(result), self.total_vacancies)
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
        """Test search filtering by city."""
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.city,
            platform_vacancy_id="1",
            title="Developer",
            url="https://example.com/1",
            published_at=timezone.now(),
        )
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.other_city,
            platform_vacancy_id="2",
            title="Developer",
            url="https://example.com/2",
            published_at=timezone.now(),
        )

        result = asyncio.run(get_search_vacancies("SPB"))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["city"], "SPB")

    def test_search_by_description(self):
        """Test search filtering by description."""
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.city,
            platform_vacancy_id="1",
            title="Developer",
            url="https://example.com/1",
            description="We need Django expertise",
            published_at=timezone.now(),
        )
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.city,
            platform_vacancy_id="2",
            title="Developer",
            url="https://example.com/2",
            description="React and JavaScript required",
            published_at=timezone.now(),
        )

        result = asyncio.run(get_search_vacancies("Django"))
        
        self.assertEqual(len(result), 1)
        self.assertIn("Django", result[0]["description"])

    def test_search_multiple_terms(self):
        """Test search with multiple terms (AND logic)."""
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.city,
            platform_vacancy_id="1",
            title="Python Developer",
            url="https://example.com/1",
            description="In Moscow office",
            published_at=timezone.now(),
        )
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.other_city,
            platform_vacancy_id="2",
            title="Python Developer",
            url="https://example.com/2",
            description="Remote position",
            published_at=timezone.now(),
        )

        result = asyncio.run(get_search_vacancies("Python Moscow"))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Python Developer")

    def test_search_case_insensitive(self):
        """Test search is case-insensitive."""
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.city,
            platform_vacancy_id="1",
            title="Python Developer",
            url="https://example.com/1",
            published_at=timezone.now(),
        )

        result_lower = asyncio.run(get_search_vacancies("python"))
        result_upper = asyncio.run(get_search_vacancies("PYTHON"))
        
        self.assertEqual(len(result_lower), 1)
        self.assertEqual(len(result_upper), 1)

    def test_search_returns_all_fields(self):
        """Test search result contains all expected fields."""
        Vacancy.objects.create(
            platform=self.platform,
            company=self.company1,
            city=self.city,
            platform_vacancy_id="123",
            title="Python Developer",
            url="https://example.com/1",
            salary="150000 RUB",
            experience="3-5 years",
            employment="Full-time",
            work_format="Remote",
            schedule="Flexible",
            address="Moscow, Russia",
            skills="Python, Django",
            description="Senior position",
            contacts="contact@example.com",
            published_at=timezone.now(),
        )

        result = asyncio.run(get_search_vacancies(""))
        
        expected_fields = [
            "id", "platform", "title", "salary", "company", "city",
            "url", "skills", "experience", "employment", "work_format",
            "schedule", "description", "address", "contacts", "published_at"
        ]
        for field in expected_fields:
            self.assertIn(field, result[0])


class PaginatedVacanciesTests(TestCase):
    """Tests for get_paginated_vacancies function."""

    def setUp(self):
        """Set up test fixtures and request factory."""
        self.factory = RequestFactory()
        self.platform = Platform.objects.create(name=Platform.HH)
        self.company = Company.objects.create(name="Tech Corp")
        self.city = City.objects.create(name="Moscow")

    def test_first_page_pagination(self):
        """Test pagination on first page."""
        # Create more vacancies than VACANCIES_PER_PAGE
        for i in range(10):
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=f"Developer {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies?page=1")
        result = asyncio.run(get_paginated_vacancies(request))
        
        self.assertEqual(len(result["vacancies"]), VACANCIES_PER_PAGE)
        self.assertEqual(result["pagination"]["current_page"], 1)
        self.assertTrue(result["pagination"]["has_next"])
        self.assertFalse(result["pagination"]["has_previous"])

    def test_middle_page_pagination(self):
        """Test pagination on middle page."""
        # Create enough vacancies for 3 pages
        for i in range(15):
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=f"Developer {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies?page=2")
        result = asyncio.run(get_paginated_vacancies(request))
        
        self.assertEqual(len(result["vacancies"]), VACANCIES_PER_PAGE)
        self.assertEqual(result["pagination"]["current_page"], 2)
        self.assertTrue(result["pagination"]["has_next"])
        self.assertTrue(result["pagination"]["has_previous"])
        self.assertEqual(result["pagination"]["previous_page_number"], 1)
        self.assertEqual(result["pagination"]["next_page_number"], 3)

    def test_last_page_pagination(self):
        """Test pagination on last page."""
        # Create 12 vacancies (2 full pages + 2 items)
        for i in range(12):
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=f"Developer {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies?page=3")
        
        with patch('app.services.vacancies.utils.paginated_vacancies.hh_vacancy_parse') as mock_hh:
            with patch('app.services.vacancies.utils.paginated_vacancies.superjob_vacancy_parse') as mock_sj:
                mock_hh.return_value = AsyncMock(status_code=404)()
                mock_sj.return_value = AsyncMock(status_code=404)()
                
                result = asyncio.run(get_paginated_vacancies(request))
        
        self.assertEqual(result["pagination"]["current_page"], 3)
        self.assertFalse(result["pagination"]["has_next"])
        self.assertTrue(result["pagination"]["has_previous"])

    def test_default_page_number(self):
        """Test default page is 1 when not specified."""
        for i in range(5):
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=f"Developer {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies")
        result = asyncio.run(get_paginated_vacancies(request))
        
        self.assertEqual(result["pagination"]["current_page"], 1)

    def test_pagination_with_search_query(self):
        """Test pagination works with search queries."""
        # Create vacancies with different titles
        for i in range(10):
            title = "Python Developer" if i % 2 == 0 else "Java Engineer"
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=title,
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies?page=1&search=Python")
        result = asyncio.run(get_paginated_vacancies(request))
        
        self.assertEqual(result["pagination"]["current_page"], 1)
        # Should have Python vacancies
        for vacancy in result["vacancies"]:
            self.assertIn("Python", vacancy["title"])

    def test_pagination_structure(self):
        """Test pagination returns correct structure."""
        for i in range(5):
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=f"Developer {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies?page=1")
        result = asyncio.run(get_paginated_vacancies(request))
        
        # Check structure
        self.assertIn("pagination", result)
        self.assertIn("vacancies", result)
        
        pagination = result["pagination"]
        self.assertIn("current_page", pagination)
        self.assertIn("total_pages", pagination)
        self.assertIn("has_next", pagination)
        self.assertIn("has_previous", pagination)

    def test_empty_vacancies_pagination(self):
        """Test pagination with no vacancies."""
        request = self.factory.get("/vacancies?page=1")
        result = asyncio.run(get_paginated_vacancies(request))
        
        self.assertEqual(len(result["vacancies"]), 0)
        self.assertEqual(result["pagination"]["current_page"], 1)
        self.assertEqual(result["pagination"]["total_pages"], 1)
        self.assertFalse(result["pagination"]["has_next"])
        self.assertFalse(result["pagination"]["has_previous"])

    def test_next_page_number_on_last_page(self):
        """Test next_page_number is None on last page."""
        for i in range(5):
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=f"Developer {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies?page=1")
        result = asyncio.run(get_paginated_vacancies(request))
        
        # Last page should have None for next_page_number
        self.assertIsNone(result["pagination"]["next_page_number"])

    def test_previous_page_number_on_first_page(self):
        """Test previous_page_number is None on first page."""
        for i in range(10):
            Vacancy.objects.create(
                platform=self.platform,
                company=self.company,
                city=self.city,
                platform_vacancy_id=f"id_{i}",
                title=f"Developer {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )

        request = self.factory.get("/vacancies?page=1")
        result = asyncio.run(get_paginated_vacancies(request))
        
        self.assertIsNone(result["pagination"]["previous_page_number"])


@pytest.mark.django_db
class TestSearchVacanciesAsync:
    """Pytest-style async tests for search vacancies."""

    async def test_search_with_empty_query(self):
        """Test search with empty query returns all vacancies."""
        platform = Platform.objects.create(name=Platform.HH)
        company = Company.objects.create(name="TechCo")
        city = City.objects.create(name="Moscow")
        
        for i in range(3):
            Vacancy.objects.create(
                platform=platform,
                company=company,
                city=city,
                platform_vacancy_id=f"id_{i}",
                title=f"Dev {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )
        
        result = await get_search_vacancies("")
        assert len(result) == 3

    async def test_search_returns_dict_objects(self):
        """Test search returns proper dict structure."""
        platform = Platform.objects.create(name=Platform.HH)
        company = Company.objects.create(name="TechCo")
        city = City.objects.create(name="Moscow")
        
        Vacancy.objects.create(
            platform=platform,
            company=company,
            city=city,
            platform_vacancy_id="123",
            title="Python Dev",
            url="https://example.com/1",
            published_at=timezone.now(),
        )
        
        result = await get_search_vacancies("")
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert result[0]["title"] == "Python Dev"


@pytest.mark.django_db
class TestPaginatedVacanciesAsync:
    """Pytest-style async tests for paginated vacancies."""

    async def test_paginated_vacancies_returns_dict(self):
        """Test paginated vacancies returns proper structure."""
        factory = RequestFactory()
        platform = Platform.objects.create(name=Platform.HH)
        company = Company.objects.create(name="TechCo")
        city = City.objects.create(name="Moscow")
        
        for i in range(5):
            Vacancy.objects.create(
                platform=platform,
                company=company,
                city=city,
                platform_vacancy_id=f"id_{i}",
                title=f"Dev {i}",
                url=f"https://example.com/{i}",
                published_at=timezone.now(),
            )
        
        request = factory.get("/vacancies?page=1")
        result = await get_paginated_vacancies(request)
        
        assert "pagination" in result
        assert "vacancies" in result
        assert result["pagination"]["current_page"] == 1
