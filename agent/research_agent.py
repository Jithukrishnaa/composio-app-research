import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from composio import Composio
from groq import Groq

from config import COMPOSIO_API_KEY, GROQ_API_KEY
from models import AppResearch


# ============================================================
# CONFIGURATION
# ============================================================

MODEL = "openai/gpt-oss-120b"

# Maximum number of NEW apps to research in this run.
# We will skip apps that already have a research JSON file.
#
# For your current run, 100 is correct.
MAX_APPS = int(os.getenv("MAX_APPS", "100"))

USER_ID = "research-agent"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

APPS_FILE = PROJECT_ROOT / "data" / "apps.json"

REPORTS_DIR = PROJECT_ROOT / "reports"

RAW_DIR = REPORTS_DIR / "raw"

REPORTS_DIR.mkdir(
    exist_ok=True
)

RAW_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# API CLIENTS
# ============================================================

if not COMPOSIO_API_KEY:

    raise RuntimeError(
        "COMPOSIO_API_KEY is missing from your .env file."
    )


if not GROQ_API_KEY:

    raise RuntimeError(
        "GROQ_API_KEY is missing from your .env file."
    )


print("Initializing Groq...")

groq = Groq(
    api_key=GROQ_API_KEY
)


print("Initializing Composio...")

composio = Composio(
    api_key=COMPOSIO_API_KEY
)


print("Creating Composio research session...")

session = composio.sessions.create(
    user_id=USER_ID,
    toolkits=["composio_search"]
)


print("Research session ready.")


# ============================================================
# LOAD APPS
# ============================================================

