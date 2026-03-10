from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PricingStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return ["pricing_page"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "pricing_static": PricingStaticSitemap,
}
