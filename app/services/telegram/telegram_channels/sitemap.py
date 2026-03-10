from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class TelegramChannelsStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.3

    def items(self):
        return ["channels_list"]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "telegram_channels_static": TelegramChannelsStaticSitemap,
}
