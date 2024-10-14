from django import template
from django.utils.timesince import timesince as django_timesince
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def timesince(value, arg=None):
    """
    Returns the number of days since the given date/time.
    Removes the hours/minutes/seconds components from the output.
    """
    try:
        dateToday = datetime.today().date()
        dateYesterday = dateToday - timedelta(days=1)
        if value == dateToday:
            return 'Today'
        elif value == dateYesterday: 
            return 'Yesterday'
        return str(django_timesince(value, arg).split(',')[0]) + ' ago'
    except (ValueError, TypeError):
        return ''