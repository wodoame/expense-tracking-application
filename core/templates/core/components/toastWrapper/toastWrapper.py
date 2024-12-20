from django_components import Component, register

@register('toastWrapper')
class ToastWrapper(Component):
    template_name = 'toastWrapper.html'
    class Media:
        js = 'js/toast.js'