from django_components import Component, register

@register('chart')
class Chart(Component):
    template_name = 'chart.html'