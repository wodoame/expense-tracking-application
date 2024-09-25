from django import template
from django.utils.timesince import timesince as django_timesince
# https://docs.djangoproject.com/en/5.1/howto/custom-template-tags/
register = template.Library()

@register.filter
def timesince(value, arg=None):
    """
    Returns the number of days since the given date/time.
    Removes the hours/minutes/seconds components from the output.
    """
    if not value:
        return ''

    try:
        return str(int(django_timesince(value, arg).split(',')[0])) + ' day(s) ago'
    except (ValueError, TypeError):
        return ''