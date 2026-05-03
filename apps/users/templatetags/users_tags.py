from django import template

register = template.Library()


class RoleCheckNode(template.Node):
    def __init__(self, roles, nodelist):
        self.roles = [role.strip("'\"") for role in roles]
        self.nodelist = nodelist

    def render(self, context):
        request = context.get("request")
        if not request or not request.user.is_authenticated:
            return ""
        if request.user.role in self.roles:
            return self.nodelist.render(context)
        return ""


@register.tag(name="withrole")
def withrole_tag(parser, token):
    """Block tag to conditionally render content based on the user's role.

    Usage:
        {% withrole 'ADMIN' 'SPECIALIST' %}
            ... content for admins and specialists ...
        {% endwithrole %}
    """
    roles = token.split_contents()[1:]
    nodelist = parser.parse(("endwithrole",))
    parser.delete_first_token()
    return RoleCheckNode(roles, nodelist)
