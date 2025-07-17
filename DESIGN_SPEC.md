
# Design Specification: ai.cli

## 1. Introduction

`ai.cli` is a command-line interface (CLI) tool designed to streamline the management and usage of various AI development tools and resources, including Gemini, Amazon Q for CLI, and Windsurf. It provides a unified interface for managing configuration profiles, reusable prompts (MCPs), rules, and complex workflows.

The tool features a dual interface: direct command execution via switches and an interactive menu for guided operations. It supports both global (user-level) and project-specific configurations, allowing for flexible and context-aware AI development.

## 2. Core Concepts

- **Profiles**: A collection of settings that define a specific configuration for an AI tool. This can include API endpoints, model parameters, and other preferences.
- **Rules**: A set of instructions or constraints provided to an LLM to guide its behavior, ensuring consistent and desired output.
- **MCPs (Multi-turn Conversation Prompts)**: Reusable templates for prompts that can handle complex, multi-turn conversations with an AI.
- **Workflows**: A series of chained prompts or commands that act as a "macro" to perform complex, multi-step tasks.
- **Global vs. Project Scope**:
    - **Global**: A central repository of shared resources located at `~/.ai.cli`. These are available across all projects.
    - **Project**: A local directory (`<project>/.ai.cli`) that can contain project-specific resources or override global ones.

## 3. Command Line Interface (CLI)

The tool is invoked as `ai.cli`.

### Usage

```bash
# Launch the interactive menu
ai.cli

# Direct command execution
ai.cli [command] [subcommand] [options]
```

### Commands

- **`ai.cli <tool_name> [args...]`**: Pass-through command to execute a specific AI tool.
  - *Example*: `ai.cli gemini "Summarize this document."`

- **`ai.cli sync-all`**: Updates all global resources by syncing with the configured Git repository.

- **`ai.cli sync-project`**: Copies or updates the resources from the global store to the current project's `.ai.cli` directory.

- **`ai.cli manage [resource] [action]`**: Command to manage resources.
  - **Resources**: `profile`, `mcp`, `rule`, `workflow`, `token`
  - **Actions**: `add`, `list`, `edit`, `remove`
  - *Examples*:
    - `ai.cli manage mcp list`
    - `ai.cli manage token add`

- **`ai.cli backup [action]`**: Manages backups.
  - **Actions**: `list`, `restore`
  - *Example*: `ai.cli backup restore`

## 4. Interactive Menu

Running `ai.cli` without arguments launches a user-friendly interactive menu, built with a library like `rich` or `inquirer`.

### Menu Structure

```
Main Menu:
  - Use an AI Tool (Gemini, Amazon Q, etc.)
  - Manage Global Resources
    - Profiles
    - MCPs
    - Rules
    - Workflows
  - Manage Project Resources
    - Profiles
    - MCPs
    - Rules
    - Workflows
  - Manage Access Tokens
  - Synchronization
    - Sync All Global Resources
    - Sync Project from Global
  - Backup and Restore
  - Exit
```

## 5. Directory Structure

### Global (`~/.ai.cli/`)

```
~/.ai.cli/
├── config.json         # Main configuration, including git repo URL
├── tokens.json         # Encrypted file for personal access tokens
├── profiles/           # Global profiles
├── rules/              # Global rules
├── mcps/               # Global MCPs
├── workflows/          # Global workflows
└── backups/
    ├── mcps_20250716_103000/
    └── ... (maintains 5 rolling backups per resource)
```

### Project (`<project_root>/.ai.cli/`)

```
<project_root>/.ai.cli/
├── config.json         # Project-specific settings and overrides
├── rules/              # Project-specific rules
├── mcps/               # Project-specific MCPs
└── workflows/          # Project-specific workflows
```

## 6. File Formats

- **`config.json`**: JSON for all configurations.
- **`tokens.json`**: JSON for access tokens.
- **Resources (`.yml`)**: MCPs, Rules, and Workflows will be stored in YAML format for readability and ease of editing. Each file represents one resource.

## 7. Synchronization Logic

- The tool will manage a user-configured Git repository for the global resources.
- `ai.cli sync-all` will perform a `git pull` to update the local `~/.ai.cli` directories from the remote repository.
- `ai.cli sync-project` will intelligently copy or symlink resources from `~/.ai.cli` to the project's `.ai.cli` directory based on the project's configuration.

## 8. Backup and Restore

- Before any write operation (add, edit, remove, sync), a compressed, timestamped backup of the target directory is created.
- The system will automatically maintain the 5 most recent backups, deleting the oldest one as new ones are created.
- `ai.cli backup restore` will provide an interactive prompt to select and restore a backup.

## 9. Installation

- The tool will be packaged for distribution via `pip` (Python) or `npm` (Node.js).
- An installation script (`install.sh`) will be provided for easy setup.
- The script will perform the following actions:
  1. Install the tool and its dependencies.
  2. Create the `~/.ai.cli` directory structure.
  3. Add the `ai.cli` executable to the user's shell `PATH` (e.g., by modifying `.bashrc` or `.zshrc`).

## 10. Security

- The `tokens.json` file will be protected with file permissions set to `600` (read/write for owner only).
- The file's contents will be encrypted using a key derived from a user-defined password or system keychain.

## 11. Future Considerations

- **Hooks/Callbacks**: Implement a system for triggering external scripts or agents at different stages of a workflow.
- **Plugin Architecture**: Design a plugin system to allow for easy integration of new AI tools and services.
- **Extensibility**: Allow users to define custom resource types beyond the default ones.
