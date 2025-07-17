---
trigger: model_decision
---

# Developer Tools Reference

This document lists the main Windsurf/Cascade tools available in this workspace and what they are used for.

## 1. Code Navigation
* **find_by_name** – Locate files or directories by glob pattern.
* **grep_search** – Search for text/regex matches across the codebase.
* **view_file_outline** – View a file’s outline (functions/classes, ranges).
* **view_line_range** – Read specific line ranges of a file.
* **view_code_item** – Fetch the full source of a function/class.
* **search_in_file** – Find relevant snippets inside one file.

## 2. Code Editing
* **replace_file_content** – Modify existing files by replacing exact chunks.
* **write_to_file** – Create new files (will auto-create parent dirs).

## 3. Running & Debugging
* **run_command** – Execute shell commands in the project directory.
* **browser_preview** – Open a browser preview after starting a local web server.

## 4. Deployment Helpers
* **read_deployment_config** – Inspect deployment configuration (e.g., Netlify).
* **deploy_web_app** – Deploy frontend/web apps.
* **check_deploy_status** – Poll a deployment for its build status.

## 5. Supabase MCP Toolkit (mcp3_…)
Extensive set for managing Supabase projects:
* `mcp3_execute_sql`, `mcp3_apply_migration`, `mcp3_get_logs`, etc.
* Allows creating branches, running migrations, deploying Edge Functions, fetching advisors, etc.

## 6. Knowledge & Documentation
* **search_web** – Basic web search.
* **mcp0_resolve-library-id / mcp0_get-library-docs** – Fetch up-to-date library docs via Context7.

## 7. Planning & Memory
* **update_plan** – Maintain the current project plan.
* **create_memory** – Persist user preferences & project context.

---

### Usage Notes
* Use navigation tools before editing to understand the context.
* Combine all edits to one file in a single `replace_file_content` call.
* Only call tools when necessary—they are resource-intensive.
* Respect user’s preference for silent lint/compile fixes: continue until tests pass.
