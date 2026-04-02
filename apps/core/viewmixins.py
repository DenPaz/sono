from django.core.exceptions import ImproperlyConfigured


class HtmxTemplateMixin:
    """Render an alternative template for HTMX requests.

    Views using this mixin must define `htmx_template_name`, which can be either
    a full template name or a fragment identifier (starting with `#`) to be appended
    to the default template name.

    Behavior:
        - If the request is not HTMX, the view's normal template resolution is used.
        - If the request is HTMX and `htmx_template_name` starts with `#`, it is
          appended to the primary template name (e.g., `app/template.html#fragment`).
        - Otherwise, `htmx_template_name` is used as the sole template.

    Raises:
        ImproperlyConfigured: If `htmx_template_name` is not set.

    Returns:
        list[str]: A list of template names to be used for rendering the response.
    """

    htmx_template_name: str | None = None

    def dispatch(self, request, *args, **kwargs):
        if not self.htmx_template_name:
            msg = (
                f"{self.__class__.__name__} is missing `htmx_template_name`. "
                "Define it or remove HtmxTemplateMixin from the view."
            )
            raise ImproperlyConfigured(msg)
        return super().dispatch(request, *args, **kwargs)

    def is_htmx(self) -> bool:
        return getattr(self.request, "htmx", False)

    def get_template_names(self) -> list[str]:
        template_names = super().get_template_names()
        if not self.is_htmx():
            return template_names
        if self.htmx_template_name.startswith("#"):
            return [template_names[0] + self.htmx_template_name]
        return [self.htmx_template_name]
