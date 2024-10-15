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


The datetime string `2024-10-15T08:52:01.380160Z` is in the **ISO 8601** format. This format is widely used for representing date and time in a standardized way. Here's a breakdown of the components:

- `2024-10-15`: The date part in `YYYY-MM-DD` format.
- `T`: The separator between the date and time parts.
- `08:52:01.380160`: The time part in `HH:MM:SS.ssssss` format, where `ssssss` represents fractional seconds.
- `Z`: Indicates that the time is in UTC (Coordinated Universal Time).

This format is commonly used in APIs and databases because it is unambiguous and easily sortable.

To extract only the time from the ISO 8601 datetime string `2024-10-15T08:52:01.380160Z`, you can use Python's `datetime` module. Here's how you can do it:

```python
from datetime import datetime

iso_datetime_str = "2024-10-15T08:52:01.380160Z"
parsed_datetime = datetime.fromisoformat(iso_datetime_str.replace("Z", "+00:00"))

# Extract the time part
time_only = parsed_datetime.time()

print(time_only)
```

In this example:
- The `datetime.fromisoformat` method parses the ISO 8601 string into a `datetime` object.
- The `time()` method extracts the time part from the `datetime` object.

The output will be:
```
08:52:01.380160
```