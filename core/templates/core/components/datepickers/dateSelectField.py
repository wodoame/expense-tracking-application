from django_components import Component, register

@register('dateSelectField')
class DateSelectField(Component):
    template_name = 'dateSelectField.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs