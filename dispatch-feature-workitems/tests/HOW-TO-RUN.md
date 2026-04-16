# How to Run Skill Tests

Tests follow the RED → GREEN → REFACTOR cycle from `superpowers:writing-skills`.

## Setup

Tests need a realistic target repo. Use a throwaway clone or a dedicated test fixture:

```bash
git clone <any-node-or-python-repo> /tmp/skill-test-repo
cd /tmp/skill-test-repo
```

The repo needs a GitLab remote so `glab mr create` has somewhere to point.

## RED Phase — Baseline (without skill)

1. Open a fresh Claude Code session in the target repo
2. Do NOT load `dispatch-feature-workitems`
3. Paste the **Input Prompt** from the scenario verbatim
4. Watch what the agent does — do not intervene
5. Fill in the **Baseline Failure Log** in the scenario file:
   - Check every assertion in the checklist
   - Record verbatim rationalizations the agent used to skip steps

This documents what the skill needs to fix.

## GREEN Phase — Compliance (with skill)

1. Open a fresh Claude Code session in the same repo
2. Load the skill: invoke `dispatch-feature-workitems`
3. Paste the same **Input Prompt**
4. Check every assertion in the checklist again
5. Fill in the **Skill Compliance Log**

All assertions should pass. If any fail, move to REFACTOR.

## REFACTOR Phase — Close Loopholes

For each new failure or rationalization found in GREEN:
1. Add an explicit counter to `SKILL.md` (rationalization table or Common Mistakes)
2. Re-run the GREEN phase
3. Repeat until all assertions pass across two consecutive runs

## Adding New Scenarios

Create `tests/scenario-NN.md` when you find a new failure mode not covered by existing scenarios.
Good candidates:
- A project with no lockfile (tests dep-detection skip path)
- A single-item list (tests that the skill still creates a worktree, not just edits in place)
- A Python project (tests uv/pip detection path)
