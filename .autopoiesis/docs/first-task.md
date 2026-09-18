# First development task

Use this task in the web interface after configuring model and GitHub access.
The project directory is /projects/app.

> Read AGENTS.md and README.md. Extend the example CLI with a --json option.
> It should output a JSON object with the integer fields characters, words,
> and lines. Without --json, preserve the existing text output.
> The option must work with both a text argument and stdin.
> Add behavioral tests, including empty text and Unicode input, and run
> sh .autopoiesis/scripts/check.sh. Work on a new ai/json-output branch,
> commit the change, push the branch, and open a draft PR against main.
> Describe the change and the checks you ran in the PR. Stop afterwards.

## Acceptance criteria

- Validate JSON with a real parser and verify that it contains exactly the three fields.
- Existing CLI tests continue to pass.
- The PR includes the implementation and relevant tests.
- GitHub Actions passes; the local agent response alone does not count as
  independent CI evidence.
