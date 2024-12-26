from django_components import Component, register

@register('deleteProductModal')
class DeleteProductModal(Component):
    template_name = 'deleteProductModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs