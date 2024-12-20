from django_components import Component, register

@register('themeToggler')
class ThemeToggler(Component):
    template_name = 'themeToggler.html'