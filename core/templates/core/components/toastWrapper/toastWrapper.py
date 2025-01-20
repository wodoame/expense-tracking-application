from django_components import Component, register

@register('toastWrapper')
class ToastWrapper(Component):
    template_name = 'toastWrapper.html'