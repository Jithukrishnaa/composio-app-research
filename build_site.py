import json
import glob
import html
from pathlib import Path
from collections import Counter
from statistics import mean


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
WEB = ROOT / "web"

WEB.mkdir(exist_ok=True)


# ============================================================
# LOAD RESEARCH
# ============================================================

files = glob.glob(
    str(REPORTS / "*_research.json")
)

records = []

for file in files:
    try:
        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:
            records.append(json.load(f))
    except Exception as e:
        print(
            f"Could not read {file}: {e}"
        )


# Sort by ID
records.sort(
    key=lambda x: x.get("id", 9999)
)


total_researched = len(records)

avg_confidence = (
    mean(
        float(x.get("confidence", 0))
        for x in records
    )
    if records
    else 0
)


credential_counts = Counter(
    x.get(
        "credential_access",
        "UNKNOWN"
    )
    for x in records
)


mcp_counts = Counter(
    x.get(
        "mcp_status",
        "UNKNOWN"
    )
    for x in records
)


build_counts = Counter(
    x.get(
        "buildability",
        "UNKNOWN"
    )
    for x in records
)


api_counts = Counter(
    api
    for x in records
    for api in x.get(
        "api_types",
        []
    )
)


# ============================================================
# HELPERS
# ============================================================

def esc(value):
    return html.escape(
        str(value)
    )


def list_text(values):
    if not values:
        return "—"

    return ", ".join(
        esc(v)
        for v in values
    )


def pct(value, total):
    if not total:
        return 0

    return round(
        value / total * 100
    )


# ============================================================
# TABLE ROWS
# ============================================================

rows = []

for r in records:

    evidence_links = []

    for ev in r.get(
        "evidence",
        []
    ):

        url = ev.get(
            "url"
        )

        if url:

            evidence_links.append(
                f'<a href="{esc(url)}" '
                f'target="_blank" '
                f'rel="noopener">'
                f'View</a>'
            )

    evidence_html = (
        "<br>".join(
            evidence_links[:4]
        )
        if evidence_links
        else "—"
    )

    rows.append(
        f"""
        <tr>
            <td>{esc(r.get("id", ""))}</td>

            <td>
                <strong>
                    {esc(r.get("app", "Unknown"))}
                </strong>
            </td>

            <td>
                {esc(r.get("category", "UNKNOWN"))}
            </td>

            <td>
                {list_text(
                    r.get("api_types", [])
                )}
            </td>

            <td>
                {list_text(
                    r.get("auth_methods", [])
                )}
            </td>

            <td>
                {esc(
                    r.get(
                        "credential_access",
                        "UNKNOWN"
                    )
                )}
            </td>

            <td>
                {esc(
                    r.get(
                        "mcp_status",
                        "UNKNOWN"
                    )
                )}
            </td>

            <td>
                {esc(
                    r.get(
                        "buildability",
                        "UNKNOWN"
                    )
                )}
            </td>

            <td>
                {float(
                    r.get(
                        "confidence",
                        0
                    )
                ):.2f}
            </td>

            <td>
                {evidence_html}
            </td>
        </tr>
        """
    )


table_html = "\n".join(rows)


# ============================================================
# API BREAKDOWN
# ============================================================

api_items = []

for api, count in api_counts.most_common():

    api_items.append(
        f"""
        <div class="bar-row">
            <div class="bar-label">
                <span>{esc(api)}</span>
                <strong>{count}</strong>
            </div>

            <div class="bar">
                <div
                    class="bar-fill"
                    style="width:{pct(count, total_researched)}%"
                ></div>
            </div>
        </div>
        """
    )


api_html = "\n".join(
    api_items
)


# ============================================================
# HTML
# ============================================================

page = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Composio AI App Research
</title>


<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background: #f6f7fb;

    color: #172033;

    line-height: 1.5;
}}

.container {{
    width: min(
        1400px,
        94%
    );

    margin: auto;
}}

.hero {{
    background:
        linear-gradient(
            135deg,
            #111827,
            #26344d
        );

    color: white;

    padding: 70px 0;

    margin-bottom: 35px;
}}

.hero h1 {{
    font-size: clamp(
        38px,
        6vw,
        70px
    );

    line-height: 1.05;

    margin: 0 0 20px;
}}

.hero p {{
    max-width: 800px;

    font-size: 19px;

    color: #dbe4f0;
}}

.badge {{
    display: inline-block;

    padding: 7px 13px;

    border-radius: 999px;

    background: rgba(
        255,
        255,
        255,
        0.12
    );

    margin-bottom: 20px;

    font-size: 13px;

    font-weight: 700;

    letter-spacing: .05em;

    text-transform: uppercase;
}}

