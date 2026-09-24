import json

from groq import Groq
from composio import Composio

from config import GROQ_API_KEY, COMPOSIO_API_KEY
from models import AppResearch


groq = Groq(api_key=GROQ_API_KEY)
composio = Composio(api_key=COMPOSIO_API_KEY)


# ---------------------------------------------------------
# 1. Fetch official Salesforce evidence
# ---------------------------------------------------------

session = composio.sessions.create(
    user_id="research-agent",
    toolkits=["composio_search"]
)

url = (
    "https://developer.salesforce.com/docs/"
    "atlas.en-us.api_rest.meta/api_rest/sforce_rest_api.htm"
)

print("Fetching Salesforce evidence...")

fetch_result = session.execute(
    "COMPOSIO_SEARCH_FETCH_URL_CONTENT",
    arguments={
        "url": url
    }
)

print("Evidence fetched successfully.")


# ---------------------------------------------------------
# 2. Extract the fetched text
# ---------------------------------------------------------

result_data = fetch_result.data

results = result_data.get("results", [])

if not results:
    raise RuntimeError("No content was returned from the URL.")

page = results[0]

page_text = page.get("text", "")
page_title = page.get("title", "")
page_url = page.get("url", url)

if not page_text:
    raise RuntimeError("The fetched page contains no text.")


print("Page title:", page_title)
print("Evidence characters:", len(page_text))


# ---------------------------------------------------------
# 3. Ask Groq to analyze the evidence
# ---------------------------------------------------------

schema = AppResearch.model_json_schema()

prompt = f"""
You are an evidence-based application research analyst.

Research the application: Salesforce.

You MUST use only the supplied evidence below.

Do NOT rely on your prior knowledge.
Do NOT invent facts.
If the evidence does not support a field, use:
- an empty list for list fields
- "UNKNOWN" for categorical fields
- null for optional fields
- a low confidence score

The evidence URL is:
{page_url}

Evidence title:
{page_title}

Evidence:
{page_text[:12000]}

Return a structured research record for Salesforce.

Important:
- description must be a concise one-line description.
- auth_methods should contain only authentication methods supported by the evidence.
- credential_access should be SELF_SERVE, GATED, or UNKNOWN.
- api_types should contain only API types explicitly supported by evidence.
- api_breadth should be Broad, Moderate, Narrow, or UNKNOWN.
- mcp_status should be AVAILABLE, NOT_FOUND, or UNKNOWN.
- buildability should be POSSIBLE, BLOCKED, or UNKNOWN.
- main_blocker should be null unless the evidence identifies a blocker.
- Every important claim must have an evidence entry.
- confidence must be between 0 and 1.
- verified must be false because this is the initial research pass.

Use this JSON schema:

{json.dumps(schema, indent=2)}
"""


print("\nSending evidence to Groq...")

response = groq.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a careful research analyst. "
                "Never invent information that is not supported "
                "by the supplied evidence."
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


# ---------------------------------------------------------
# 4. Validate Groq's result with Pydantic
# ---------------------------------------------------------

raw_output = response.choices[0].message.content

research_data = json.loads(raw_output)

research = AppResearch.model_validate(research_data)


# ---------------------------------------------------------
# 5. Save result
# ---------------------------------------------------------

output_path = "reports/salesforce_research.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        research.model_dump(),
        f,
        indent=2,
        ensure_ascii=False,
    )


print("\n====================================")
print("Salesforce research completed.")
print("====================================")
print(json.dumps(research.model_dump(), indent=2))
print(f"\nSaved to: {output_path}")