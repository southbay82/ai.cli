---
trigger: always_on
---

### General Guidelines
- Prefer simple, concise solutions
- Suggest terminal commands or file edits when applicable
- Check for existing similar code before adding new functionality
- Consider dev, test, and prod environments
- Make minimal, targeted changes
- Exhaust existing implementation options before introducing new patterns
- Keep codebase clean and organized
- Avoid scripts in files for one-time use
- Never add stubbing/fake data to dev/prod environments
- Never overwrite .env without confirmation
- Store secrets in .env.secrets
- Limit logs/tail commands to 100 lines
- Maintain a decision log for major architectural decisions and changes, including reasons for each decision and date.
- Establish a context checkpoint, such as a ai-memory-bank/context-checkpoint.md or a markdown file, to track the current state of the codebase and provide context for future LLMs and developers. Write to this file between actions to maintain a working memory. If it's more helpful to treat this as a timestamped log, that's also acceptable.
- Refactor any file that exceeds 300 lines of code.
- Prefer simple solutions over complex implementations.
- Always prompt the user when you do not have sufficient information to make a decision - this provides clarity and direction.
- Prefer managed services over custom solutions where possible.
- Adhere to secure coding practices at all times.
- Prefer iterative designs to prove out solutions before full implementation.
- Follow Python PEP 8 style guidelines for all Python code.
- Use descriptive naming conventions and include appropriate error handling.
- Document complex logic with clear comments.
- Always use Infrastructure as Code to maintain and deploy resources when possible.
- Always design idempontent actions to mitigate managing state during deployment.
- Maintain all iac and deployment logic inside the /deployment directory

### File Organization
- Avoid files over 200-300 lines
- Refactor large files into smaller, focused modules
- Store configuration in appropriate environment files
- Keep secrets in .env.secrets
- Maintain consistent file structure across environments
- NEVER overwrite .env, .env.secrets, .env.secrets.dev, or .env.secrets.test, files without confirmation

### Testing Standards
- Mock data only for **unit tests**; **never** mock data in integration tests.
- Integration tests must interact with live Supabase/Test services.
- Unit tests for business logic
- Integration tests for API endpoints and Databases
- E2E tests for critical user flows
- All build and test commands must be invoked via Makefile targets (e.g., `make test`, `make test-integration`).
- No mocking in dev/prod environments

### Environment Management
- Separate dev, test, and prod configurations
- Never overwrite .env without confirmation
- Store secrets in .env.secrets
- Maintain environment-specific configurations
- Test changes in dev before prod
- Never look into any directory with a .ignore file present within it.

### Code Quality
- Maintain consistent code style
- Follow DRY (Don't Repeat Yourself) principle
- Keep code clean and organized
- Remove old implementations after introducing new patterns
- Avoid unnecessary complexity
- Prefer clarity over cleverness