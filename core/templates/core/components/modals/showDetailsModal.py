from django_components import Component, register

@register('showDetailsModal')
class DeleteProductModal(Component):
    template_name = 'showDetailsModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs