from django_components import Component, register

@register('addCategoryModal')
class AddProductModal(Component):
    template_name = 'addCategoryModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs