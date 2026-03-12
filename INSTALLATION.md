# Installation notes

Installation is intentionally minimal, but older scientific Python environments can still surface resolver noise.

- Use a fresh environment when possible. aeon/sktime/numba ecosystems can produce resolver warnings even when echowave itself installs correctly.
- Core install stays intentionally small: numpy and scipy.
- For tabular IO use echowave[io]. For parquet support use echowave[parquet].
- For mixed scientific stacks, export a compatibility preset and install with constraints instead of doing a bare install.
- If you only want to evaluate product value first, use the static playground or starter notebooks before integrating into a larger stack.
- Zero-install and low-friction entry points in this version: static playground, local live demo server, Colab notebook, and uvx CLI pattern.

# Environment doctor

Environment is usable, but tsontology recommends safer install and HTML-output paths for this stack.

## Watchouts

- stdout encoding is gbk; HTML-heavy guide output should go to a file or browser instead of the terminal.
- mixed scientific-stack packages are present (aeon/sktime/numba); resolver warnings are more likely in an existing environment.
- no active virtual environment detected.

## Recommended next steps

- Use `--output file.html`, `--export-pages docs`, or `tsontology-demo --open-browser` instead of printing raw HTML to the terminal.
- Use the mixed scientific-stack constraints profile instead of a bare install.
- Create a dedicated environment for the cleanest install experience.
- Use `tsontology-demo --open-browser` to evaluate the product surface without wiring tsontology into an existing notebook stack.
- Use `tsontology --export-pages docs` to generate a GitHub-Pages-ready static demo bundle.
- Use `tsontology --write-constraints constraints/mixed-scientific-stack.txt --constraint-profile mixed-scientific-stack` to export a concrete constraints file.