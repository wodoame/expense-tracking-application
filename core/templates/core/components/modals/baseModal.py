from django_components import Component, register

@register('baseModal')
class BaseModal(Component):
    template_name = 'baseModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs