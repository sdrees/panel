# Basic Tutorials

Welcome to the Basic Tutorials!

Are you ready to dive into the exciting world of Panel? Our Basic Tutorials are designed to guide you step by step through building awesome apps with wind turbine data. Whether you're a beginner or an enthusiast, we've got you covered! And don't hesitate to reach out on [Discord](https://discord.gg/rb6gPXbdAr) if you need help along the way.

## Prerequisites

Before we dive in, make sure you've followed along with our [Getting Started Guide](../../getting_started/index.md).

Please execute the following command to install the dependencies required by the basic tutorials:

::::{tab-set}

:::{tab-item} pip
:sync: pip

```bash
pip install altair hvplot matplotlib numpy pandas panel plotly scipy watchfiles
```

:::

:::{tab-item} conda
:sync: conda

```bash
conda install -y -c conda-forge altair hvplot matplotlib numpy pandas panel plotly scipy watchfiles
```

:::

::::

:::{important}
Is Panel installed together with JupyterLab/Jupyter Notebook in your working environment? If not, you need to make sure that `panel` is also installed in the same environment as JupyterLab/Jupyter Notebook (`pip install panel` or `conda install panel`).
:::

## Let's Get Started

Start your journey with these foundational tutorials:

- **[Build Hello World App](serve.md):** Kick things off with a simple app.
- **[Develop in Notebooks](develop_notebook.md):** Learn how to build apps right in your notebooks.
- **[Develop in Editors](develop_editor.md):** Explore tips for developing in your favorite code editor.

## Master Panel Basics

Once you're comfortable, it's time to dive deeper:

| Part | Section A | Section B| Section C |
|--------------------------|---------------------------|-------------------|------------------------------------------------------|
| **1. Display Content**       | [`pn.panel`](pn_panel.md) | [Panes](panes.md) | [Performance Indicators](indicators_performance.md) |
| **2. Organize Content**      | [Layouts](layouts.md)    | [Control the Size](size.md) | [Align Content](align.md)                           |
| **3. Handle User Input**     | [Widgets](widgets.md)    | [React to User Input](pn_bind.md) | [Handle State](state.md)                        |
| **4. Improve the look**      | [Templates](templates.md)| [Designs](design.md) | [Styles](style.md)                                |
| **5. Improve the Feel**      | [Caching](caching.md)    | [Activity Indicators](indicators_activity.md) | [Progressive Updates](progressive_layouts.md)  |

## Share Your Creations

Share your awesome apps with the world!

- **[Build a Dashboard](build_dashboard.md)**
- **[Deploy a Dashboard](deploy.md)**

## Ready for Projects?

Now that you've got the basics down, it's time to put your skills to the test:

- **[Build a Report](build_report.md)**
- **[Build a Monitoring Dashboard](build_monitoring_dashboard.md)**
- **[Build an Animation](build_animation.md)**
- **[Build a Todo App](build_todo.md)**
- **[Build an Image Classifier](build_image_classifier.md)**
- **[Build a Streaming Dashboard](build_streaming_dashboard.md)**
- **[Build a Chat Bot](build_chatbot.md)**

Let's start building some amazing wind turbine apps! 🌬️🌀

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

serve
develop_notebook
develop_editor
pn_panel
panes
indicators_performance
layouts
size
align
widgets
pn_bind
state
caching
indicators_activity
progressive_layouts
templates
design
style
build_dashboard
deploy
build_report
build_monitoring_dashboard
build_animation
build_todo
build_image_classifier
build_streaming_dashboard
build_chatbot
```
