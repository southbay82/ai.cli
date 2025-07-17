---
trigger: always_on
---

##GitHub Actions Workflows Rules

# Enabling Debug Logging for GitHub Actions Workflows

This document outlines the steps to enable debug logging for GitHub Actions workflows, as sourced from the GitHub documentation. Debug logging provides detailed logs to troubleshoot and monitor workflows effectively.

## Overview

Debug logging in GitHub Actions allows you to access verbose logs for workflow runs, which can help diagnose issues with actions, runners, or workflow configurations. Enabling debug logging requires specific permissions and the use of repository secrets or variables.

## Prerequisites

- **Repository Permissions**: You need write access to the repository to enable debug logging.
- **Secrets or Variables Access**: You must have permission to create or modify repository secrets or variables.

## Steps to Enable Debug Logging

1. **Navigate to the Repository**:
   - Go to the repository where the workflow is defined on GitHub.

2. **Access Settings**:
   - Click the **Settings** tab in the repository.

3. **Manage Secrets or Variables**:
   - Under the **Security** section, expand **Secrets and variables** and select **Actions**.
   - Choose either **Secrets** or **Variables** based on your preference for storing the debug setting.

4. **Create a New Secret or Variable**:
   - Click **New repository secret** or **New repository variable**.
   - Name the secret or variable `ACTIONS_STEP_DEBUG`.
   - Set the value to `true`.

5. **Save the Secret or Variable**:
   - Click **Add secret** or **Add variable** to save the configuration.

6. **Rerun the Workflow**:
   - Trigger the workflow again (e.g., via a push, pull request, or manual dispatch).
   - Debug logging will now be enabled for all subsequent workflow runs.

## Viewing Debug Logs

- Once debug logging is enabled:
  - Go to the **Actions** tab in the repository.
  - Select the workflow run you want to inspect.
  - Expand the job steps to view detailed debug logs, which include additional information such as environment variables, action inputs/outputs, and runner diagnostics.

## Disabling Debug Logging

To disable debug logging:
1. Return to **Settings** > **Secrets and variables** > **Actions**.
2. Locate the `ACTIONS_STEP_DEBUG` secret or variable.
3. Either:
   - Delete the secret/variable.
   - Set its value to `false`.
4. Save the changes.

## Notes

- **Security Considerations**:
  - Debug logs may contain sensitive information, such as environment variables or action outputs. Ensure that only trusted users have access to these logs.
  - Avoid enabling debug logging in public repositories unless necessary, as logs may expose sensitive data.

- **Performance Impact**:
  - Debug logging increases log verbosity, which may slow down workflow execution or increase log storage usage.

- **Scope**:
  - The `ACTIONS_STEP_DEBUG` setting applies to all workflows in the repository where it is defined.
  - To enable debug logging for specific workflows, consider using workflow-specific conditions or matrix strategies instead of repository-wide settings.

## Additional Debugging Options

- **Runner Diagnostics**:
  - To enable more detailed runner diagnostics (e.g., for self-hosted runners), create a secret or variable named `ACTIONS_RUNNER_DEBUG` and set it to `true`.
  - This provides additional logs about the runner's operations, such as network calls and process execution.

## Troubleshooting Tips

- If debug logs do not appear:
  - Verify that the `ACTIONS_STEP_DEBUG` secret or variable is correctly set to `true`.
  - Ensure the workflow run was triggered after the setting was applied.
  - Check for typos in the secret/variable name.
- If logs are too verbose:
  - Consider temporarily enabling debug logging only for problematic runs and disabling it afterward.

## Source

This information is based on the GitHub Actions documentation for enabling debug logging, available at: [GitHub Docs - Enabling Debug Logging](https://docs.github.com/en/actions/how-tos/monitoring-and-troubleshooting-workflows/troubleshooting-workflows/enabling-debug-logging).

---
*Last updated: July 10, 2025*