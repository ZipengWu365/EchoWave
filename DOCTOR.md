# Environment doctor

`tsontology` now treats environment diagnosis as a product feature, not just a warning message.

## What the doctor checks

- Python version and platform
- stdout / terminal encoding
- whether you are in a virtual environment
- installed versions of `numpy`, `scipy`, `pandas`, `aeon`, `sktime`, and `numba`
- whether a mixed scientific stack is likely to produce resolver warnings

## Run it

```bash
tsontology --guide doctor
```

## What changed in v0.16.0

The doctor no longer stops at “be careful”. It now points you to:

- a **recommended compatibility profile**
- **exact next-step install commands**
- a **constraints export command** you can run immediately

## Common fixes

### HTML guide output on a non-UTF terminal

If your console uses `gbk`, `cp936`, or another non-UTF encoding, prefer one of these paths:

```bash
tsontology --guide homepage --output homepage.html
tsontology --export-pages docs
tsontology-demo --open-browser
```

### Mixed scientific Python stack

```bash
tsontology --write-constraints constraints/mixed-scientific-stack.txt --constraint-profile mixed-scientific-stack
pip install -c constraints/mixed-scientific-stack.txt tsontology
```

### Clean fresh environment

```bash
tsontology --write-constraints constraints/clean-venv.txt --constraint-profile clean-venv
pip install -c constraints/clean-venv.txt tsontology
```
