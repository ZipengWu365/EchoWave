# Local live demo

Run the local EchoWave live demo when you want a real interactive similarity surface without building a web stack.

## Commands

- `pip install echowave`
- `echowave-demo --open-browser`
- `tsontology-demo --open-browser`
- `echowave --serve-demo --open-browser`
- `python -m tsontology.demo_server --open-browser`

## Notes

- The local live demo is compute-backed: pasted arrays and starter cases generate real similarity verdicts and HTML reports.
- The legacy tsontology-demo alias stays available so older scripts and docs do not break while the brand migrates.
- The GitHub Pages playground stays static and showcase-oriented; use the live demo when you need real computation.