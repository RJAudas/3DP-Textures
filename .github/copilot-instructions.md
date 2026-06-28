This repository is currently a Spec Kit/Copilot scaffold. There is no product source tree or build manifest yet; derive build, test, lint, and single-test commands from the active feature plan once implementation files exist.

## Spec Kit workflow

- Feature work is driven by Copilot agents/prompts in `.github\agents\speckit.*.agent.md` and `.github\prompts\speckit.*.prompt.md`.
- Use the normal sequence: `speckit.specify` → `speckit.plan` → `speckit.tasks` → `speckit.implement`; `speckit.analyze` is read-only and checks consistency across `spec.md`, `plan.md`, and `tasks.md`.
- The full workflow definition is `.specify\workflows\speckit\workflow.yml`; it includes review gates after specification and planning.
- Run the PowerShell helpers from the repository root:
  - `.specify\scripts\powershell\setup-plan.ps1 -Json`
  - `.specify\scripts\powershell\setup-tasks.ps1 -Json`
  - `.specify\scripts\powershell\check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks`
- The active feature is resolved from `SPECIFY_FEATURE_DIRECTORY` first, then `.specify\feature.json`; if neither exists, prerequisite scripts fail and the next step is to run `speckit.specify`.

## Architecture and generated artifacts

- `.specify\templates\` contains the canonical templates for `spec.md`, `plan.md`, `tasks.md`, checklists, and the constitution. Treat these as workflow templates, not product documentation.
- Feature artifacts are created under `specs\<NNN-feature-name>\` using sequential three-digit numbering from `.specify\init-options.json`. The spec directory and git branch are independent.
- A complete planned feature may contain `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts\`, and `tasks.md`.
- `.specify\extensions\agent-context\` owns the managed section below. Its hooks are configured in `.specify\extensions.yml` and can refresh this file after `speckit.specify` or `speckit.plan`.

## Repository conventions

- Prefer the PowerShell Spec Kit scripts in `.specify\scripts\powershell\`; this project was initialized with `"script": "ps"`.
- Keep the Spec Kit managed block intact. Add durable Copilot guidance outside the `<!-- SPECKIT START -->` / `<!-- SPECKIT END -->` markers because the extension may rewrite the marked section.
- Generated tasks must follow the checklist format from `.specify\templates\tasks-template.md`: `- [ ] T### [P?] [US#?] Description with exact file paths`.
- Organize implementation work by independently testable user stories in priority order, with foundational tasks blocking story work and an MVP checkpoint after User Story 1.
- Tests in generated `tasks.md` are optional unless the feature spec explicitly requests them; when requested, write the test tasks before implementation tasks for that story.
- When planning, fill unknown technical context as `NEEDS CLARIFICATION` and resolve it in `research.md` before design artifacts are finalized.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan at
`specs/002-printable-texture-addon/plan.md`.
<!-- SPECKIT END -->
