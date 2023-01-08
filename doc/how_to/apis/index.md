# APIs

Panel can be used to make a first pass at an app or dashboard in minutes, while also allowing you to fully customize the app's behavior and appearance or flexibly integrate GUI support into long-term, large-scale software projects. To accommodate these different ways of using Panel, four different APIs are available:

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} Reactive Functions
:link: reactive
:link-type: doc

Linking functions or methods to widgets using ``pn.bind`` or the equivalent ``pn.depends`` decorator.
:::

:::{grid-item-card} Interact functions
:link: interact
:link-type: doc

Auto-generates a full UI (including widgets) given a function.
:::

:::{grid-item-card} Parameterized class
:link: parameterized
:link-type: doc

Declare parameters and their ranges in `Parameterized` classes, then get GUIs (and value checking!) for free.
:::


:::{grid-item-card} Callbacks
:link: callbacks
:link-type: doc

Generate a UI by manually declaring callbacks that update panels or panes.
:::

::::

Each of these APIs has its own benefits and drawbacks, so this section will go through each one in turn, while working through an example app and pointing out the benefits and drawback along the way. For a quick overview you can also review the API gallery examples, e.g. the [stocks_hvplot](../../gallery/apis/stocks_hvplot.ipynb) app.

As you will discover, each of these four APIs allows building the same basic application. The choice of the appropriate API depends very much on the use case. To build a quick throwaway GUI the ``interact`` approach can be completely sufficient. A much more explicit, flexible, and maintainable version of that approach is to define a reactive function that is bound directly to a set of widgets using `pn.bind`. When writing libraries or other code that might be used independently of the actual GUI, a Parameterized class can be a great way to organize the code.

Finally, if you need low-level control or want to complement any of the other approaches, defining explicit callbacks can be the best approach. Nearly all of the functionality of Panel can be accessed using any of the APIs, but each makes certain things much easier than others. Choosing the API is therefore a matter of considering the tradeoffs and of course also a matter of preference. If you still aren't sure after reading the above, then just go with the `pn.bind` reactive API!

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

reactive
interact
parameterized
callbacks
```