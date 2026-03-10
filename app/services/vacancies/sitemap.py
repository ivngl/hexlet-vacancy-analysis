from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class VacanciesStaticSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ["vacancy_list"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "vacancies_static": VacanciesStaticSitemap,
}
