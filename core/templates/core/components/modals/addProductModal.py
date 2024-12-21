from django_components import Component, register

@register('addProductModal')
class AddProductModal(Component):
    template_name = 'addProductModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs