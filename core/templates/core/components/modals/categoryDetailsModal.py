from django_components import Component, register

@register('categoryDetailsModal')
class CategoryDetailsModal(Component):
    template_name = 'categoryDetailsModal.html'
    def get_context_data(self, *args, **kwargs):
        return kwargs