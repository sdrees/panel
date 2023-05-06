import json
import os
import pathlib

import param

param.parameterized.docstring_signature = False
param.parameterized.docstring_describe_params = False

from nbsite.shared_conf import *

project = 'Panel'
authors = 'Panel contributors'
copyright_years['start_year'] = '2019'
copyright = copyright_fmt.format(**copyright_years)
description = 'High-level dashboarding for python visualization libraries'

import panel

from panel.io.convert import BOKEH_VERSION, PY_VERSION
from panel.io.resources import CDN_DIST

PANEL_ROOT = pathlib.Path(panel.__file__).parent

version = release = base_version(panel.__version__)
js_version = json.loads((PANEL_ROOT / 'package.json').read_text())['version']

is_dev = any(ext in version for ext in ('a', 'b', 'rc'))

# For the interactivity warning box created by nbsite to point to the right
# git tag instead of the default i.e. main.
os.environ['BRANCH'] = f"v{release}"

html_static_path += ['_static']

html_css_files = [
    'nbsite.css',
    'css/custom.css',
    'css/dataframe.css',
]

html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo_horizontal.png"
html_favicon = "_static/icons/favicon.ico"

html_theme_options = {
    "github_url": "https://github.com/holoviz/panel",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/Panel_Org",
            "icon": "fa-brands fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/c/panel/5",
            "icon": "fa-brands fa-discourse",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/muhupDZM",
            "icon": "fa-brands fa-discord",
        },
    ],
    "google_analytics_id": "UA-154795830-2",
    "pygment_light_style": "material",
    "pygment_dark_style": "material",
    "header_links_before_dropdown": 5,
    'secondary_sidebar_items': [
        "panelitelink",
        "page-toc",
    ],
}

extensions += [
    'sphinx.ext.napoleon',
    'nbsite.gallery',
    'sphinx_copybutton',
    'nbsite.pyodide'
]
napoleon_numpy_docstring = True

myst_enable_extensions = ["colon_fence", "deflist"]

gallery_endpoint = 'panel-gallery-dev' if is_dev else 'panel-gallery'

if not is_dev:
    jlite_url = 'https://panelite.holoviz.org'
else:
    jlite_url = 'https://pyviz-dev.github.io/panelite-dev'


nbsite_gallery_conf = {
    'github_org': 'holoviz',
    'github_project': 'panel',
    'galleries': {
        'reference': {
            'title': 'Component Gallery',
            'sections': [
                'panes',
                'layouts',
                'templates',
                'global',
                'indicators',
                'widgets',
            ],
            'titles': {
                'Vega': 'Altair & Vega',
                'DeckGL': 'PyDeck & Deck.gl',
                'ECharts': 'PyEcharts & ECharts',
                'IPyWidget': 'ipywidgets'
            },
            'as_pyodide': True,
            'normalize_titles': False
        }
    },
    'thumbnail_url': 'https://assets.holoviz.org/panel/thumbnails',
    'deployment_url': f'https://{gallery_endpoint}.pyviz.demo.anaconda.com/',
    'jupyterlite_url': jlite_url,
}

if panel.__version__ != version and (PANEL_ROOT / 'dist' / 'wheels').is_dir():
    py_version = panel.__version__.replace("-dirty", "")
    panel_req = f'./wheels/panel-{py_version}-py3-none-any.whl'
    bokeh_req = f'./wheels/bokeh-{BOKEH_VERSION}-py3-none-any.whl'
else:
    panel_req = f'{CDN_DIST}wheels/panel-{PY_VERSION}-py3-none-any.whl'
    bokeh_req = f'{CDN_DIST}wheels/bokeh-{BOKEH_VERSION}-py3-none-any.whl'

def get_requirements():
    with open('pyodide_dependencies.json') as deps:
        dependencies = json.load(deps)
    requirements = {}
    for name, deps in dependencies.items():
        if deps is None:
            continue
        name = name.replace('.ipynb', '').replace('.md', '')
        # Temporary patch for HoloViews
        if any('holoviews' in req for req in deps):
            reqs = ['holoviews>=1.16.0a7' if 'holoviews' in req else req for req in deps]
        elif any('hvplot' in req for req in deps):
            deps.insert(0, 'holoviews>=1.16.0a7')
        requirements[name] = deps
    return requirements

nbsite_pyodide_conf = {
    'PYODIDE_URL': 'https://cdn.jsdelivr.net/pyodide/v0.23.1/full/pyodide.js',
    'requirements': [bokeh_req, panel_req, 'pyodide-http'],
    'requires': get_requirements()
}

templates_path = [
    '_templates'
]

html_context.update({
    "last_release": f"v{release}",
    "github_user": "holoviz",
    "github_repo": "panel",
    "default_mode": "light",
    "panelite_endpoint": jlite_url,
})

nbbuild_patterns_to_take_along = ["simple.html", "*.json", "json_*"]

# Override the Sphinx default title that appends `documentation`
html_title = f'{project} v{version}'



# Patching GridItemCardDirective to be able to substitute the domain name
# in the link option.
from sphinx_design.grids import GridItemCardDirective  # noqa

orig_run = GridItemCardDirective.run

def patched_run(self):
    app = self.state.document.settings.env.app
    existing_link = self.options.get('link')
    domain = getattr(app.config, 'grid_item_link_domain', None)
    if existing_link and domain:
        new_link = existing_link.replace('|gallery-endpoint|', domain)
        self.options['link'] = new_link
    return list(orig_run(self))

GridItemCardDirective.run = patched_run

def setup(app) -> None:
    app.add_config_value('grid_item_link_domain', '', 'html')

grid_item_link_domain = gallery_endpoint
