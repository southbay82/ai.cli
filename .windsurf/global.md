---
trigger: always_on
---

# Global Rules

## Documentation Management Rules
- projectSummary.md - Complete project overview, with component level explanations, internal and external dependencies documented.
- taskPlan.md - Update as we learn or need to adjust the work pending or completed. This is important to allow you to resume work sessions and track progress.
- README.md - Update as appropriate to inform the reader about the project. Provide hyperlinks to documentation in the README.md.
- dataFlow.md - Update to show the data flow of user requests, different agents, and external system interactions. Utilize mermaid diagrams in the documentation.
- security.md - Update to explain security mechanisms in the system, including necessary authentication details to interact with the system and what credentials it requires to interact with external systems.
- memory-bank/contextSummary.md - Update your current context summary when promptd by the user. This supports resuming work when context windows and conversations become too lengthy.

## Tool Usage Rules
- When the user mentions "remember", use the cascade memories feature.
- - IMPORTANT - all memories should be prefixed with "the project home directory name" and always referenced using the same term.
- Use context7 MCP for technical documentation and library information.
- Use aws MCP to read and interact with AWS cloud resources.
- Use aws cli to read and interact with AWS cloud resources.
- Use azure MCP to read and interact with Azure cloud resources.
- Use azd CLI tool for Azure Developer CLI operations.
- Use azure cli tool for general Azure CLI operations.
- Use Atlassian MCP for JIRA access and issue management.
- Use Git utilities for code diffing, review, and bridging gaps not fulfilled by Bitbucket MCP and CLI tools.
- Use Cascade's web fetch feature for accessing web content.



