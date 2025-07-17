---
trigger: always_on
---


## Architecture Design Rules
- Design for scalability and observability in all system designs.
- The system must utilize cloud native observability, logging, and metrics to monitor performance, activity, and problems. When possible, consider Grafana Observability for Metrics, Logs, Traces, Profiles and Synthetic Transactions.
- Implement proper retry and circuit breaker patterns for external integrations.
- Design for eventual consistency where appropriate.
- Maintain clear API contracts between agents.
- Consider using MCP for the Agents to interact with data sources, prefer alternative connectors when you determine there is a better alternative that meets the rules.


## Security Rules

- Never expose API keys or credentials directly in code unless explicitly requested by the user.
- In production, Use a Key Vault for all sensitive configuration and credentials.
- Implement proper authentication and authorization for all system components.
- Follow the principle of least privilege for all service accounts and permissions.
- All  Blob Storage such as S3 bucketes, must have encryption enabled and block public access unless specifically required.
- All database services must have encryption enabled.
- All messaging services must enforce SSL/TLS encryption.
- All Web services must enforce SSL/TLS encryption.

## Integration Rules

- When integrating with external systems (GitHub, JIRA, Confluence, ServiceNow, CareFabric, FHIR, AWS, Azure, Databases, Managed Services), provide clear interface specifications.
- Use serverless for workflow orchestration where appropriate.
- Implement proper error handling and logging for all external API calls.
- Design integrations to be resilient to temporary service outages.
- Document all external dependencies and their authentication requirements in security.md.