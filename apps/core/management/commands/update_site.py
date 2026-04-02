from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    help = "Update Site object using SITE_NAME and SITE_DOMAIN settings."

    def handle(self, *args, **options):
        if settings.DEBUG:
            site_name = "Localhost"
            site_domain = "localhost:8000"
        else:
            site_name = getattr(settings, "SITE_NAME", None)
            site_domain = getattr(settings, "SITE_DOMAIN", None)
            if not site_name or not site_domain:
                msg = "SITE_NAME and SITE_DOMAIN settings must be defined."
                raise CommandError(msg)

        try:
            site = Site.objects.get_current()
        except Exception as exc:
            msg = f"Error retrieving current site: {exc}"
            raise CommandError(msg) from exc

        site.name = site_name
        site.domain = site_domain
        site.save()
        self.stdout.write(self.style.SUCCESS("Site updated successfully."))
