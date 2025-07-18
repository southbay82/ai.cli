---
description: Content path rules and ContentItem.save contract
---

# Content Path Design

This document captures the **single-argument** contract for `ContentItem.save()` and the directory layout rules for global / project / tool-specific content.

## 1. `ContentItem.save()` contract
```python
ContentItem.save(path_or_dir: Union[str, Path]) -> Path
```

* `path_or_dir` can be **either**
  1. A directory (existing or not) ⇒ `save()` generates a filename from the item’s name and appends it to the directory.
  2. A full file path (has an extension such as `.yaml`, `.yml`, `.json`) ⇒ `save()` writes **exactly** to that path.
* Behaviour is purely data-driven:
  * If `Path(path_or_dir).suffix` is `` (empty)  → treat as directory.
  * Else treat as explicit file path.
* Generated filename = `slugify(name) + default_ext`.  Default extensions:
  | ContentType | ext |
  |-------------|------|
  | RULE / WORKFLOW / PROFILE | `.yaml` |
  | MCP | `.json` |
* The function always:
  1. Ensures `output_path.parent.mkdir(parents=True, exist_ok=True)`.
  2. Serialises YAML w/ `yaml.dump()` or JSON with `json.dump()`.
  3. Sets `self.path = output_path` and returns it.
* **Removed arguments**: `base_dir` (previous versions) is now obsolete.  Callers simply pass a directory when they need auto-naming.

### Deprecations
Old call sites that still pass the former `(base_dir, filename)` pairs must be updated.  A thin shim emitting `DeprecationWarning` will live until 0.6.0.

## 2. Directory conventions
* **Global Tool Directories**  (under `$HOME`)
  * Amazon Q   → `~/.q/` (rules ⇢ `rules/`, profiles ⇢ `profiles/`)
  * Windsurf     → `~/.windsurf/` (personas under `personas/`)
  * Gemini       → `~/.gemini/prompts/`
* **Project scope**
  * Each project has `.ai.cli/<content_type>/` by default.
  * Example: `<project>/.ai.cli/rules/bug_fixes.yaml`.
* **Workspace sync rules**
  * The `sync` command copies from project scope to each enabled tool directory using an Adapter transform if necessary (e.g., Rule YAML → Amazon Q YAML).

## 3. Public Interfaces (frozen)
| Component | Method | Note |
|-----------|--------|------|
| ContentItem | `save(path_or_dir)` | new single-arg signature |
| ContentManager | `add_item(item, *, overwrite=False, target_dir: Path)` | target_dir is the directory where the item should live |
| Adapters | `write_rule(rule, target_dir)` etc. | must pass directory, *never* file path |

## 4. TODOs after adoption
* Update unit/integration tests for new signature – `TODO(ai.cli): update tests for save() refactor (2025-07-18)`.
* Remove deprecation shim after all call-sites migrate.
