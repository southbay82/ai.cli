---
description: Update the documentation
---

---
description: keep documentation in-sync with codebase changes
---

1. Review change scope  
   • Read the latest commit messages (last 10 or more commits or PR description).  
   • Identify keywords: table names, package names, env-vars, new features, tests, integration, security or other key terms related to code changes.

2. Search the **entire** repo – code and docs  
   // turbo  
   run: grep -RniE "(public\.users|public\.profiles|<other-keywords>)" docs/ code/ | head -n 200

3. Update docs in-place  
   • For each hit inside `docs/` or markdown in `code/`, open the file, edit the outdated reference, and add a short “Last updated: YYYY-MM-DD” line.  
   • Keep historical references (e.g., decision-log) but mark them “legacy” when appropriate.

4. Regenerate high-level docs (if any)  
   • `make docs` or `npm run docs:build` (if we use a generator).  
   • Check rendered output locally.

5. Validate links  
   // turbo  
   run: markdown-link-check -q docs/**/*.md

6. Commit & tag  
   • `git add docs/**/*.md`  
   • `git commit -m "docs: sync with <feature> change"`  
   • `git tag docs-sync-$(date +%Y%m%d)`

7. PR / merge policy  
   • Documentation PR must pass `make lint-docs` and link-check CI steps.  
   • CI blocks merge if code changes reference tables or packages not present in docs.