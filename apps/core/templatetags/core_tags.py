from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(
    context,
    *view_names,
    css_class: str = "active",
    prefix_match: bool = False,
    ignore_params: str = "page",
    **params,
) -> str:
    """Return a `css_class` ("active" by default) if the current request matches
    any of the specified `view_names` and optional `params`.

    Matches `request.resolver_match.view_name` against `view_names` (exact match by
    default; prefix match when `prefix_match=True`). If `params` are provided, all
    must match the merged request parameters (URL kwargs + query string). Query
    string values take precedence over URL kwargs when keys overlap.

    Args:
        context: Template context (must include `request`).
        *view_names: URL names to match (e.g., "orders:list").
        css_class: Class to return on match (default: "active").
        prefix_match: Use prefix matching for view names.
        ignore_params: Comma-separated query parameter names to ignore
            when matching (default: "page").
        **params: Expected URL kwargs and/or query parameters.

    Returns:
        `css_class` on match; otherwise "".
    """
    request = context.get("request")
    resolver_match = getattr(request, "resolver_match", None) if request else None
    current_view_name = getattr(resolver_match, "view_name", None)
    if not current_view_name:
        return ""

    view_matches = (
        any(current_view_name.startswith(name) for name in view_names)
        if prefix_match
        else current_view_name in view_names
    )
    if not view_matches:
        return ""

    if params:
        expected_params = {str(k): str(v) for k, v in params.items()}
        url_kwargs = {str(k): str(v) for k, v in (resolver_match.kwargs or {}).items()}
        ignored_params = {p.strip() for p in ignore_params.split(",") if p.strip()}
        query_params = {
            str(k): str(v) for k, v in request.GET.items() if k not in ignored_params
        }
        url_kwargs.update(query_params)
        if any(url_kwargs.get(k) != v for k, v in expected_params.items()):
            return ""

    return css_class
