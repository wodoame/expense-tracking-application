from django_components import Component, register

@register('recordOptionsDropdown')
class RecordOptionsDropdown(Component):
    template_name = 'recordOptionsDropdown.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs