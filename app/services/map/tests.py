from http import HTTPStatus
from unittest.mock import AsyncMock, patch
from django.test import RequestFactory, TransactionTestCase, override_settings
from django.urls import reverse
from inertia.test import InertiaTestCase

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

    @patch("app.services.vacancies.views.inertia_render")
    def test_map_list_view_get(self, mock_inertia_render):
        response = self.client.get(reverse("map_list"))
        props = self.props()
        map_data = props["mapData"]
        region_data = map_data[0]

        self.assertIn("mapData", props)
        self.assertEqual(len(map_data), 1)
        self.assertComponentUsed("MapPage")
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertEqual(region_data["region"], self.vacancies_data["region"])
        self.assertEqual(
            region_data["totalVacancies"], self.vacancies_data["totalVacancies"]
        )
