In Django, the `timesince` template filter is used to display the time since a given date/time. By default, it will show the time in a format like "2 days, 6 hours ago".

If you want to remove the hours component from the output and just show the days, you can create a custom template filter to achieve this.

Here's how you can do it:

1. In your Django app, create a new file called `templatetags.py` (or any other name you prefer) and add the following code:

```python
from django import template
from django.utils.timesince import timesince as django_timesince

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
```

2. In your Django template, you can then use the custom `timesince` filter like this:

```html
{{ my_date|timesince }}
```

This will output the time since the `my_date` field in a format like "2 day(s) ago", without the hours/minutes/seconds information.

The key points are:

- We create a custom template filter called `timesince` that wraps the built-in `django_timesince` function.
- We split the output of `django_timesince` on the comma to extract just the days component.
- We then convert the days value to an integer and append the "day(s) ago" text.

This allows you to easily modify the output of the `timesince` filter to suit your specific needs.