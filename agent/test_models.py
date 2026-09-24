from models import AppResearch, Evidence


research = AppResearch(
    id=1,
    app="Salesforce",
    category="CRM and Sales",
    website="https://salesforce.com/",
    description="Customer relationship management platform.",
    auth_methods=["OAuth 2.0"],
    credential_access="SELF_SERVE",
    api_types=["REST"],
    api_breadth="Broad",
    mcp_status="UNKNOWN",
    buildability="POSSIBLE",
    main_blocker=None,
    evidence=[
        Evidence(
            claim="Authentication",
            url="https://developer.salesforce.com/",
            source_type="official documentation"
        )
    ],
    confidence=0.8
)


print(research.model_dump_json(indent=2))