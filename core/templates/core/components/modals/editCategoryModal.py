from django_components import Component, register
@register('editCategoryModal')
class EditCategoryModal(Component):
    template_name = 'editCategoryModal.html'
    def get_context_data(self, *args, **kwargs):
        return kwargs