# Access Pane Type

To access the type for a given component, use the ``pprint`` method. This can come in handy when a component was created in such a way where the type was not explicitly specified, such as with ``pn.panel`` as described on the [How to construct panes page](construct_panes.md).

```{pyodide}
import panel as pn
pn.extension() # for notebook

example_pane = pn.panel('https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif', width=500)

example_pane.pprint()
```

:::{admonition} See Also
:class: seealso
* Learn more about Panes in the <a href="../../background/components/components_overview.html#panes">Background for Components</a>
:::
