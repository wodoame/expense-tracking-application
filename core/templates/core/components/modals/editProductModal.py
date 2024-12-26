from django_components import Component, register

@register('editProductModal')
class DeleteProductModal(Component):
    template_name = 'editProductModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs