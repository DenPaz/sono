from __future__ import annotations

import json

import pytest
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory

from apps.core.middleware import HtmxMessagesMiddleware


class _TruthyHtmx:
    boosted = False

    def __bool__(self):
        return True


@pytest.mark.django_db

def test_htmx_messages_middleware_ignores_invalid_hx_trigger_json():
    request = RequestFactory().get("/operacional/")
    SessionMiddleware(lambda _request: None).process_request(request)
    request.session.save()
    request.htmx = _TruthyHtmx()
    request.__dict__["_messages"] = FallbackStorage(request)

    messages.success(request, "Mensagem de teste")

    response = HttpResponse("ok")
    response.headers["HX-Trigger"] = "{invalid"

    middleware = HtmxMessagesMiddleware(lambda _request: response)
    result = middleware(request)

    trigger_payload = json.loads(result.headers["HX-Trigger"])
    assert "messages" in trigger_payload
    assert trigger_payload["messages"][0]["message"] == "Mensagem de teste"
