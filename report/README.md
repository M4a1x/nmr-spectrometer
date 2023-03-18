# Report

## Technical
This report is based on the [`latex-cookbook`](https://github.com/alexpovel/latex-cookbook) by Alex Povel.
It's a _modern_ template for LuaLaTeX _only_, using a lot of its new features.
Additionally, this is inspired by [`kaobook`](https://github.com/fmarotta/kaobook) by Federico Marotta (which in turn was inspired by Ken Arroyo Ohori and `tufte-latex`) and [`latex-mimosis`](https://github.com/Pseudomanifold/latex-mimosis) by Bastian Rieck.
Finally, some ETH specific stuff has been added, for example, the official [ETH Colorscheme](https://ethz.ch/staffnet/en/service/communication/corporate-design/farbe.html).

## Installation
### Docker
Since this is using recent software with requirements especially on the TexLive installation that is not available even in recent Linux Distributions (e.g. `tabularray` is only available in TexLive 2022 or newer). The official `texlive/texlive:latest` docker image is used. You need to setup `docker` and open this folder directly (`./report`) in Visual Studio Code. It will prompt you to open the folder "inside the remote". Compiling works by simply pressing e.g. `Ctrl+Shift+P` and running `LaTeX Workshop: Build LaTeX project...` or `Ctrl+Alt+B`.

### Manual
I haven't done this till now, but at least the following software is required:
* `TexLive (2022)` or equivalent (MikTeX, ...)
* `python3` and `python-pygments` (for `minted`)
* `openjdk-17-jdk` (for `glossaries-extra`)
