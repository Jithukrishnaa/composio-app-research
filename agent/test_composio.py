from composio import Composio
from config import COMPOSIO_API_KEY

print("Checking Composio configuration...")

if not COMPOSIO_API_KEY:
    print("Composio API key NOT found.")
    raise SystemExit(1)

print("Composio API key loaded successfully.")

composio = Composio(api_key=COMPOSIO_API_KEY)

print("Connecting to Composio...")

toolkits = composio.toolkits.list(limit=5)

print("\nComposio connection successful.")
print("Sample toolkits:")

for toolkit in toolkits.items:
    print("-", toolkit.slug)