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
        if isinstance(value, str): 
            value = datetime.strptime(value, '%Y-%m-%d').date()
        dateToday = datetime.today().date()
        dateYesterday = dateToday - timedelta(days=1)
        if value == dateToday:
            return 'Today'
        elif value == dateYesterday: 
            return 'Yesterday'
        return str(django_timesince(value, arg).split(',')[0]) + ' ago'
    except (ValueError, TypeError):
        return ''
@register.filter
def timeOnly(value, arg=None):
    """
    Converts a string date to datetime.time object.
    """
    if isinstance(value, str): 
        parsedDatetime = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsedDatetime.time()
    return value.time()