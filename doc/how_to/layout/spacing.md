# Customize Spacing

This guide addresses how to customize the spacing between elements.

---

The spacing between components is controlled by setting the margin parameter on individual components and by adding Spacers between components.

## Margin Parameter

The ``margin`` parameter can be used to create space around an element defined as the number of pixels at the (top, right, bottom, and left). The ``margin`` can be defined in one of three ways:

``` python
margin=25
    # top, bottom, left, and right margins are 25px

margin=(25, 50)
    # top and bottom margins are 25px
    # right and left margins are 50px

margin=(25, 50, 75, 100)
    # top margin is 25px
    # right margin is 50px
    # bottom margin is 75px
    # left margin is 100px
```

For example, let's create three buttons and customize their margin. To make it easier to see the margin area, we'll embed each into a `Column` and then shade the `Column` background.

```{pyodide}

import panel as pn
pn.extension() # for notebook

pn.Row(
    pn.Column(pn.widgets.Button(name='B1', width=100, margin=25), background='#f0f0f0'),
    pn.Column(pn.widgets.Button(name='B2', width=100, margin=(40, 50)), background='#f0f0f0'),
    pn.Column(pn.widgets.Button(name='B3', width=100, margin=(25, 50, 75, 100)), background='#f0f0f0'))

```

## Spacer Components

Spacer components make it easy to put fixed or responsive spacing between objects.

First, let's add fixed-width Spacers in between some numbers:

```{pyodide}
pn.Row(
    1,
    pn.Spacer(width=200),
    2,
    pn.Spacer(width=100),
    3,
    pn.Spacer(width=50),
    4,
    pn.Spacer(width=25),
    5
)
```

Instead of absolute spacing, we could use ``VSpacer`` or ``HSpacer`` components to provide responsive vertical and horizontal spacing, respectively. Using these components we can space objects equidistantly in a layout and allow the empty space to shrink when the browser is resized.

```{pyodide}
pn.Row(
    pn.layout.HSpacer(),
    '* Item 1\n* Item2',
    pn.layout.HSpacer(),
    '1. First\n2. Second',
    pn.layout.HSpacer()
)
```

---

## Related Resources
