import json

from django.contrib.messages import get_messages


class HtmxMessagesMiddleware:
    """Middleware to add Django messages to HTMX responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not request.htmx or request.htmx.boosted:
            return response

        if 300 <= response.status_code < 400:  # noqa: PLR2004
            return response

        if "HX-Redirect" in response.headers:
            return response

        messages = [
            {"message": str(message.message), "tags": str(message.tags)}
            for message in get_messages(request)
        ]
        if not messages:
            return response

        hx_trigger = response.headers.get("HX-Trigger")
        if hx_trigger is None:
            triggers = {}
        elif hx_trigger.startswith("{"):
            try:
                triggers = json.loads(hx_trigger)
            except json.JSONDecodeError:
                triggers = {}
        else:
            triggers = {hx_trigger: True}

        triggers["messages"] = messages
        response.headers["HX-Trigger"] = json.dumps(triggers, default=str)
        return response
