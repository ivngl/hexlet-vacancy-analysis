from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class AccountStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.4

    def items(self):
        return ["account_profile_edit"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "account_static": AccountStaticSitemap,
}
