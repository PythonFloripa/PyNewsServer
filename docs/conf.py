# -- Project information -----------------------------------------------------
project = "pynewsserver"
author = "PyNews"

# -- General configuration ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx_rtd_theme",
    "sphinxcontrib.redoc",
    "sphinx_copybutton",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "linkify",
    "substitution",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_title = "Documentação - PyNewsServer"
html_static_path = ['_static']

# -- Options for sphinxcontrib-redoc -----------------------------------------
redoc = [
    {
        "name": "OpenAPI",
        "page": "api",
        "spec": "../openapi.json",
        "embed": True,
        "opts": {
            "hide-hostname": True
        }
    },
]
