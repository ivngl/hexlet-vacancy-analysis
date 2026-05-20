from http import HTTPStatus
from unittest.mock import AsyncMock, patch

from django.test import RequestFactory, TransactionTestCase, override_settings
from django.urls import reverse
from inertia.test import InertiaTestCase

from app.services.map.views import MapListView
from app.services.vacancies.models import Vacancy
from app.services.vacancies.tests.factories import VacancyFactory


class MapTests(TransactionTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vacancies_data = {"totalVacancies": 5, "region": "Moscow"}
        VacancyFactory.create_batch(
            cls.vacancies_data["totalVacancies"],
            region=cls.vacancies_data["region"],
        )

    async def test_map_list_view_get(self):
        # response = self.client.get(reverse("map_list"))
        request = self.factory.get("/map/")
        view = MapListView()
        response = await view.get(request)

        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertIn(response, self.vacancies_data)
