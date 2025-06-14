## Overview
Page implementations are the actual content of the page.
Page implementations replace skeleton representations of the page.
They are stored in `core\templates\core\implementations`.
They are loaded by views in `core/views.py`. For example

```py
# ... existing code
context = {
    'dateToday':dateToday, 
    'dateYesterday':dateYesterday, 
    'today': today, 
    'yesterday':yesterday,
    'todayTotal':todayTotal,
    'yesterdayTotal':yesterdayTotal,
    }
    return render(request, 'core/implementations/dashboard.html', context)
# ... existing code
```

## Notes
1. Page implementations may contain skeletons which are responsible for loading other parts of the page. This may be because those parts of the page are compute intensive (and so are fetched after some main information is ready to be displayed) or handled by another route.

## Examples
### Dashboard implementation
```django
<!-- ... existing code  -->
{% include 'core/components/statSummarySkeleton2.html' %}
<div class="grid grid-cols-1 mt-4 md:grid-cols-2 gap-4 items-start" id="product-items">
  <!-- today  -->
   {% include 'core/components/records.html' with products=today date=dateToday total=todayTotal only %}
   
   <!-- yesterday -->
   {% include 'core/components/records.html' with products=yesterday date=dateYesterday total=yesterdayTotal only %}

</div> 
<!-- ... existing code -->
```