# Configure VS Code

This guide addresses how to configure VS Code for an efficient Panel development workflow.

We assume you have

- a basic understanding of [developing Panel apps in an editor](editor.md) and [working with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial).
- installed the VS Code [Python extension](https://github.com/Microsoft/vscode-python)

---

## Debugging

To learn how to use the *integrated debugger* in general check out [the official guide](https://code.visualstudio.com/docs/editor/debugging).

To configure the integrated debugger for Panel, you will need to add a debugging configuration like the below.

```bash
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "panel serve",
            "type": "python",
            "request": "launch",
            "program": "-m",
            "args": [
                "panel",
                "serve",
                "${relativeFile}",
                "--show"
            ],
            "console": "integratedTerminal",
            "justMyCode": true
        },
    ]
}
```

In use it looks like

![Integrated Debugging of a Panel app in VS Code](../../_static/vscode-integrated-debugging.png)

## Extensions

The following extensions will help speed up your Panel workflow

- [Live Server](https://github.com/ritwickdey/vscode-live-server-plus-plus): Enables you to easily view `.html` files created using `.save()` or `panel convert`.

## General Settings

We recommend adding the below to your `settings.json` file.

```bash
"explorer.copyRelativePathSeparator": "/" # Relevant on Windows only
```

## Keyboard Shortcuts

To speed up your workflow we recommend configuring a keyboard short cut to `panel serve` your app.

```bash
[
    {
        "key": "ctrl+shift+space",
        "command": "workbench.action.terminal.sendSequence",
        "args": { "text": "panel serve ${relativeFile} --autoreload --show\u000D" }
    }
]
```

On Windows you will need to add quotes around `${relativeFile}`, i.e. replace it with `'${relativeFile}'`.

When you press `CTRL+SHIFT+SPACE` you will `panel serve` your file in the terminal, if you have an open terminal.

## Notebook and Interactive Environment

Ensure you install `jupyter_bokeh` with `pip install jupyter_bokeh` or `conda install -c bokeh jupyter_bokeh` and then enable the extension with `pn.extension()`.

You can see a notebook in action below.

![Panel in VS Code Notebook Environment](../../_static/vscode-notebook.png)

## Snippets

To speed up your workflow you can configure [*user defined snippets*](https://code.visualstudio.com/docs/editor/userdefinedsnippets) like these [example Panel snippets](../../_static/json/vscode-snippets-python.json). When you start typing `import panel` you will get the option to select between the snippets as shown below.

![Panel VS Code Snippets](../../_static/vscode-snippets-python.png)

The snippets will be available in the script, notebook and the interactive environments.
