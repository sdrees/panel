"""
Script that removes large files from bokeh wheel and repackages it
to be included in the NPM bundle.
"""

import argparse
import os
import pathlib
import shutil
import subprocess
import zipfile

from importlib.metadata import version

from packaging.version import Version

PANEL_BASE = pathlib.Path(__file__).parent.parent
bokeh_version = Version(version("bokeh"))
bokeh_dev = bokeh_version.is_devrelease

parser = argparse.ArgumentParser()
parser.add_argument("out", default="panel/dist/wheels", nargs="?", help="Output dir")
parser.add_argument(
    "--no-deps",
    action="store_true",
    default=False,
    help="Don't install package dependencies.",
)
args = parser.parse_args()

command = ["pip", "wheel", "."]
if bokeh_dev:
    command.append("--pre")

if args.no_deps:
    command.append("--no-deps")
command.extend(["-w", str(PANEL_BASE / "build")])
print("command: ", " ".join(command))

out = PANEL_BASE / args.out
out.mkdir(exist_ok=True)
print("out dir: ", out)

sp = subprocess.Popen(command, env=dict(os.environ, PANEL_LITE="1"))
sp.wait()


panel_wheels = list(PANEL_BASE.glob("build/panel-*-py3-none-any.whl"))
if not panel_wheels:
    raise RuntimeError("Panel wheel not found.")
panel_wheel = sorted(panel_wheels)[-1]

if bokeh_dev:
    zin = zipfile.ZipFile(panel_wheel, "r")
    zout = zipfile.ZipFile(out / os.path.basename(panel_wheel).replace(".dirty", ""), "w")
    for item in zin.infolist():
        filename = item.filename
        buffer = zin.read(filename)
        if filename.startswith("panel-") and filename.endswith("METADATA"):
            lines = buffer.decode("utf-8").split("\n")
            lines = [
                f"Requires-Dist: bokeh =={bokeh_version}"
                if line.startswith("Requires-Dist: bokeh")
                else line for line in lines
            ]
            buffer = "\n".join(lines).encode('utf-8')
        zout.writestr(item, buffer)
else:
    shutil.copyfile(panel_wheel, out / os.path.basename(panel_wheel).replace(".dirty", ""))

bokeh_wheels = PANEL_BASE.glob("build/bokeh-*-py3-none-any.whl")

if not bokeh_wheels:
    raise RuntimeError("Bokeh wheel not found.")
bokeh_wheel = sorted(bokeh_wheels)[-1]

zin = zipfile.ZipFile(bokeh_wheel, "r")

zout = zipfile.ZipFile(out / os.path.basename(bokeh_wheel), "w")
exts = [".js", ".d.ts", ".tsbuildinfo"]
for item in zin.infolist():
    filename = item.filename
    buffer = zin.read(filename)
    if not filename.startswith("bokeh/core/_templates") and (
        filename.endswith("bokeh.json") or any(filename.endswith(ext) for ext in exts)
    ):
        continue
    elif filename.startswith("bokeh-") and filename.endswith("METADATA"):
        # remove tornado dependency
        buffer = "\n".join(
            [
                line
                for line in buffer.decode("utf-8").split("\n")
                if not (
                    "Requires-Dist:" in line
                    and ("tornado" in line or "contourpy" in line)
                )
            ]
        ).encode("utf-8")
    zout.writestr(item, buffer)

zout.close()
zin.close()

print(f"\nWheels where successfully written to {out}")
