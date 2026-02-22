Figure X – Numerical validation panels (Matplotlib)
===================================================

This folder provides a minimal, fully runnable plotting pipeline to generate the 3-panel Figure X used in the manuscript.

Quickstart
----------
1) Create a virtual environment and install requirements:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2) Run the plotting script on the included example data:
   python scripts/plot_figureX.py --data-dir data/examples --out-dir figures --observable Lambda14

Outputs
-------
- figures/figX_panelA_convergence.pdf/png
- figures/figX_panelB_epsratio.pdf/png
- figures/figX_panelC_residuals.pdf/png
- figures/figX_3panel.pdf/png
- figures/plot_metadata.json   (generated from plot_metadata.json.template)

Replace example inputs with your real analysis outputs by writing files with the same schemas
(see data/examples/* for reference).


### High-resolution exports
Use `--dpi 600` to generate 600 dpi PNG/TIFF outputs alongside vector PDFs:

```bash
python scripts/plot_figureX.py --data-dir data/examples --out-dir figures --observable Lambda14 --dpi 600
```
