from django import template
from django.conf import settings

register = template.Library()

@register.tag
def experimental(parser, token):
    """
    Custom template tag to render enclosed HTML only when DEBUG is True.
    Usage:
    {% experimental %}
        <p>This is experimental HTML.</p>
    {% endexperimental %}
    """
    nodelist = parser.parse(('endexperimental',))
    parser.delete_first_token()
    return ExperimentalNode(nodelist)

class ExperimentalNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # Check if DEBUG is True in settings
        if settings.DEBUG:
            return self.nodelist.render(context)
        return ''
