# Control Visibility

All components provide a `visible` parameter which toggles a component's visibility.

Let's create three simple components with different colors. We'll set the visibility parameter of the blue one to `False`:

```{pyodide}

import panel as pn
pn.extension() # for notebook

a = pn.pane.HTML(width=60, height=60, styles=dict(background='green'))
b = pn.pane.HTML(width=60, height=60, styles=dict(background='blue'), visible=False)
c = pn.pane.HTML(width=60, height=60, styles=dict(background='red'))

layout = pn.Row(a, b, c)
layout

```

In some cases, exposing control of component visibility within the user interface may come in handy. To achieve this, we can use the `controls` method on a component to create a widget that allows for the manipulation of the `visibility` parameter. For instance, toggling this checkbox will update the visibility of the blue `b` component above:

```{pyodide}
b.controls(['visible'])[1]
```
