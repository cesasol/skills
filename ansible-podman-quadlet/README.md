# ansible-podman-quadlet (skill)

General skill for managing Podman Quadlets (systemd unit files) with the
`containers.podman` Ansible collection — generating `.container`/`.pod`/
`.network`/`.volume`/`.image` files idempotently via `state: quadlet`,
installing/removing Quadlet bundles with `podman_quadlet`, and managing
Podman secrets, networks, volumes, pods, and images.

## Files

| File | Purpose |
| ------ | --------- |
| `SKILL.md` | Main skill — patterns, secrets, registry auth, health, lifecycle, idempotency, gotchas. |
| `references/quadlet-params-cheatsheet.md` | Per-module first-class params vs `quadlet_options` raw lines, plus Podman→systemd unit name mapping. |
| `examples/deploy-quadlets.yml` | Worked example: a pod + network + volume + two containers (webapp + dependent worker) with secrets, health, registry auth, ordering, and restart-on-change. |
| `evals/evals.json` | Test prompts for the skill. |

See `SKILL.md` for the triggering description and full guidance.
