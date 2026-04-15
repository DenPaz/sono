from django.views.generic import RedirectView


class IndexView(RedirectView):
    pattern_name = "assessments:overview"
    permanent = False
    query_string = True
