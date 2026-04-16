from django.views import View
from inertia import render as inertia_render  # type: ignore

from .models import HomePageBlock


class HomePageView(View):
    def get(self, request):
        blocks = HomePageBlock.objects.for_homepage()
        return inertia_render(request, "MapPage", props={"blocks": blocks})
