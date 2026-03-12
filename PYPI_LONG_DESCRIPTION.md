# EchoWave

**Explainable time-series similarity for humans and agents.**

[![PyPI version](https://img.shields.io/pypi/v/echowave?style=flat-square)](https://pypi.org/project/echowave/)
[![Python versions](https://img.shields.io/pypi/pyversions/echowave?style=flat-square)](https://pypi.org/project/echowave/)
[![License: MIT](https://img.shields.io/badge/license-MIT-0b6cff?style=flat-square)](LICENSE)
[![Status: Beta](https://img.shields.io/badge/status-beta-dd6b20?style=flat-square)](https://github.com/ZipengWu365/EchoWave)
[![Docs: GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-0a7f5a?style=flat-square)](https://zipengwu365.github.io/EchoWave/)

EchoWave compares time series and time-series datasets, explains why they match or differ, and emits compact JSON plus shareable HTML reports.

Formerly published under the **tsontology** name. EchoWave is the renamed package and keeps the legacy import and CLI aliases during the migration window.

## Why this package exists

Most time-series tooling helps after you decide what to model. EchoWave helps one step earlier: compare two signals clearly, compare two datasets structurally, and emit a result that a human or an agent can actually act on.

## Quickstart

```bash
pip install echowave
python -c "import numpy as np; from echowave import compare_series; x=np.sin(np.linspace(0,8*np.pi,128)); y=np.sin(np.linspace(0,8*np.pi,128)+0.2); print(compare_series(x,y).to_summary_card_markdown())"
```

Expected output starts like this:

```text
# EchoWave similarity summary
overall similarity: ...
top components: shape similarity, trend similarity, spectral similarity
```

## What ships in v0.16.0

- compare-first public package surface
- agent-ready JSON wrappers with stable envelopes
- GitHub Pages-ready docs bundle
- local live demo for pasted arrays
- starter datasets, notebooks, and flagship demos
- compatibility presets and environment doctor guidance for mixed scientific stacks

## Common entry points

- `echowave-demo --open-browser`
- `tsontology-demo --open-browser` (legacy alias)
- `echowave --guide quickstart`
- `echowave --guide doctor`
- `echowave --export-pages docs`

## Links

- README: `README.md`
- Start here: `START_HERE.md`
- Compatibility: `COMPATIBILITY.md`
- Local live demo: `LIVE_DEMO.md`
- Agent input contract: `AGENT_INPUT_CONTRACT.md`

## Maintainer

- **Zipeng Wu**
- The University of Birmingham
- zxw365@student.bham.ac.uk
- https://github.com/ZipengWu365/EchoWave

## Legacy compatibility

The historical package name `tsontology` is still kept as a compatibility shim in this release, but the official package name and branding are now **EchoWave** / `echowave`.
