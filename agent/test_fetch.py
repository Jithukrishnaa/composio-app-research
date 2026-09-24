from composio import Composio
from config import COMPOSIO_API_KEY


print("Starting Salesforce evidence fetch...")

composio = Composio(api_key=COMPOSIO_API_KEY)

session = composio.sessions.create(
    user_id="research-agent",
    toolkits=["composio_search"]
)

print("Research session created.")

# Official Salesforce REST API documentation
url = "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/sforce_rest_api.htm"

print("\nFetching:")
print(url)

result = session.execute(
    "COMPOSIO_SEARCH_FETCH_URL_CONTENT",
    arguments={
        "url": url
    }
)

print("\nFetch completed.")
print(result)