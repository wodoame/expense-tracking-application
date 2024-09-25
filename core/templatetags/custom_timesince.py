from django import template
from django.utils.timesince import timesince as django_timesince
from core.datechecker import DateChecker as dc

# https://docs.djangoproject.com/en/5.1/howto/custom-template-tags/
# when you add a new tag or filter restart the server
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
        if value == dc.get_date_today(): 
            return 'Today'
        elif value == dc.get_date_yesterday():
            return 'Yesterday' 
        return str(django_timesince(value, arg).split(',')[0]) + ' ago'
    except (ValueError, TypeError):
        return ''