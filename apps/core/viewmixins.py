from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django_htmx.http import HttpResponseClientRedirect


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


class HtmxFormSuccessMixin:
    """Return HX-Redirect instead of a plain 302 on successful form submission.

    Without this, HTMX follows the 302 and swaps the full user-list page HTML
    into the modal target div. HX-Redirect causes HTMX to perform a full browser
    navigation instead, and any queued Django messages survive in the session.
    """

    def form_valid(self, form):
        response = super().form_valid(form)
        if getattr(self.request, "htmx", False):
            return HttpResponseClientRedirect(self.get_success_url())
        return response


class AllowedRolesMixin(UserPassesTestMixin):
    """Restrict view access to users with specific roles.

    Views using this mixin must define `allowed_roles` as a list of role values
    from `UserRole`. Unauthenticated users are redirected to the login page.
    Authenticated users whose role is not in `allowed_roles` are handled by
    `handle_no_permission()` (403 by default, or redirect to login if
    `raise_exception` is False).

    Attributes:
        allowed_roles: A list of role values (e.g. [UserRole.ADMIN]).

    Raises:
        ImproperlyConfigured: If `allowed_roles` is None (not configured).

    Example:
        class UserListView(AllowedRolesMixin, FilterView):
            allowed_roles = [UserRole.ADMIN]
    """

    allowed_roles: list | None = None

    def test_func(self):
        if self.allowed_roles is None:
            msg = (
                f"{self.__class__.__name__} is missing `allowed_roles`. "
                "Define it or remove AllowedRolesMixin from the view."
            )
            raise ImproperlyConfigured(msg)
        user = self.request.user
        return user.is_authenticated and user.role in self.allowed_roles
