# Composio App Research Agent

An evidence-first AI research pipeline for analyzing application integrations across APIs, authentication, credential access, MCP availability, and integration buildability.

Built as part of the **AI Product Ops Intern take-home assignment**.

---

## Overview

Researching 100+ applications manually across API documentation, authentication requirements, credential access, MCP support, and integration feasibility is time-consuming and difficult to keep consistent.

This project automates the first-pass research workflow using:

* **Composio** for web search and evidence fetching
* **Groq** for structured evidence extraction
* **Pydantic** for output validation
* **Python** for orchestration
* **JSON** for structured research records
* **HTML/CSS** for the final case-study deliverable

The core principle is:

> **If the evidence does not support a claim, the system records `UNKNOWN` instead of guessing.**

---

## Research Pipeline

```text
100 Target Applications
          │
          ▼
   Research Agent
          │
          ▼
  Composio Web Search
          │
          ▼
  Official / Relevant
   Documentation
          │
          ▼
    Evidence Fetch
          │
          ▼
  Evidence Compression
          │
          ▼
   Groq Structured
      Extraction
          │
          ▼
  Pydantic Validation
          │
          ▼
 Individual JSON Reports
          │
          ▼
 Pattern Analysis
          │
          ▼
  HTML Case Study
```

---

## What Is Being Researched?

Each application is analyzed across the following dimensions:

| Field             | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| Application       | Application name                                            |
| Category          | Product category                                            |
| Website           | Official website                                            |
| Description       | One-line application description                            |
| Authentication    | Supported authentication methods found in evidence          |
| Credential Access | Self-serve, gated, or unknown                               |
| API Types         | APIs explicitly identified in evidence                      |
| API Breadth       | Broad, moderate, narrow, or unknown                         |
| MCP Status        | MCP availability based on evidence                          |
| Buildability      | Initial integration feasibility classification              |
| Main Blocker      | Known blocker when supported by evidence                    |
| Evidence          | Source URLs supporting claims                               |
| Confidence        | Research confidence score                                   |
| Verification      | Whether the record has passed a separate verification stage |

---

## Target Dataset

The target dataset contains **100 applications** across categories including:

* CRM & Sales
* Support & Helpdesk
* Communications & Messaging
* Marketing & Advertising
* Ecommerce
* Data, SEO & Scraping
* Developer Infrastructure
* Data Platforms
* Productivity & Project Management
* Finance & Fintech
* AI, Research & Media

The application list is stored in:

```text
data/apps.json
```

---

## Current Research Results

The automated research run attempted all **100 target applications**.

The completed first pass produced:

| Metric                           | Result |
| -------------------------------- | -----: |
| Target applications              |    100 |
| Completed research records       |     57 |
| Incomplete / failed applications |     43 |
| Average confidence               |  0.705 |
| SELF_SERVE credential access     |     30 |
| GATED credential access          |      8 |
| UNKNOWN credential access        |     19 |
| MCP AVAILABLE                    |      1 |
| MCP UNKNOWN                      |     56 |
| Buildability POSSIBLE            |     30 |
| Buildability UNKNOWN             |     27 |

### Important

These metrics describe the **57 successfully processed records**, not all 100 target applications.

The 43 unsuccessful applications were not filled with fabricated values. This is intentional.

---

## Key Findings From the Initial Pass

### Credential Access

Among the completed records:

* **30** were classified as `SELF_SERVE`
* **8** were classified as `GATED`
* **19** remained `UNKNOWN`

This suggests that credential-access requirements are not uniformly exposed through public documentation.

### MCP Evidence

Only **1** completed record was classified as:

```text
AVAILABLE
```

while **56** remained:

```text
UNKNOWN
```

This should not be interpreted as proof that those applications do not support MCP.

It indicates that MCP availability was not established from the evidence collected during this initial automated pass.

### Buildability

The initial pass classified:

* **30** as `POSSIBLE`
* **27** as `UNKNOWN`

The system intentionally avoids treating missing evidence as a blocker.

---

## Architecture

```text
                    apps.json
                       │
                       ▼
              ┌─────────────────┐
              │ Research Agent  │
              └────────┬────────┘
                       │
                       ▼
               Composio Search
                       │
                       ▼
                URL Discovery
                       │
                       ▼
                 URL Fetching
                       │
                       ▼
             Evidence Collection
                       │
                       ▼
              Evidence Reduction
                       │
                       ▼
                Groq LLM
                       │
                       ▼
             Structured JSON
                       │
                       ▼
             Pydantic Validation
                       │
                       ▼
               Research Reports
                       │
                       ▼
                HTML Generator
                       │
                       ▼
                Case Study Page
```

---

## Project Structure

