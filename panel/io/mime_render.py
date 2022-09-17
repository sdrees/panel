"""
Utilities for executing Python code and rendering the resulting output
using a similar MIME-type based rendering system as implemented by
IPython.

Attempts to limit the actual MIME types that have to be rendered on
to a minimum simplifying frontend implementation:

    - application/bokeh: Model JSON representation
    - text/plain: HTML escaped string output
    - text/html: HTML code to insert into the DOM
"""

from __future__ import annotations

import ast
import base64
import copy
import io
import traceback

from contextlib import redirect_stderr, redirect_stdout
from html import escape
from typing import Any, Dict

import markdown

UNDEFINED = object()

#---------------------------------------------------------------------
# Execution API
#---------------------------------------------------------------------

def _convert_expr(expr: ast.Expr) -> ast.Expression:
    """
    Converts an ast.Expr to and ast.Expression that can be compiled
    and evaled.
    """
    expr.lineno = 0
    expr.col_offset = 0
    return ast.Expression(expr.value, lineno=0, col_offset = 0)

def exec_with_return(code: str, global_context: Dict[str, Any] = None) -> Any:
    """
    Executes a code snippet and returns the resulting output of the
    last line.

    Arguments
    ---------
    code: str
      The code to execute
    global_context: Dict[str, Any]
      The globals to inject into the execution context.

    Returns
    -------

    The return value of the executed code and stdout and stederr output.
    """
    global_context = global_context if global_context else globals()
    code_ast = ast.parse(code)

    init_ast = copy.deepcopy(code_ast)
    init_ast.body = code_ast.body[:-1]

    last_ast = copy.deepcopy(code_ast)
    last_ast.body = code_ast.body[-1:]

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            exec(compile(init_ast, "<ast>", "exec"), global_context)
            if type(last_ast.body[0]) == ast.Expr:
                out = eval(compile(_convert_expr(last_ast.body[0]), "<ast>", "eval"), global_context)
            else:
                exec(compile(last_ast, "<ast>", "exec"), global_context)
                out = UNDEFINED
        except Exception:
            out = UNDEFINED
            traceback.print_exc(file=stderr)
    return out, stdout.getvalue(), stderr.getvalue()

#---------------------------------------------------------------------
# MIME Render API
#---------------------------------------------------------------------

MIME_METHODS = {
    "__repr__": "text/plain",
    "_repr_html_": "text/html",
    "_repr_markdown_": "text/markdown",
    "_repr_svg_": "image/svg+xml",
    "_repr_png_": "image/png",
    "_repr_pdf_": "application/pdf",
    "_repr_jpeg_": "image/jpeg",
    "_repr_latex": "text/latex",
    "_repr_json_": "application/json",
    "_repr_javascript_": "application/javascript",
    "savefig": "image/png"
}

# Rendering function

def render_svg(value, meta, mime):
    return value, 'text/html'

def render_image(value, meta, mime):
    data = f"data:{mime};charset=utf-8;base64,{value}"
    attrs = " ".join(['{k}="{v}"' for k, v in meta.items()])
    return f'<img src="{data}" {attrs}</img>', 'text/html'

def render_javascript(value, meta, mime):
    return f'<script>{value}</script>', 'text/html'

def render_markdown(value, meta, mime):
    return (markdown.markdown(
        value, extensions=["extra", "smarty", "codehilite"], output_format='html5'
    ), 'text/html')

def render_pdf(value, meta, mime):
    data = value.encode('utf-8')
    base64_pdf = base64.b64encode(data).decode("utf-8")
    src = f"data:application/pdf;base64,{base64_pdf}"
    return f'<embed src="{src}" width="100%" height="100%" type="application/pdf">', 'text/html'

def identity(value, meta, mime):
    return value, mime

MIME_RENDERERS = {
    "image/png": render_image,
    "image/jpeg": render_image,
    "image/svg+xml": identity,
    "application/json": identity,
    "application/javascript": render_javascript,
    "application/pdf": render_pdf,
    "text/html": identity,
    "text/markdown": render_markdown,
    "text/plain": identity,
}

def eval_formatter(obj, print_method):
    """
    Evaluates a formatter method.
    """
    if print_method == "__repr__":
        return repr(obj)
    elif hasattr(obj, print_method):
        if print_method == "savefig":
            buf = io.BytesIO()
            obj.savefig(buf, format="png")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode("utf-8")
        return getattr(obj, print_method)()
    elif print_method == "_repr_mimebundle_":
        return {}, {}
    return None

def format_mime(obj):
    """
    Formats object using _repr_x_ methods.
    """
    if isinstance(obj, str):
        return escape(obj), "text/plain"
    mimebundle = eval_formatter(obj, "_repr_mimebundle_")
    if isinstance(mimebundle, tuple):
        format_dict, _ = mimebundle
    else:
        format_dict = mimebundle

    output, not_available = None, []
    for method, mime_type in reversed(list(MIME_METHODS.items())):
        if mime_type in format_dict:
            output = format_dict[mime_type]
        else:
            output = eval_formatter(obj, method)

        if output is None:
            continue
        elif mime_type not in MIME_RENDERERS:
            not_available.append(mime_type)
            continue
        break
    if output is None:
        output = repr(output)
        mime_type = "text/plain"
    elif isinstance(output, tuple):
        output, meta = output
    else:
        meta = {}
    content, mime_type = MIME_RENDERERS[mime_type](output, meta, mime_type)
    if mime_type == 'text/plain':
        content = escape(content)
    return content, mime_type
