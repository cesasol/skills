# gitlab-mr-review
- Spawn subagents for large MRs to parallelize review. Confidence: 0.75
- For code-related comments: generate atomic, actionable findings using `--file` and `--line` flags. Confidence: 0.75
- For non-code or cross-cutting comments: use `- [ ]` checkboxes to track progress. Confidence: 0.75
