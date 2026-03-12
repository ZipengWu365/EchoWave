import React from "react";

const trustBadges = [
  "MIT License",
  "Beta release",
  "GitHub Pages",
  "Cross-disciplinary",
];

const features = [
  {
    label: "Representations",
    title: "Scientific features without black-box packaging",
    body: "Build and inspect time-series representations that are readable enough for researchers and robust enough for engineering handoff.",
    tone: "blue",
  },
  {
    label: "Benchmarks",
    title: "Reproducible evaluation surfaces",
    body: "Show benchmark assumptions, artifacts, and limitations in a way that helps people trust the result instead of just copying a leaderboard number.",
    tone: "sun",
  },
  {
    label: "Agents",
    title: "Structured outputs for automation",
    body: "Wrap core technical tasks in stable JSON so downstream agents and apps can route and consume them without scraping notebook prose.",
    tone: "blue",
  },
];

const workflow = [
  {
    step: "01",
    title: "Bring in a dataset",
    body: "Start with arrays, tables, or a small benchmark-ready sample.",
  },
  {
    step: "02",
    title: "Inspect the structure",
    body: "Compare signals, surface assumptions, and generate a shareable artifact.",
  },
  {
    step: "03",
    title: "Hand off the result",
    body: "Export code-ready output, report cards, and ecosystem links for the next repo or agent.",
  },
];

const ecosystem = [
  { name: "TSLab Core", role: "Representation learning and scientific utilities" },
  { name: "TSLab Bench", role: "Benchmark orchestration and result packaging" },
  { name: "TSLab Agents", role: "Agent wrappers and tool contracts for research automation" },
];

