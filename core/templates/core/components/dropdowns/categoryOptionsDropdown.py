from django_components import Component, register

@register('categoryOptionsDropdown')
class CategoryOptionsDropdown(Component):
    template_name = 'categoryOptionsDropdown.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs