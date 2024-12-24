# Overview
Components are found in the component directory of any particular app. For example the core components are found in `core/templates/core/components`.

A component consists of a `.py`, `.html`, `.css` and `.js` file.
These files define a component. The folder for a component will typically look like this:  
```
├── mycomponent/
    ├── mycomponent.py
    ├── mycomponent.html
    ├── mycomponent.css
    ├── mycomponent.js
```
Javascript and CSS files can live elsewhere other than in the directory `mycomponent`. 
This architecture for creating components is in accordance with the principles of [django-components library](https://emilstenstrom.github.io/django-components/latest/overview/welcome/)


# Creating a Component
You will usually see something like this in the html templates
```html
{% component 'mycomponent' / %}
```
This is a neat encapsulation of a component. After a component is created it can be registered and used as a tag as seen above. This is beneficial because:
1. It promotes code reusability 
1. You don't have to worry about the actual implementation of the component. 
1. Dependencies like JavaScript and CSS files are automatically included in the template

Initially we were using
```html 
{% include 'path/to/mycomponent.html' %}
```
This also improves code reusability but it doesn't have the level of encapsulation as `{% component 'mycomponent' / %}` since the developer has to remember which dependencies (JavaScript and CSS) to apply to the component and include them in the template. 
This method is not abandoned though since it's useful for reusing some html that don't necessarily deserve to be a dedicated component. So it's not common to see that syntax also in the codebase since some older components may even depend on that approach.

## The Python File
In the Python file of a component you'll typically see something like this
```python
from django_components import Component, register

@register('mycomponent')
class MyComponent(Component):
    template_name = 'mycomponent.html'
    class Media: 
        js = 'mycomponent.js'
        css = 'mycomponent.css'
```
This file is responsible for registering a component so that we can use the tag `{% component 'mycomponent' / %}` in the templates. 

# Conclusion
To understand more about creating components and what's possible you can read visit the [official documentation for django-components](https://emilstenstrom.github.io/django-components/latest/overview/welcome/)