def load_apps() -> list[dict[str, Any]]:
    """
    Load applications from data/apps.json.
    """

    if not APPS_FILE.exists():

        raise FileNotFoundError(
            f"Could not find apps file: {APPS_FILE}"
        )


    with open(
        APPS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        apps = json.load(f)


    if not isinstance(apps, list):

        raise ValueError(
            "data/apps.json must contain a JSON list."
        )


    print(
        f"Loaded {len(apps)} apps from apps.json."
    )


    return apps


# ============================================================
# SAFE FILENAME
# ============================================================

def safe_filename(
    name: str
) -> str:

    filename = name.lower()


    replacements = {
        " ": "_",
        ".": "",
        "/": "_",
        "\\": "_",
        "-": "_",
        ":": "_",
        "(": "",
        ")": "",
    }


    for old, new in replacements.items():

        filename = filename.replace(
            old,
            new
        )


    return filename


# ============================================================
# DOMAIN HELPER
# ============================================================

def get_domain(
    website: str
) -> str:

    if not website:

        return ""


    try:

        parsed = urlparse(
            website
        )

        domain = parsed.netloc


        if domain.startswith("www."):

            domain = domain[4:]


        return domain


    except Exception:

        return ""


# ============================================================
# EXTRACT URLS
# ============================================================

def extract_urls(
    obj: Any
) -> list[str]:

    urls = []


    if isinstance(obj, dict):

        for key, value in obj.items():

            if key.lower() in {
                "url",
                "link",
                "source_url",
                "href",
            }:

                if isinstance(
                    value,
                    str
                ):

                    if (
                        value.startswith("http://")
                        or value.startswith("https://")
                    ):

                        urls.append(
                            value
                        )


            urls.extend(
                extract_urls(value)
            )


    elif isinstance(obj, list):

        for item in obj:

            urls.extend(
                extract_urls(item)
            )


    elif isinstance(obj, str):

        for word in obj.split():

            word = word.strip(
                "()[]{}<>\"',"
            )


            if (
                word.startswith("http://")
                or word.startswith("https://")
            ):

                urls.append(
                    word
                )


    return urls


# ============================================================
# UNIQUE URLS
# ============================================================

def unique_urls(
    urls: list[str]
) -> list[str]:

    seen = set()

    result = []


    for url in urls:

        clean_url = url.strip()

        clean_url = clean_url.rstrip(
            ".,);]"
        )


        if not clean_url:

            continue


        if clean_url not in seen:

            seen.add(
                clean_url
            )

            result.append(
                clean_url
            )


    return result


# ============================================================
# COMPOSIO WEB SEARCH
# ============================================================

def search_web(
    query: str
) -> Any:

    print(
        f"    Searching: {query}"
    )


    result = session.execute(
        "COMPOSIO_SEARCH_WEB",
        arguments={
            "query": query,
            "start": 0,
        },
    )


    return result


# ============================================================
# COLLECT SEARCH URLS
# ============================================================

def collect_search_urls(
    app_name: str,
    website: str
) -> list[str]:

    domain = get_domain(
        website
    )


    queries = []


    # --------------------------------------------------------
    # API / AUTHENTICATION / CREDENTIALS
    # --------------------------------------------------------

    if domain:

        queries.append(
            f"{app_name} official API authentication "
            f"developer documentation site:{domain}"
        )

    else:

        queries.append(
            f"{app_name} official API authentication "
            f"developer documentation"
        )


    # --------------------------------------------------------
    # MCP
    # --------------------------------------------------------

    queries.append(
        f"{app_name} official MCP "
        f"Model Context Protocol"
    )


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    all_urls = []


    for query in queries:

        try:

            result = search_web(
                query
            )


            if result and result.data:

                urls = extract_urls(
                    result.data
                )


                all_urls.extend(
                    urls
                )


        except Exception as e:

            print(
                f"    Search failed: {e}"
            )


    # --------------------------------------------------------
    # FILTER NON-DOCUMENTATION ASSETS
    # --------------------------------------------------------

    filtered_urls = []


    for url in unique_urls(
        all_urls
    ):

        lower_url = url.lower()


        if any(
            unwanted in lower_url
            for unwanted in [
                ".ico",
                ".svg",
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".css",
                ".js",
            ]
        ):

            continue


        filtered_urls.append(
            url
        )


    return filtered_urls


# ============================================================
# FETCH URL
# ============================================================

def fetch_url(
    url: str
) -> dict[str, Any] | None:

    try:

        result = session.execute(
            "COMPOSIO_SEARCH_FETCH_URL_CONTENT",
            arguments={
                "url": url
            }
        )


        if not result:

            return None


        if not result.data:

            return None


        results = result.data.get(
            "results",
            []
        )


        if not results:

            return None


        page = results[0]


        text = page.get(
            "text",
            ""
        )


        if not text:

            return None


        return {
            "title": page.get(
                "title",
                ""
            ),
            "url": page.get(
                "url",
                url
            ),
            "text": text,
        }


    except Exception as e:

        print(
            f"    Fetch failed: {url}"
        )

        print(
            f"    Reason: {e}"
        )

        return None


# ============================================================
# COLLECT EVIDENCE
# ============================================================

def collect_evidence(
    app_name: str,
    website: str
) -> list[dict[str, Any]]:

    print(
        "  Collecting evidence..."
    )


    urls = collect_search_urls(
        app_name,
        website
    )


    print(
        f"  Candidate URLs found: "
        f"{len(urls)}"
    )


    # Keep this small to reduce API usage.
    urls = urls[:3]


    evidence_pages = []


    for url in urls:

        print(
            f"    Fetching: {url}"
        )


        page = fetch_url(
            url
        )


        if page:

            evidence_pages.append(
                page
            )


        time.sleep(
            0.3
        )


    return evidence_pages


# ============================================================
# BUILD COMPACT EVIDENCE
# ============================================================

def build_evidence_text(
    evidence_pages: list[dict[str, Any]]
) -> str:

    if not evidence_pages:

        return (
            "NO EVIDENCE WAS SUCCESSFULLY FETCHED."
        )


    parts = []


    # Maximum sources sent to Groq.
    max_sources = 3


    # Maximum characters per source.
    max_chars_per_source = 2000


    selected_pages = evidence_pages[
        :max_sources
    ]


    for index, page in enumerate(
        selected_pages,
        start=1
    ):

        title = page.get(
            "title",
            ""
        )


        url = page.get(
            "url",
            ""
        )


        text = page.get(
            "text",
            ""
        )


        text = text[
            :max_chars_per_source
        ]


        parts.append(
            f"""
--- EVIDENCE {index} ---

TITLE:
{title}

URL:
{url}

CONTENT:
{text}
"""
        )


    return "\n".join(
        parts
    )


# ============================================================
# ANALYZE WITH GROQ
# ============================================================

def analyze_with_groq(
    app: dict[str, Any],
    evidence_pages: list[dict[str, Any]]
) -> AppResearch:

    app_id = app.get(
        "id"
    )


    app_name = app.get(
        "name",
        "Unknown"
    )


    category = app.get(
        "category",
        "UNKNOWN"
    )


    website = app.get(
        "website",
        "UNKNOWN"
    )


    print(
        "  Sending evidence to Groq..."
    )


    evidence_text = build_evidence_text(
        evidence_pages
    )


    schema = AppResearch.model_json_schema()


    prompt = f"""
You are an evidence-based application research analyst.

Research this application:

ID: {app_id}
NAME: {app_name}
CATEGORY: {category}
WEBSITE: {website}

Use ONLY the supplied evidence.

Do NOT use prior knowledge.
Do NOT invent facts.
Do NOT guess.

If evidence does not support a field, use UNKNOWN
or an empty list.

FIELD RULES:

description:
Write one concise sentence based only on evidence.

auth_methods:
Only authentication methods explicitly supported
by evidence.

credential_access:
Use exactly:
SELF_SERVE
GATED
UNKNOWN

api_types:
Only API types explicitly supported by evidence.

api_breadth:
Use exactly:
Broad
Moderate
Narrow
UNKNOWN

mcp_status:
Use exactly:
AVAILABLE
NOT_FOUND
UNKNOWN

Only use AVAILABLE when the evidence explicitly
supports MCP availability.

buildability:
Use exactly:
POSSIBLE
BLOCKED
UNKNOWN

main_blocker:
Use null unless evidence identifies a concrete blocker.

evidence:
Every important factual claim should have an evidence entry.

Each evidence entry requires:
claim
url
source_type
notes

URLs MUST come from the supplied evidence.

confidence:
Return a number between 0 and 1.
Be conservative.

verified:
false

verification_notes:
null

IMPORTANT:

Return these identity fields exactly:

id = {app_id}
app = {json.dumps(app_name)}
category = {json.dumps(category)}
website = {json.dumps(website)}

SUPPLIED EVIDENCE:

{evidence_text}

Return ONLY the JSON object.
Do not include markdown.
Do not include explanations.
"""


    response = groq.chat.completions.create(
        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful evidence-based "
                    "research analyst. "
                    "Never invent facts. "
                    "Use UNKNOWN when evidence is insufficient."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],

        response_format={
            "type": "json_schema",

            "json_schema": {
                "name": "app_research",

                "strict": False,

                "schema": schema,
            },
        },
    )


    raw_output = (
        response
        .choices[0]
        .message
        .content
    )


    if not raw_output:

        raise RuntimeError(
            "Groq returned an empty response."
        )


    research_data = json.loads(
        raw_output
    )


    research = AppResearch.model_validate(
        research_data
    )


    # --------------------------------------------------------
    # FORCE ORIGINAL IDENTITY
    # --------------------------------------------------------

    research.id = app_id

    research.app = app_name

    research.category = category

    research.website = website

    research.verified = False


    return research