section {{
    margin: 45px 0;
}}

h2 {{
    font-size: 30px;

    margin-bottom: 10px;
}}

.subtitle {{
    color: #657085;

    max-width: 800px;
}}

.cards {{
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                180px,
                1fr
            )
        );

    gap: 16px;

    margin-top: 25px;
}}

.card {{
    background: white;

    border: 1px solid #e5e8ef;

    border-radius: 16px;

    padding: 23px;

    box-shadow:
        0 5px 20px
        rgba(
            20,
            30,
            50,
            .05
        );
}}

.metric {{
    font-size: 35px;

    font-weight: 800;
}}

.label {{
    color: #6b7280;

    font-size: 14px;
}}

.workflow {{
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                150px,
                1fr
            )
        );

    gap: 12px;

    margin-top: 25px;
}}

.step {{
    background: white;

    border:
        1px solid #e5e8ef;

    border-radius: 14px;

    padding: 20px;

    text-align: center;

    font-weight: 700;
}}

.step span {{
    display: block;

    font-size: 25px;

    margin-bottom: 8px;
}}

.insight {{
    background: white;

    border-left:
        5px solid #4f46e5;

    padding: 20px 25px;

    border-radius: 10px;

    margin-top: 15px;
}}

.bars {{
    background: white;

    border:
        1px solid #e5e8ef;

    padding: 25px;

    border-radius: 16px;

    margin-top: 25px;
}}

.bar-row {{
    margin: 17px 0;
}}

.bar-label {{
    display: flex;

    justify-content:
        space-between;

    margin-bottom: 6px;
}}

.bar {{
    height: 10px;

    background: #edf0f5;

    border-radius: 20px;

    overflow: hidden;
}}

.bar-fill {{
    height: 100%;

    background: #4f46e5;

    border-radius: 20px;
}}

.table-wrap {{
    overflow-x: auto;

    background: white;

    border-radius: 16px;

    border:
        1px solid #e5e8ef;

    margin-top: 25px;
}}

table {{
    width: 100%;

    border-collapse:
        collapse;

    min-width: 1200px;
}}

th {{
    background: #f1f3f7;

    text-align: left;

    padding: 14px;

    font-size: 13px;

    position: sticky;

    top: 0;
}}

td {{
    padding: 13px 14px;

    border-top:
        1px solid #edf0f4;

    font-size: 13px;

    vertical-align: top;
}}

a {{
    color: #4f46e5;

    text-decoration: none;

    font-weight: 600;
}}

footer {{
    background: #111827;

    color: #cbd5e1;

    padding: 35px 0;

    margin-top: 70px;
}}

small {{
    color: #7b8496;
}}

@media(max-width:700px) {{

    .hero {{
        padding: 45px 0;
    }}

    .hero h1 {{
        font-size: 40px;
    }}

}}

</style>

</head>


<body>


<header class="hero">

<div class="container">

<div class="badge">
AI Product Ops Intern Take-Home
</div>

<h1>
AI App Integration Research
</h1>

<p>
An evidence-first research pipeline for evaluating
application APIs, authentication, credential access,
MCP availability and integration buildability across
a 100-app target set.
</p>

</div>

</header>


<main class="container">


<section>

<h2>
Research Snapshot
</h2>

<p class="subtitle">
The automated research pass successfully produced
structured, evidence-backed records for
{total_researched} of the 100 target applications.
The remaining applications encountered pipeline-level
failures and were not fabricated or filled with guessed
information.
</p>


<div class="cards">

<div class="card">
<div class="metric">
{total_researched}
</div>
<div class="label">
Apps successfully researched
</div>
</div>


<div class="card">
<div class="metric">
{100 - total_researched}
</div>
<div class="label">
Apps without completed records
</div>
</div>


<div class="card">
<div class="metric">
{avg_confidence:.2f}
</div>
<div class="label">
Average confidence
</div>
</div>


<div class="card">
<div class="metric">
{credential_counts.get("SELF_SERVE", 0)}
</div>
<div class="label">
Self-serve credential access
</div>
</div>


<div class="card">
<div class="metric">
{credential_counts.get("GATED", 0)}
</div>
<div class="label">
Gated credential access
</div>
</div>


<div class="card">
<div class="metric">
{mcp_counts.get("AVAILABLE", 0)}
</div>
<div class="label">
MCP availability confirmed
</div>
</div>

</div>

</section>


<section>

<h2>
How the Research Agent Works
</h2>

<p class="subtitle">
The pipeline separates evidence collection from
structured extraction. Search results are fetched,
compressed into a bounded evidence context, and passed
to a structured-output model. Unsupported claims are
represented as UNKNOWN instead of being invented.
</p>


<div class="workflow">

<div class="step">
<span>01</span>
Load 100 Apps
</div>

<div class="step">
<span>02</span>
Composio Search
</div>

<div class="step">
<span>03</span>
Fetch Evidence
</div>

<div class="step">
<span>04</span>
Compact Evidence
</div>

<div class="step">
<span>05</span>
Groq Extraction
</div>

<div class="step">
<span>06</span>
Pydantic Validation
</div>

<div class="step">
<span>07</span>
JSON Reports
</div>

</div>

</section>


<section>

<h2>
What the Initial Pass Shows
</h2>


<div class="insight">

<strong>
Credential access is observable but incomplete.
</strong>

<p>
Among the {total_researched} completed records,
{credential_counts.get("SELF_SERVE", 0)} were classified as
SELF_SERVE, {credential_counts.get("GATED", 0)} as GATED,
and {credential_counts.get("UNKNOWN", 0)} remained UNKNOWN.
This indicates that credential-access evidence is not
uniformly exposed across applications.
</p>

</div>


<div class="insight">

<strong>
MCP evidence is currently the largest research gap.
</strong>

<p>
Only {mcp_counts.get("AVAILABLE", 0)} completed record was
classified as AVAILABLE for MCP, while
{mcp_counts.get("UNKNOWN", 0)} remained UNKNOWN.
The result should be treated as an evidence-coverage
signal, not as proof that those applications do not
support MCP.
</p>

</div>


<div class="insight">

<strong>
The agent is conservative about buildability.
</strong>

<p>
{build_counts.get("POSSIBLE", 0)} applications were classified
as POSSIBLE and {build_counts.get("UNKNOWN", 0)} remained
UNKNOWN. This is preferable to treating missing evidence
as evidence of a blocker.
</p>

</div>


</section>


<section>

<h2>
API Surface Observed
</h2>

<p class="subtitle">
Counts below represent API labels extracted from the
{total_researched} successfully researched applications.
They are not counts for the entire 100-app target.
</p>


<div class="bars">

{api_html}

</div>

</section>


<section>

<h2>
Application Research Records
</h2>

<p class="subtitle">
Each row is generated from a structured JSON research
record. Evidence links point to the sources retained
by the research pipeline.
</p>


<div class="table-wrap">

<table>

<thead>

<tr>

<th>ID</th>
<th>Application</th>
<th>Category</th>
<th>API Surface</th>
<th>Authentication</th>
<th>Credential Access</th>
<th>MCP</th>
<th>Buildability</th>
<th>Confidence</th>
<th>Evidence</th>

</tr>

</thead>


<tbody>

{table_html}

</tbody>

</table>

</div>

</section>


<section>

<h2>
Limitations & Verification
</h2>

<div class="insight">

<p>
<strong>
Important:
</strong>
This page reports the initial automated research pass.
The 57 completed records should not be treated as
ground truth. Some applications expose incomplete,
dynamic or gated documentation, and 43 target applications
did not produce completed records during this run.
</p>

<p>
The pipeline intentionally preserves UNKNOWN values and
does not invent missing facts. A production workflow should
add an independent verification pass and human spot checks
for high-impact claims, especially authentication,
credential access and MCP availability.
</p>

</div>

</section>


<section>

<h2>
Technical Stack
</h2>

<div class="cards">

<div class="card">
<strong>Python</strong>
<p class="label">
Research orchestration
</p>
</div>

<div class="card">
<strong>Composio</strong>
<p class="label">
Web search and evidence fetching
</p>
</div>

<div class="card">
<strong>Groq</strong>
<p class="label">
Structured research extraction
</p>
</div>

<div class="card">
<strong>Pydantic</strong>
<p class="label">
Schema validation
</p>
</div>

<div class="card">
<strong>JSON</strong>
<p class="label">
Evidence-backed research records
</p>
</div>

<div class="card">
<strong>HTML/CSS</strong>
<p class="label">
Final case-study deliverable
</p>
</div>

</div>

</section>


</main>


<footer>

<div class="container">

<strong>
Composio App Research Agent
</strong>

<br><br>

<small>
Evidence-first application research •
Initial automated pass •
57 successfully completed records
</small>

</div>

</footer>


</body>

</html>
"""


# ============================================================
# WRITE FILE
# ============================================================

output = WEB / "index.html"

with open(
    output,
    "w",
    encoding="utf-8"
) as f:

    f.write(page)


print()
print("=" * 60)
print("WEBSITE GENERATED")
print("=" * 60)
print()
print(
    f"Research records: {total_researched}"
)
print(
    f"Average confidence: {avg_confidence:.3f}"
)
print()
print(
    f"Saved to: {output}"
)
print()