```text
composio-app-research/
│
├── agent/
│   ├── config.py
│   ├── models.py
│   ├── research_agent.py
│   ├── analyze_evidence.py
│   ├── test_models.py
│   ├── test_config.py
│   ├── test_groq.py
│   ├── test_composio.py
│   ├── test_research_tools.py
│   └── test_fetch.py
│
├── data/
│   └── apps.json
│
├── reports/
│   ├── *_research.json
│   └── raw/
│       └── local evidence files
│
├── web/
│   └── index.html
│
├── build_site.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

> `reports/raw/` contains locally fetched raw evidence and is intentionally excluded from the public Git repository.

---

## Technology Stack

### Python

Research orchestration, file handling, data processing, and pipeline control.

### Composio

Used to search for and fetch web evidence.

### Groq

Used to transform collected evidence into structured application research.

Current model:

```text
openai/gpt-oss-120b
```

### Pydantic

Used to validate structured research records.

### JSON

Used for:

* Application configuration
* Research reports
* Evidence storage

### HTML/CSS

Used to generate the final self-contained research case study.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/jithukrishnaa/composio-app-research.git
cd composio-app-research
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Create a local `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
COMPOSIO_API_KEY=your_composio_api_key
```

The `.env` file is intentionally excluded from Git.

Use `.env.example` as the template.

**Never commit API keys to the repository.**

---

## Run the Research Agent

Set the maximum number of applications:

```powershell
$env:MAX_APPS="100"
```

Run:

```powershell
python agent\research_agent.py
```

The agent checks the existing `reports/` directory and skips applications that already have completed research records.

This allows interrupted runs to continue without unnecessarily repeating successful research.

---

## Research Output

Structured research records are saved under:

```text
reports/
```

Example:

```text
reports/
├── salesforce_research.json
├── hubspot_research.json
├── github_research.json
└── ...
```

Each record follows the Pydantic research schema.

---

## Generate the Case Study

After research records have been generated:

```powershell
python build_site.py
```

The script creates:

```text
web/index.html
```

Open locally:

```powershell
start web\index.html
```

The generated page includes:

* Research methodology
* Agent workflow
* Dataset statistics
* Credential-access analysis
* MCP analysis
* Buildability analysis
* API surface analysis
* Application-level records
* Evidence links
* Confidence scores
* Limitations
* Technology stack

---

## Evidence Strategy

The research pipeline prioritizes:

1. Official developer documentation
2. Official API documentation
3. Official authentication documentation
4. Official credential/access documentation
5. Official MCP documentation
6. Official GitHub repositories
7. Other relevant sources when necessary

Search is primarily used for discovery.

Fetched source content is then supplied to the structured extraction stage.

---

## Accuracy Strategy

The system separates:

```text
Evidence Collection
        ↓
Structured Extraction
        ↓
Validation
        ↓
Verification
```

The current implementation represents an **initial automated research pass**.

A production implementation should add an independent verification stage.

Recommended verification workflow:

```text
Initial Research
       ↓
Independent Evidence Search
       ↓
Claim Comparison
       ↓
Human Spot Check
       ↓
Final Record
```

Fields requiring particular attention during verification:

* Authentication
* Credential access
* MCP availability
* API breadth
* Buildability

---

## Handling Uncertainty

The pipeline intentionally distinguishes between:

```text
Evidence confirms a claim
        ↓
Return the supported value
```

and:

```text
Evidence does not establish the claim
        ↓
Return UNKNOWN
```

For example:

```text
MCP documentation found
        ↓
MCP = AVAILABLE
```

but:

```text
No reliable MCP evidence found
        ↓
MCP = UNKNOWN
```

rather than:

```text
MCP = NOT_AVAILABLE
```

This reduces unsupported conclusions.

---

## Failure Handling

Individual application failures do not terminate the complete research run.

```text
Application
     │
     ├── Research succeeds
     │       ↓
     │    Save JSON
     │
     └── Research fails
             ↓
        Record failure
             ↓
        Continue next app
```

This makes the pipeline resilient to:

* Search failures
* Fetch failures
* Rate limits
* Invalid pages
* Gated documentation
* Model/API errors

---

## Why Raw Evidence Is Not Public

Raw fetched pages are stored locally under:

```text
reports/raw/
```

but excluded from Git using:

```gitignore
reports/raw/
```

The raw evidence can contain arbitrary page content, including strings that resemble credentials or API tokens.

The public repository therefore contains the **structured research records and evidence URLs**, rather than all raw fetched page content.

---

## Limitations

The current implementation has several limitations:

1. Only 57 of the 100 target applications completed successfully during the available automated run.
2. MCP status is under-researched for many applications.
3. The initial automated results have not undergone independent human verification for every claim.
4. Some documentation may be gated or dynamically generated.
5. API terminology differs between vendors.
6. Search results can change over time.
7. Buildability is an initial research classification, not a guarantee of implementation effort.

These limitations are intentionally disclosed rather than hidden.

---

## Future Improvements

Potential production improvements include:

* Independent verification agent
* Human review queue
* Automatic retries
* Better domain-specific search strategies
* Dedicated MCP verification
* Evidence freshness tracking
* Claim-level confidence
* Duplicate evidence detection
* Parallel research workers
* Persistent database storage
* Research history/versioning
* Accuracy measurement before and after verification
* Automatic regression testing

---

## Deliverables

### Research Agent

```text
agent/research_agent.py
```

### Application Dataset

```text
data/apps.json
```

### Structured Research

```text
reports/*_research.json
```

### Case Study

```text
web/index.html
```

### Generator

```text
build_site.py
```

### Documentation

```text
README.md
```

---

## Final Takeaway

This project demonstrates an evidence-first approach to agentic product research.

The goal is not simply to generate a large table of application metadata.

The important design principle is:

> **Automate discovery and extraction, preserve evidence, validate structure, expose uncertainty, and verify important claims before treating them as reliable.**
