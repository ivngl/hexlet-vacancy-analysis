from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PasswordResetStaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.2

    def items(self):
        return ["password_reset"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "password_reset_static": PasswordResetStaticSitemap,
}
