from django_components import Component, register

@register('baseDropdown')
class BaseDropdown(Component):
    template_name = 'baseDropdown.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs