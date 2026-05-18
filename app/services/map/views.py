from django.db.models import Count, F
from django.views import View
from inertia import render as inertia_render

from app.services.vacancies.models import Vacancy


class MapListView(View):
    def get(self, request):
        map_data = list(
            Vacancy.objects.filter(region__isnull=False)
            .values("region")
            .annotate(totalVacancies=Count("region"))
            .order_by("region")
        )

        return inertia_render(request, "MapPage", props={"mapData": map_data})
