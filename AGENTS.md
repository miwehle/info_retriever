# Agent Notes

## Shared Base

Before starting work, read [AGENTS_BASE.md](../../dev/agents-base/AGENTS_BASE.md). Its rules, including the referenced test rules, are binding for this repository. The following rules supplement that shared base.

## Test Code

Do not modify the shared test rules as part of work on Info Retriever.

- Separate correctness tests from retrieval-quality evaluation: pytest checks behavior such as correct source mapping and ranking calculations; a small set of representative questions and expected passages helps assess search usefulness. Passing correctness tests alone does not establish good retrieval quality.
