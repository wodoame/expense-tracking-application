from django_components import Component, register

@register('deleteCategoryModal')
class DeleteCategoryModal(Component):
    template_name = 'deleteCategoryModal.html'
    
    def get_context_data(self, *args, **kwargs):
        return kwargs
    