from django_components import Component, register

@register('searchModal')
class SearchModal(Component):
    template_name = 'searchModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs