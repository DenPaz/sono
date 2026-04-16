from django.views import View
from django.views.i18n import set_language


class SetLanguageView(View):
    def post(self, request, *args, **kwargs):
        language = request.POST.get("language")
        if language and hasattr(request.user, "profile"):
            profile = request.user.profile
            profile.language = language
            profile.save(update_fields=["language", "modified"])
        return set_language(request)
