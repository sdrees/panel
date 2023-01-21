# Access and Set Widget Values

In addition to other parameters that govern widget behavior and appearance, Widget objects have a ``value`` parameter that can be used to access the current value state.


Let's first create a `TextInput` widget:

```{pyodide}
import panel as pn
pn.extension() # for notebook

widget = pn.widgets.TextInput(name='A widget', value='A string')
widget
```

Now we can programmatically access its value:

```{pyodide}
widget.value
```

We can also use this value parameter to set the widget value:

```{pyodide}
widget.value = '3'
```

:::{admonition} See Also
:class: seealso

* Learn more about Widgets in the <a href="../../background/components/components_overview.html#widgets">Background for Components</a>
:::
