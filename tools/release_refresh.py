from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from echowave import (  # noqa: E402
    agent_schema_guide,
    agent_manifest,
    case_studies_guide,
    doctor_guide,
    github_readme,
    installation_guide,
    integration_templates_guide,
    live_demo_guide,
    mcp_tool_descriptors,
    openai_function_schemas,
    pages_deploy_guide,
    project_demo_manifest,
    project_docs_pages,
    project_homepage_html,
    project_launchpad_html,
    project_playground_html,
    pypi_long_description,
    quickstart_guide,
    routing_contract_guide,
    similarity_method_atlas_guide,
    starter_datasets_guide,
    start_here_guide,
    tool_schemas,
    trust_guide,
    utility_benchmark_guide,
    write_pages_bundle,
    zero_install_guide,
)
from echowave.demo_server import demo_server_html  # noqa: E402
from tools.generate_preview_assets import generate_preview_assets  # noqa: E402


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    _write(path, json.dumps(payload, indent=2))


def _copy(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _zip_dir(source_dir: Path, archive_path: Path) -> None:
    archive_path.unlink(missing_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(source_dir.rglob("*")):
            if file.is_file():
                zf.write(file, file.relative_to(source_dir))


def _release_draft() -> str:
    return """# EchoWave v0.16.0 Release Draft

## Headline

EchoWave v0.16.0 is the first fully branded release surface for the renamed package: official package name, Pages-ready title card, local demo entry points, compatibility presets, and PyPI release copy now all point to the same product story.

## Official package name

- Brand: EchoWave
- PyPI package: `echowave`
- Legacy compatibility shim: `tsontology`

## Release highlights

- compare-first README and homepage
- PyPI long description tailored for package index readers
- GitHub Pages-ready title card and refreshed visual language
- compatibility-aware onboarding for mixed scientific stacks
- root/docs release assets regenerated from one refresh script

## Entry points

```bash
pip install echowave
echowave-demo --open-browser
echowave --guide doctor
echowave --export-pages docs
```

## Compatibility note

The old `tsontology` package name remains callable in this release as a compatibility shim, but the official product name is now EchoWave.
"""


def main() -> None:
    generate_preview_assets(ROOT)

    _write(ROOT / "README.generated.md", github_readme())
    _write(ROOT / "README.md", github_readme())
    _write(ROOT / "PYPI_LONG_DESCRIPTION.md", pypi_long_description())
    _write(ROOT / "homepage.html", project_homepage_html())
    _write(ROOT / "playground.html", project_playground_html())
    _write(ROOT / "start-here.html", project_launchpad_html())
    _write(ROOT / "local_demo.html", demo_server_html())
    for rel, content in project_docs_pages().items():
        _write(ROOT / rel, content)

    _write(ROOT / "START_HERE.md", start_here_guide())
    _write(ROOT / "INSTALLATION.md", installation_guide() + "\n\n" + doctor_guide())
    _write(ROOT / "ZERO_INSTALL.md", zero_install_guide())
    _write(ROOT / "LIVE_DEMO.md", live_demo_guide())
    _write(ROOT / "PAGES_DEPLOYMENT.md", pages_deploy_guide())
    _write(ROOT / "INTEGRATIONS.md", integration_templates_guide())
    _write(ROOT / "CASE_STUDIES.md", case_studies_guide())
    _write(ROOT / "TRUST.md", trust_guide())
    _write(ROOT / "STARTER_DATASETS.md", starter_datasets_guide())
    _write(ROOT / "AGENT_SCHEMAS.md", agent_schema_guide())
    _write(ROOT / "ROUTING_CONTRACTS.md", routing_contract_guide())
    _write(ROOT / "SIMILARITY_METHOD_ATLAS.md", similarity_method_atlas_guide())
    _write(ROOT / "UTILITY_BENCHMARK.md", utility_benchmark_guide())
    _write(ROOT / "PROJECT_HOMEPAGE.md", "# EchoWave homepage\n\nUse `homepage.html` or `docs/index.html` as the official GitHub Pages front door.\n")
    _write(ROOT / "RELEASE_DRAFT_v0.16.0.md", _release_draft())

    _write_json(ROOT / "AGENT_TOOL_SCHEMAS.json", tool_schemas(format="dict"))
    _write_json(ROOT / "OPENAI_FUNCTION_SCHEMAS.json", openai_function_schemas(format="dict"))
    _write_json(ROOT / "MCP_TOOL_DESCRIPTORS.json", mcp_tool_descriptors(format="dict"))
    _write_json(ROOT / "DEMO_MANIFEST.json", project_demo_manifest())
    _write_json(ROOT / "AGENT_MANIFEST.json", agent_manifest(format="json"))

    docs_dir = ROOT / "docs"
    audit_dir = ROOT / "audit_pages_out"
    write_pages_bundle(docs_dir)
    write_pages_bundle(audit_dir)

    _copy(ROOT / "assets" / "echowave_title_card.svg", ROOT / "social" / "echowave_title_card.svg")
    _copy(ROOT / "assets" / "echowave_mark.svg", ROOT / "social" / "echowave_mark.svg")
    _copy(ROOT / "assets" / "bham_affiliation_badge.svg", ROOT / "social" / "bham_affiliation_badge.svg")
    _copy(ROOT / "assets" / "echowave_title_card.svg", docs_dir / "social" / "echowave_title_card.svg")
    _copy(ROOT / "assets" / "echowave_mark.svg", docs_dir / "social" / "echowave_mark.svg")
    _copy(ROOT / "assets" / "bham_affiliation_badge.svg", docs_dir / "social" / "bham_affiliation_badge.svg")
    _copy(ROOT / "assets" / "echowave_title_card.png", ROOT / "social" / "echowave_title_card.png")
    _copy(ROOT / "assets" / "echowave_title_card.png", docs_dir / "social" / "echowave_title_card.png")

    _zip_dir(docs_dir, ROOT / "echowave_v0.16_pages_bundle.zip")
    print("release surface refreshed")


if __name__ == "__main__":
    main()
