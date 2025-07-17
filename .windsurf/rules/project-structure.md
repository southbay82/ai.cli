---
trigger: always_on
---

## Project Structure Rules
Utilize the following directory structure.
- /doc - All related documentation exists in here.
- /memory-bank - All AI/LLM helper documentation including project summary, component summary, todo for task tracking, decision log, and other temporary docs live here.
- /src - Application source code exist in this directory
- /tests - Unit and Integration Tests
- /deployment - Deployment related scripts, infrastructure as code and configuration files exist in this directory
- /deployment/data - Any database or datastore scripts for schema, change scripts reside here. If the database you are working with has a specific migration script utility which uses it's own specific directory structure, use that instead.
- /util_scripts - Any helper scripts during development go here. 
- /config - This is mainly to store different configurations for each of the components in our applications.
- .ignore Ignore any directory and it's contents which contains a .ignore file.
- Makefile -  Use for installing dependencies, linting, formatting, quick testing. (make build {env}, make test {env}, make deploy {env})
- /content - contains the content we will distribute and deploy for an end user.
- /content/rules - AI IDE rules for an LLM
- /content/global - Global rules for the AI tool
- /content/project - Project specific rules, also inherited by Amazon Q Profiles
- /content/amazonq_profiles - Amazon Q CLI profiles
- /content/windsurf_workflows - Windsurf Workflows