# ============================================================
# SAVE RESEARCH
# ============================================================

def save_research(
    research: AppResearch,
    evidence_pages: list[dict[str, Any]]
) -> None:

    filename = safe_filename(
        research.app
    )


    research_file = (
        REPORTS_DIR
        / f"{filename}_research.json"
    )


    evidence_file = (
        RAW_DIR
        / f"{filename}_evidence.json"
    )


    # --------------------------------------------------------
    # Save structured research
    # --------------------------------------------------------

    with open(
        research_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            research.model_dump(),
            f,
            indent=2,
            ensure_ascii=False,
        )


    # --------------------------------------------------------
    # Save raw evidence
    # --------------------------------------------------------

    with open(
        evidence_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            evidence_pages,
            f,
            indent=2,
            ensure_ascii=False,
        )


    print(
        f"  Saved: {research_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("COMPOSIO APP RESEARCH AGENT")
    print("=" * 60)
    print()


    # --------------------------------------------------------
    # LOAD APPS
    # --------------------------------------------------------

    apps = load_apps()


    # --------------------------------------------------------
    # VALIDATE APPS
    # --------------------------------------------------------

    print(
        "Validating application list..."
    )


    for app in apps:

        required_fields = [
            "id",
            "name",
            "category",
            "website",
        ]


        for field in required_fields:

            if field not in app:

                raise ValueError(
                    f"Missing '{field}': {app}"
                )


    print(
        "Application list validation successful."
    )


    # --------------------------------------------------------
    # FIND ALREADY COMPLETED APPS
    # --------------------------------------------------------

    completed_apps = set()


    for report_file in REPORTS_DIR.glob(
        "*_research.json"
    ):

        filename = report_file.stem


        if filename.endswith(
            "_research"
        ):

            app_filename = filename[
                :-len("_research")
            ]


            completed_apps.add(
                app_filename.lower()
            )


    # --------------------------------------------------------
    # FIND REMAINING APPS
    # --------------------------------------------------------

    remaining_apps = []


    for app in apps:

        app_name = app.get(
            "name",
            "Unknown"
        )


        filename = safe_filename(
            app_name
        ).lower()


        if filename not in completed_apps:

            remaining_apps.append(
                app
            )


    # --------------------------------------------------------
    # SELECT ONLY REMAINING APPS
    # --------------------------------------------------------

    selected_apps = remaining_apps[
        :min(
            MAX_APPS,
            len(remaining_apps)
        )
    ]


    print()

    print(
        f"Total apps available: "
        f"{len(apps)}"
    )


    print(
        f"Already completed: "
        f"{len(completed_apps)}"
    )


    print(
        f"Remaining apps: "
        f"{len(remaining_apps)}"
    )


    print(
        f"Apps selected for this run: "
        f"{len(selected_apps)}"
    )


    print()


    # --------------------------------------------------------
    # NOTHING LEFT
    # --------------------------------------------------------

    if not selected_apps:

        print(
            "No new apps need to be researched."
        )

        return


    successful = 0

    failed = 0


    # --------------------------------------------------------
    # PROCESS APPS
    # --------------------------------------------------------

    for position, app in enumerate(
        selected_apps,
        start=1
    ):

        app_id = app.get(
            "id"
        )


        app_name = app.get(
            "name",
            "Unknown"
        )


        category = app.get(
            "category",
            "UNKNOWN"
        )


        website = app.get(
            "website",
            ""
        )


        print()
        print("=" * 60)


        print(
            f"APP {position}/{len(selected_apps)}: "
            f"{app_name}"
        )


        print(
            f"ID: {app_id}"
        )


        print(
            f"Category: {category}"
        )


        print(
            f"Website: {website}"
        )


        print("=" * 60)


        try:

            # ------------------------------------------------
            # SEARCH + FETCH
            # ------------------------------------------------

            evidence_pages = collect_evidence(
                app_name,
                website
            )


            print(
                f"  Evidence pages fetched: "
                f"{len(evidence_pages)}"
            )


            # ------------------------------------------------
            # GROQ ANALYSIS
            # ------------------------------------------------

            research = analyze_with_groq(
                app,
                evidence_pages
            )


            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            save_research(
                research,
                evidence_pages
            )


            successful += 1


            # ------------------------------------------------
            # SUMMARY
            # ------------------------------------------------

            print()
            print("  RESULT")


            print(
                f"  App: "
                f"{research.app}"
            )


            print(
                f"  API: "
                f"{research.api_types}"
            )


            print(
                f"  Auth: "
                f"{research.auth_methods}"
            )


            print(
                f"  Credential: "
                f"{research.credential_access}"
            )


            print(
                f"  MCP: "
                f"{research.mcp_status}"
            )


            print(
                f"  Buildability: "
                f"{research.buildability}"
            )


            print(
                f"  Confidence: "
                f"{research.confidence}"
            )


        except Exception as e:

            failed += 1


            print()
            print(
                f"  ERROR: {app_name}"
            )


            print(
                f"  {e}"
            )


            # Continue to next app.
            continue


        # ----------------------------------------------------
        # SMALL DELAY
        # ----------------------------------------------------

        time.sleep(
            0.5
        )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("RESEARCH RUN COMPLETE")
    print("=" * 60)


    print(
        f"Successful: {successful}"
    )


    print(
        f"Failed:     {failed}"
    )


    print(
        f"Processed this run: "
        f"{successful + failed}"
    )


    print()


    # Recount reports after this run.
    final_report_count = len(
        list(
            REPORTS_DIR.glob(
                "*_research.json"
            )
        )
    )


    print(
        f"Total research reports now: "
        f"{final_report_count}"
    )


    print()


    print(
        f"Reports: {REPORTS_DIR}"
    )


    print(
        f"Raw evidence: {RAW_DIR}"
    )


    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()