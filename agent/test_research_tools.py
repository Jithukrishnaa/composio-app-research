from composio import Composio
from config import COMPOSIO_API_KEY


print("Starting Salesforce research...")

composio = Composio(api_key=COMPOSIO_API_KEY)

session = composio.sessions.create(
    user_id="research-agent",
    toolkits=["composio_search"]
)

print("Research session created.")
print("Session ID:", session.session_id)

print("\nSearching for Salesforce official documentation...")

search_result = session.execute(
    "COMPOSIO_SEARCH_WEB",
    arguments={
        "query": "Salesforce REST API authentication OAuth 2.0 official developer documentation site:developer.salesforce.com",
        "start": 0
    }
)
print("\nSearch completed.")
print(search_result)