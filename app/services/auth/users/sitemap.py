from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class UsersStaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.3

    def items(self):
        return ["register_user", "login"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "users_static": UsersStaticSitemap,
}
