from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class AIStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ["ai_assistant"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "ai_static": AIStaticSitemap,
}
