# Agent Notes

## Working Style

### KISS and YAGNI

KISS and YAGNI are high values in this workspace.
Do not add code just because it might help later.
Before adding code, check: is it required now, is there a simpler existing
pattern, and will it stay easy to understand tomorrow?

Keep modules easy to read and low in mental load.
Ask before adding complexity whose value is unclear.
Favor simplicity for flexibility and design for change: understandability is a
long-lived value, complexity must earn its cost, and changeability often comes
from simplicity rather than anticipation.

For design sketches and diagrams, start with the smallest useful representation.
Show only the core idea first; add detail only when the user asks for it or when
the current task clearly requires it.

Use abstractions only when they reduce current complexity or match an existing
pattern. Treat speculative generalization, optional modes, config flags,
future-proofing, and indirection as complexity costs and mental load.
Add them only for a concrete current need or when the user explicitly agrees.

Before answering concrete factual questions, verify local facts first when a
few seconds of inspection can avoid hedged answers such as "if" or "probably."

### Design First

Find the good design first; only then discuss implementation details. Good design is the first practical lever for KISS.

KISS is king, and simple design is his closest ally.

If the design is questionable or not KISS, say so plainly. Always prioritize KISS. Do not leave this path, and help the user stay on it too.

If the user appears to be following an unnecessarily complex path, pause and point to the simpler design before implementing.

### Deep Modules and Detail Hiding

Prefer deep modules: separate the levers from the details. Prefer deep modules over shallow ones: hide real complexity behind small, clear interfaces. A good API should reduce the caller's cognitive load.

Deep modules and information hiding are very welcome in this workspace. Public APIs should make common use simple, expose the right levers, and keep implementation details under the hood.

### Refactoring and Automated Tests

KISS is king. Refactoring keeps the kingdom tidy; automated tests guard the gates. Treat refactoring as an active parallel process that preserves or restores simple design while behavior evolves, and use automated tests to keep that process safe.

Outside the user's explicit `#focus` mode, proactively point out concrete, likely worthwhile simplification or refactoring opportunities; ask whether to schedule or do them soon instead of silently carrying complexity forward.

### Cost-Aware Alternative Selection

When proposing or comparing implementation alternatives, estimate the likely cost and complexity of each option, especially hidden infrastructure cost such as orchestration, persistence, evaluation, reporting, notebooks, tests, and integration glue.

If the user chooses an option that appears significantly more complex or costly than another viable option, pause before implementation and explicitly call out the tradeoff. Ask for confirmation in plain language, for example: "This option likely costs much more code because it duplicates existing experiment infrastructure. Do you still want this path?"

Do not treat "go" as overriding this warning when the selected option conflicts with KISS/YAGNI or appears to create avoidable infrastructure duplication. First confirm that the user intentionally accepts the extra complexity.
### Explicit Simplification Tasks

When the task is explicitly to simplify, aim to reduce code and mental load while preserving behavior. Use LOC as a supporting indicator, not a hard budget; readability and maintainability take priority over line count.
Briefly explain any code growth needed for a clearer design. Ask before materially expanding the agreed scope or adding complexity whose value is unclear.
Do not bundle simplification with new semantics, new data flows, or extra reporting fields unless the user explicitly agrees.

### Markdown

Keep each prose paragraph on one source line; use line breaks only for structure.

### Encoding

Use UTF-8 for text files. When reading German prose or other non-ASCII text through PowerShell, make the command umlaut-safe by setting console output encoding to UTF-8 and reading files as UTF-8, for example: `[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); $OutputEncoding = [System.Text.UTF8Encoding]::new(); Get-Content -Raw -Encoding UTF8 path\to\file.md`.

If umlauts or other non-ASCII text appear corrupted in tool output, assume an encoding/display issue first and verify with an UTF-8-safe read before treating it as a content problem.

### Test Code

For test code, follow `../nmt_lab/translator/how_to_test.md` (relative to this AGENTS.md). Treat it as part of this AGENTS.md. Do not modify the shared file as part of work on Info Retriever.

The following clarifications take precedence where the shared test rules are stricter:

- Keep test modules and classes aligned with production code for navigation, but select test cases by meaningful observable behavior and risk, not by a mandatory test for every public function.
- Core logic may remain private behind a stable public interface if its behavior can be adequately tested through that interface. Do not expose internals solely to test them.
- Separate correctness tests from retrieval-quality evaluation: pytest checks behavior such as correct source mapping and ranking calculations; a small set of representative questions and expected passages helps assess search usefulness. Passing correctness tests alone does not establish good retrieval quality.

### PlantUML

Keep `.puml` sequence diagrams compact and navigable.
Use `hide footbox` in sequence diagrams.
Use plain lifeline heads plus `url of Alias is [[...]]` for clickable participants, not inline-linked participant labels.
Use message links only when they point to one concrete function or API, and keep at most one link per message.
Prefer local `vscode://file/...` links for workspace code; use external API links sparingly for established external concepts such as Optuna, Gymnasium, and PyTorch.
Centralize the local workspace URI in `puml_links.iuml` and use `WORKSPACE_ROOT/...` in PUML links instead of repeating the absolute path.
Do not add extra notes just to hold secondary links.
Use `\n` in long labels when it keeps the diagram narrow and the link still works.
Use `update pumls` or `aktualisiere pumls` as an explicit maintenance command.
For that command, find all `.puml` files and refresh local `vscode://file/...:line:col` links semantically against the current workspace code.
Do not check all PUML links on every code change; do it only when this command is requested or when directly editing a PUML file.
After refreshing links, mechanically check that local targets exist, line numbers are valid, and messages do not contain multiple links.

### Alignment

Before changing workspace files, establish alignment with the user on the direction and size of the change. An explicit request or approval authorizes work within that agreed scope; do not ask again for routine implementation steps. Seek renewed alignment for material changes in direction, scope, or complexity.

NCY means "no change yet": do not edit workspace files. Understand it as a chat
shortcut for discussing and drafting the approach first; code changes may follow
only after the user agrees.

GO means "go ahead": the user wants the discussed change implemented. Proceed
with the agreed direction and scope, and keep the implementation focused.

## Essence 

KISS/YAGNI, so complexity does not grow out of "this might be useful later."

Alignment before edits, so the agent does not rush ahead.

Simplicity for maintainability, so the system is still understandable and easy
to change tomorrow.
