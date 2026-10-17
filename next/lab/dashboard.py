"""results/dashboard.html: the report as charts, for a quick look in the browser.

Carson built a dashboard on day one (cb-bc/dashboard: rating progression, win matrix, match stats).
This is the small version: one self-contained HTML file, no server, no packages.
"""
from __future__ import annotations

import html
import time

COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#4b5563", "#db2777"]


def _chart(series: dict[str, list[tuple[float, float]]], title: str, xlab: str, ylab: str) -> str:
    pts = [p for s in series.values() for p in s]
    if not pts:
        return ""
    W, H, L, B = 640, 300, 56, 36
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(0, min(p[1] for p in pts)), max(p[1] for p in pts) or 1
    if x1 == x0:
        x1 = x0 + 1
    sx = lambda x: L + (x - x0) / (x1 - x0) * (W - L - 28)  # noqa: E731
    sy = lambda y: H - B - (y - y0) / (y1 - y0) * (H - B - 12)  # noqa: E731
    out = [f'<figure><figcaption>{html.escape(title)}</figcaption><svg viewBox="0 0 {W} {H}" role="img">']
    for i in range(5):
        y = y0 + (y1 - y0) * i / 4
        out.append(f'<line x1="{L}" x2="{W - 28}" y1="{sy(y):.1f}" y2="{sy(y):.1f}" class="grid"/>'
                   f'<text x="{L - 6}" y="{sy(y) + 4:.1f}" text-anchor="end">{y:.0f}</text>')
    for x in (x0, (x0 + x1) / 2, x1):
        out.append(f'<text x="{sx(x):.1f}" y="{H - B + 18}" text-anchor="middle">{x:.0f}</text>')
    out.append(f'<text x="{(L + W) / 2}" y="{H - 4}" text-anchor="middle">{html.escape(xlab)}</text>')
    out.append(f'<text x="12" y="{H / 2}" transform="rotate(-90 12 {H / 2})" text-anchor="middle">{html.escape(ylab)}</text>')
    legend = []
    for i, (name, s) in enumerate(series.items()):
        c = COLORS[i % len(COLORS)]
        d = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in s)
        out.append(f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="2"/>')
        legend.append(f'<span><i style="background:{c}"></i>{html.escape(name)}</span>')
    out.append("</svg>")
    out.append('<div class="legend">' + "".join(legend) + "</div></figure>")
    return "".join(out)


def write(path, summary: dict, history: list[dict], report_md: str) -> None:
    names = sorted(summary["ratings"], key=summary["ratings"].get, reverse=True)
    rows = "".join(f"<tr><td>{i}</td><td><code>{html.escape(v)}</code></td><td>{summary['ratings'][v]:.0f}</td></tr>"
                   for i, v in enumerate(names, 1))
    gems = _chart({v: summary["_curves"][v] for v in names}, "Banked gems by round (mean over games)", "round", "gems")
    prog = {}
    for h in [x for x in history if x.get("panel_version") == summary["panel_version"]] + [summary]:
        for v, r in h["ratings"].items():
            prog.setdefault(v, []).append((len(prog.get(v, [])) + 1, r))
    runs = _chart({v: prog[v] for v in names if len(prog.get(v, [])) > 1}, "Rating per league run", "run", "rating")
    page = f"""<!doctype html><meta charset="utf-8"><title>League dashboard</title>
<style>
:root{{--bg:#f7f8fa;--fg:#17202a;--muted:#5b6672;--line:#d8dde3}}
@media (prefers-color-scheme:dark){{:root{{--bg:#12171c;--fg:#e4e9ee;--muted:#9aa6b2;--line:#2b343d}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;max-width:900px;margin:0 auto;padding:24px 16px}}
h1{{font-size:1.6rem;margin:0 0 4px}} .muted{{color:var(--muted)}}
table{{border-collapse:collapse}} td,th{{padding:4px 12px;border-bottom:1px solid var(--line);text-align:left}}
figure{{margin:24px 0}} figcaption{{font-weight:600;margin-bottom:6px}} svg{{width:100%;height:auto}}
svg text{{fill:var(--muted);font-size:11px}} .grid{{stroke:var(--line)}}
.legend span{{margin-right:14px;font-size:13px}} .legend i{{display:inline-block;width:10px;height:10px;margin-right:5px;border-radius:2px}}
pre{{white-space:pre-wrap;font-size:12px;border-top:1px solid var(--line);padding-top:12px}}
</style>
<h1>League dashboard</h1>
<p class="muted">{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(summary['time']))} · champion <code>{html.escape(summary['champion'])}</code> · panel v{summary['panel_version']}</p>
<table><tr><th>#</th><th>version</th><th>rating</th></tr>{rows}</table>
{gems}{runs}
<pre>{html.escape(report_md)}</pre>
"""
    path.write_text(page, encoding="utf-8")
