## Overview
Pages are stored in `core\templates\core\pages`. 

A page follows this structure in general
1. Inherits the layout template
```django
    {% extends 'core/pages/layout.html' %}
```
2. Inserts some content into the `main` block of the page which is usually a loading skeleton or placeholder typically stored in `core\templates\core\placeholders`
```django
    {% block main %}
    {% include 'core/placeholders/someLoadingSkeleton.html' %}
    {% endblock %}
```


## Notes
1. The loading skeleton is responsible for loading the actual html content or the [implementation of the page](./page-implementations.md). This is done via `HTMX`.
2. Note that loading skeletons of the page may not be one giant html skeleton but can be a composition of smaller skeletons.
    ```django
    {% include 'path/to/skeleton1' %}
    {% include 'path/to/skeleton2' %}
    {% include 'path/to/skeleton3' %}
    ```
    One of these skeletons will be responsible for getting the [implementation of the page](./page-implementations.md)
3. The `main` block of the page is the dymanic part of the page. This is where content is swapped in and out of the DOM dynamically via `HTMX`

## Examples
### Loading the dashboard page
- In `core\templates\core\pages\dashboard.html`
```django
{% extends 'core/pages/layout.html' %}
{% block main %}
    {% include 'core/placeholders/dashboardSkeleton.html' %}
{% endblock %}
```
- The `dashboardSkeleton` is made up of other skeletons
```django
{% include 'core/components/pageHeading.html' with text="Dashboard" %}

{% include 'core/components/statSummarySkeleton.html' %}
        <!-- begin activity -->
<div class="grid grid-cols-1 mt-4 md:grid-cols-2 gap-4 items-start" id="product-items">
  <!-- today  -->
   {% include 'core/components/staticRecordSkeleton.html' %}

   <!-- yesterday -->
   {% include 'core/components/staticRecordSkeleton.html' %}
</div>
<!-- activity -->
```

- The `statSummarySkeleton` is responsible for getting the implementation of the page
```html
<!-- ... existing code -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-2 gap-y-4" id="statSummarySkeleton" hx-get="/implementations/dashboard/" hx-target="#main-content" hx-trigger="load">
<!-- ... existing code -->
```