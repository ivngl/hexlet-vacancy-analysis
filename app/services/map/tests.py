from abc import abstractmethod

from django.test import TestCase

from app.services.vacancies.models import Vacancy
from app.services.vacancies.tests.factories import VacancyFactory


class MapTests(TestCase):
    @abstractmethod
    def setUpTestData(cls):
        VacancyFactory.create_batch(5, region="Moscow")

    def test_map_list_view_get(self):
        response = self.client.get("/map")

        self.asse
        self.assertEqual(response.status_code, 200)
