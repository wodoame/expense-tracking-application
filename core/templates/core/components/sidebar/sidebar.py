from django_components import Component, register

@register('sidebar')
class Sidebar(Component): 
    template_name = 'sidebar.html'
 