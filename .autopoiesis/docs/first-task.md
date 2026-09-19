# First development task

Use this task in the web interface after configuring model and GitHub access.
The project directory is /projects/app.

> Read AGENTS.md, .autopoiesis/AGENTS.md, and README.md. Apply both AGENTS files
> together. Extend the example CLI with a --json option.
> It should output a JSON object with the integer fields characters, words,
> and lines. Without --json, preserve the existing text output.
> The option must work with both a text argument and stdin.
> Before editing, run
> python3 /projects/app/.autopoiesis/scripts/prepare_task.py json-output and
> continue in the task root it prints. Add behavioral tests, including empty
> text and Unicode input, and run sh .autopoiesis/scripts/check.sh. Commit the
> verified change locally. Do not push or create a PR yet. Stop afterwards.

After reviewing the local result, a separate user message such as:

> Push this task branch to origin.

authorizes only the push. A later message such as:

> Create a draft PR for this change.

authorizes creating the PR and, if necessary, the prerequisite push.

## Acceptance criteria

- Validate JSON with a real parser and verify that it contains exactly the three fields.
- Existing CLI tests continue to pass.
- The local task branch contains the implementation and relevant tests.
- No remote branch or PR exists until explicitly requested.
- If a PR is later requested, GitHub Actions passes; the local agent response
  alone does not count as independent CI evidence.