export default function TSLabLanding() {
  return (
    <div className="min-h-screen bg-white text-slate-800">
      <div className="absolute inset-x-0 top-0 -z-10 h-[420px] bg-[radial-gradient(circle_at_top_right,_rgba(255,226,122,0.18),_transparent_26%),linear-gradient(180deg,_#fffef8_0%,_#ffffff_26%,_#ffffff_100%)]" />

      <header className="sticky top-0 z-30 border-b border-slate-200/90 bg-white/90 backdrop-blur">
        <div className="mx-auto flex min-h-[72px] w-full max-w-6xl items-center justify-between gap-6 px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="h-5 w-5 rounded-md bg-gradient-to-br from-[#FFC83D] to-[#FFE27A]" />
            <div>
              <p className="text-[1.08rem] font-semibold tracking-[-0.02em]">TSLab</p>
              <p className="text-sm text-slate-500">Bright scientific open-source tools</p>
            </div>
          </div>
          <nav className="hidden gap-6 text-sm font-medium text-slate-500 md:flex">
            <a href="#features" className="transition hover:text-slate-800">
              Features
            </a>
            <a href="#workflow" className="transition hover:text-slate-800">
              Workflow
            </a>
            <a href="#quickstart" className="transition hover:text-slate-800">
              Quickstart
            </a>
            <a href="#ecosystem" className="transition hover:text-slate-800">
              Ecosystem
            </a>
          </nav>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-col gap-20 px-4 pb-20 pt-10 sm:px-6">
        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="flex flex-col gap-5">
            <span className="inline-flex w-fit items-center rounded-full border border-yellow-300/70 bg-[#FFF4C2] px-3 py-1 text-xs font-extrabold uppercase tracking-[0.12em] text-[#C7950A]">
              Research lab style
            </span>
            <div className="space-y-4">
              <h1 className="max-w-4xl text-5xl font-semibold leading-[0.95] tracking-[-0.05em] text-slate-900 sm:text-6xl">
                Build bright, trustworthy scientific tools for time-series research.
              </h1>
              <p className="max-w-3xl text-lg leading-8 text-slate-500">
                TSLab is a reusable landing-page surface for open-source technical products: white-first, sunlight yellow accents, restrained scientific blue, and strong information hierarchy.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <a
                href="#quickstart"
                className="inline-flex min-h-12 items-center justify-center rounded-full border border-yellow-300 bg-gradient-to-b from-[#FFD65F] to-[#FFC83D] px-5 text-sm font-semibold text-slate-900 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift"
              >
                Run quickstart
              </a>
              <a
                href="#ecosystem"
                className="inline-flex min-h-12 items-center justify-center rounded-full border border-blue-200 bg-blue-50 px-5 text-sm font-semibold text-[#2554CC] shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift"
              >
                View ecosystem
              </a>
            </div>

            <div className="flex flex-wrap gap-3">
              {trustBadges.map((badge) => (
                <span
                  key={badge}
                  className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-500"
                >
                  <span className="h-2.5 w-2.5 rounded-full bg-gradient-to-br from-[#FFC83D] to-[#2F6BFF]" />
                  {badge}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
            <div className="mb-4 inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] text-[#2554CC]">
              Productized open source
            </div>
            <div className="grid gap-4">
              <div className="rounded-2xl border border-yellow-300/70 bg-gradient-to-b from-[#FFF9E4] to-white p-5">
                <p className="text-sm font-semibold text-[#C7950A]">What this style communicates</p>
                <p className="mt-2 text-sm leading-7 text-slate-600">
                  Clarity, growth, scientific confidence, and technical seriousness without dark AI cliches.
                </p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-[#FAFAFA] p-5">
                <p className="font-semibold tracking-[-0.02em] text-slate-900">Recommended visual ingredients</p>
                <ul className="mt-3 space-y-2 text-sm leading-7 text-slate-600">
                  <li>Inter for copy and hierarchy</li>
                  <li>JetBrains Mono for code and commands</li>
                  <li>Yellow for energy, blue for science</li>
                  <li>Quiet cards, strong spacing, simple trust badges</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="space-y-6">
          <div className="space-y-3">
            <span className="inline-flex rounded-full border border-yellow-300/70 bg-[#FFF4C2] px-3 py-1 text-xs font-extrabold uppercase tracking-[0.12em] text-[#C7950A]">
              Key features
            </span>
            <h2 className="text-3xl font-semibold tracking-[-0.04em] text-slate-900">
              One design system across docs, dashboards, and repo landing pages
            </h2>
            <p className="max-w-3xl text-base leading-8 text-slate-500">
              Keep the palette and spacing consistent so a benchmark dashboard, a README, and a Pages landing page feel like part of the same lab.
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            {features.map((feature) => (
              <div
                key={feature.title}
                className={`rounded-[20px] border p-6 shadow-soft ${
                  feature.tone === "sun"
                    ? "border-yellow-300/70 bg-gradient-to-b from-[#FFF9E4] to-white"
                    : "border-slate-200 bg-white"
                }`}
              >
                <span
                  className={`inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.12em] ${
                    feature.tone === "sun"
                      ? "bg-[#FFF4C2] text-[#C7950A]"
                      : "bg-blue-50 text-[#2554CC]"
                  }`}
                >
                  {feature.label}
                </span>
                <h3 className="mt-4 text-lg font-semibold tracking-[-0.03em] text-slate-900">{feature.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{feature.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="workflow" className="space-y-6">
          <div className="space-y-3">
            <span className="inline-flex rounded-full border border-yellow-300/70 bg-[#FFF4C2] px-3 py-1 text-xs font-extrabold uppercase tracking-[0.12em] text-[#C7950A]">
              Example workflow
            </span>
            <h2 className="text-3xl font-semibold tracking-[-0.04em] text-slate-900">
              From raw dataset to a clean ecosystem handoff
            </h2>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            {workflow.map((item) => (
              <div key={item.step} className="rounded-[20px] border border-slate-200 bg-white p-6 shadow-soft">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#FFC83D] text-sm font-extrabold text-slate-900">
                  {item.step}
                </span>
                <h3 className="mt-4 text-lg font-semibold tracking-[-0.03em] text-slate-900">{item.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{item.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="quickstart" className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="rounded-[20px] border border-slate-200 bg-white p-6 shadow-soft">
            <span className="inline-flex rounded-full border border-yellow-300/70 bg-[#FFF4C2] px-3 py-1 text-xs font-extrabold uppercase tracking-[0.12em] text-[#C7950A]">
              Quickstart
            </span>
            <h2 className="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-900">
              The first minute should feel obvious
            </h2>
            <div className="mt-5 rounded-2xl border border-slate-200 bg-[#FFFEF8] p-4 font-mono text-sm leading-7 text-slate-800">
              <div>pnpm add tslab</div>
              <div>npm run demo</div>
            </div>
          </div>

          <div className="rounded-[20px] border border-slate-200 bg-[#FAFAFA] p-6 shadow-soft">
            <span className="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-extrabold uppercase tracking-[0.12em] text-[#2554CC]">
              Example surface
            </span>
            <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-5">
              <p className="text-sm font-semibold text-slate-900">Repo ecosystem modules</p>
              <div className="mt-4 grid gap-3">
                {ecosystem.map((repo) => (
                  <div key={repo.name} className="rounded-2xl border border-slate-200 bg-[#FAFAFA] px-4 py-3">
                    <p className="font-semibold text-slate-900">{repo.name}</p>
                    <p className="text-sm text-slate-500">{repo.role}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="ecosystem" className="rounded-[28px] border border-yellow-300/70 bg-gradient-to-b from-[#FFF9E4] to-white p-8 shadow-soft">
          <div className="max-w-3xl space-y-3">
            <span className="inline-flex rounded-full border border-yellow-300/70 bg-white px-3 py-1 text-xs font-extrabold uppercase tracking-[0.12em] text-[#C7950A]">
              Final CTA
            </span>
            <h2 className="text-3xl font-semibold tracking-[-0.04em] text-slate-900">
              Use one visual language across your GitHub repo family.
            </h2>
            <p className="text-base leading-8 text-slate-600">
              The payoff is not novelty. It is recognition, easier adoption, and a stronger technical identity every time someone lands on another repo in the ecosystem.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <a
                href="#"
                className="inline-flex min-h-12 items-center justify-center rounded-full border border-yellow-300 bg-gradient-to-b from-[#FFD65F] to-[#FFC83D] px-5 text-sm font-semibold text-slate-900 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift"
              >
                Reuse this layout
              </a>
              <a
                href="#"
                className="inline-flex min-h-12 items-center justify-center rounded-full border border-blue-200 bg-white px-5 text-sm font-semibold text-[#2554CC] shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift"
              >
                Open docs
              </a>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
