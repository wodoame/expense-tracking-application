from django_components import Component, register

@register('selectField')
class SelectField(Component):
    template_name = 'selectField.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs