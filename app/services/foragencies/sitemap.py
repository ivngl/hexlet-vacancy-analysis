from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class ForAgenciesStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return ["foragencies_page"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "foragencies_static": ForAgenciesStaticSitemap,
}
