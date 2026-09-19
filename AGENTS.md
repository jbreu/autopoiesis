# Product instructions

This file contains product-specific guidance for the repository.

When this repository is developed through Autopoiesis, these instructions are
combined with `.autopoiesis/AGENTS.md`. Read and apply both files before
starting a task. Keep harness workflow, Git delivery, runtime, and security rules
in `.autopoiesis/AGENTS.md` rather than duplicating them here.

## Product scope

- Application code is in `src/repo_demo`; behavioral tests are in `tests`.
- The current application is only an example product for exercising the
  Autopoiesis harness.
- Use English for product documentation, code comments, and user-facing text.
- Preserve the documented CLI behavior unless the task explicitly changes it.
- Keep the example application's runtime dependency-free where practical.

## Product verification

- Add or update behavioral tests for observable product changes.
- Use a regression test when fixing an observable bug.
- Do not weaken existing assertions merely to make a change pass.
- Run the product tests relevant to the task. The Autopoiesis instructions
  define the repository-wide check entrypoint that must also be run before
  delivery.
