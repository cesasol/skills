---
name: ansible-podman-quadlet
description: |
  Use when deploying Podman workloads as systemd units with Ansible via the containers.podman collection — generating `.container`/`.pod`/`.network`/`.volume`/`.image` Quadlet files idempotently with `state: quadlet` instead of hand-templating them (or `podman_generate_systemd`), installing/removing Quadlet bundles with `podman_quadlet`, and managing Podman secrets/networks/volumes/pods/images. Trigger on "podman quadlet", "podman_container", "podman_pod", "podman_network", "podman_volume", "podman_image", "podman_secret", "podman_quadlet", "deploy podman with ansible", "podman systemd unit", "podman generate systemd", "quadlet file", or any task that asks to manage Podman containers/pods/networks/images/volumes declaratively from Ansible, even when the user doesn't name the modules explicitly.
---

# Podman Quadlets via the containers.podman collection

The `containers.podman` Ansible collection manages the full Podman lifecycle declaratively.
This skill focuses on the **Quadlet** path: generating Podman-managed systemd unit files
idempotently so Podman starts containers/pods/networks/volumes/images as native
`systemd` services — the modern replacement for both `podman run` wrappers and the legacy
`podman_generate_systemd` output.

With `state: quadlet`, the resource modules (`podman_container`, `podman_pod`, `podman_network`,
`podman_volume`, `podman_image`) **write** a Quadlet file from first-class module parameters —
real idempotency, `--check --diff`, input validation, upstream-maintained syntax. `podman_quadlet`
is the separate **install/remove** layer for vendoring ready-made Quadlet files.

## Collection facts (verified against `containers.podman` 1.20.2)

- `podman_container`, `podman_pod`, `podman_network`, `podman_volume`, `podman_image` all accept
  `state: quadlet` and expose `quadlet_dir`, `quadlet_filename`, `quadlet_file_mode`,
  `quadlet_options`. ("Write a quadlet file with the specified configuration.")
- `podman_quadlet` runs `podman quadlet install` / `podman quadlet rm` and reloads systemd
  (`reload_systemd: true` by default). It consumes an existing file/dir/URL — it does **not**
  generate Quadlet content. Generation is the job of the resource modules above.
- `podman_generate_systemd` is the **legacy** generator predating Quadlets. Prefer Quadlets
  (the `state: quadlet` modules) for new work; only reach for `generate_systemd` on hosts
  running very old Podman (pre-4.4) that lacks the Quadlet generator.
- `podman_secret`, `podman_image`, `podman_network`, `podman_volume`, `podman_pod` cover the
  rest of the lifecycle outside of Quadlet generation.

## Podman Quadlet → systemd unit naming

Podman's systemd generator maps Quadlet files to unit names. The unit name is what you
`enable --now` and what `notify`/`when` handlers reference — enable `foo.service`, not `foo.container`.

| Quadlet file       | systemd unit             |
| ------------------ | ------------------------ |
| `<name>.container` | `<name>.service`         |
| `<name>.pod`       | `<name>-pod.service`     |
| `<name>.network`   | `<name>-network.service` |
| `<name>.volume`    | `<name>-volume.service`  |
| `<name>.image`     | `<name>-image.service`   |
| `<name>.kube`      | `<name>.service`         |
| `<name>.build`     | `<name>-build.service`   |

## Two patterns

### Pattern A — declarative generation (default; replaces hand-templated quadlets)

Resource module `state: quadlet` writes the unit file. You then daemon-reload and enable it.
Works for containers, pods, networks, volumes, images.

```yaml
- become: true
  containers.podman.podman_container:
    name: myapp
    image: docker.io/library/redis:alpine
    state: quadlet                       # write ./myapp.container, do NOT run the container
    quadlet_dir: /etc/containers/systemd  # default for root; set explicitly for clarity
    quadlet_filename: myapp              # optional; defaults to `name`
    quadlet_file_mode: "0644"
    network: host
    publish: ["6379:6379"]
    volumes: ["/opt/myapp/data:/data:Z"]
    env:
      REDIS_PASSWORD: "{{ redis_pw }}"
    healthcheck: "redis-cli ping | grep PONG"
    healthcheck_interval: 30s
    healthcheck_retries: 3
    quadlet_options:                     # raw lines appended for keys lacking a first-class param
      - "AutoUpdate=registry"
      - "[Service]"
      - "Restart=always"
      - "TimeoutStartSec=300"
      - "[Install]"
      - "WantedBy=multi-user.target"
  register: myapp_quadlet

- become: true
  ansible.builtin.systemd:
    daemon_reload: true
- become: true
  ansible.builtin.systemd:
    name: myapp.service                   # the generated unit name
    enabled: true
    state: "{{ 'restarted' if myapp_quadlet.changed else 'started' }}"
```

Why the chunked `quadlet_options` above: `AutoUpdate=`, `[Service] Restart=`/`TimeoutStartSec=`,
and `[Install] WantedBy=` have **no first-class param** on `podman_container` — they are
systemd/Quadlet directives, not `podman run` flags — so they ride along as raw lines. `Restart=`
here is the *systemd* service restart policy, *not* the module's `restart_policy` param (which
maps to `podman run --restart-policy`, a different concept and ignored under `state: quadlet`).

A multi-resource deployment (pod + network + volume + containers) generates each Quadlet in its
own task, then chains them by unit name — see `examples/deploy-quadlets.yml`.

### Pattern B — vendoring ready-made Quadlets (use `podman_quadlet`)

When Quadlet files already exist (a vendor ships them, you render them once, or you adopt a
`.quadlets` multi-section bundle), install and lifecycle them with `podman_quadlet`:

```yaml
- become: true
  containers.podman.podman_quadlet:
    state: present
    src: /tmp/webapp.quadlets            # Podman 6+: multi-section file, each needs "# FileName=name"
    quadlet_dir: /etc/containers/systemd
  # reload_systemd defaults to true -> daemon-reload happens here
```

`.quadlets` bundles require each section to start with a `# FileName=<name>` comment. Remote URL
`src` always reports `changed: true` (content can't be verified). Use `state: absent` with
`name: [foo.container]` (or bare `foo`) to remove; `all: true` removes every installed Quadlet —
dangerous.

## Secrets

Use `podman_secret` to create named secrets, then reference them on the container. Values can
come from a lookup (HashiCorp Vault, Infisical, AWS Secrets Manager, etc.), a vaulted file, or
any Ansible variable — the pattern is the same either way.

```yaml
- become: true
  containers.podman.podman_secret:
    name: myapp-database-url
    data: "{{ myapp_db_password }}"        # from whatever secrets source you use
    state: present
    skip_existing: true
  no_log: true

- become: true
  containers.podman.podman_container:
    name: myapp
    state: quadlet
    quadlet_dir: /etc/containers/systemd
    image: registry.example.com/myapp:latest
    secrets:
      - "myapp-database-url,type=env,target=DATABASE_URL"   # Secret=name,type=env,target=ENVVAR
```

Keep `no_log: true` on any task whose `data:`/`value:` is a real secret. One caveat: the
`Secret=` line is the same string regardless of the secret's current value, so rotating the value
via `podman_secret` does not by itself mark the container Quadlet `changed`. If you want
secret rotation to restart the container, register the `podman_secret` result and include it in
your restart `when`.

## Registry auth

Quadlet pulls from a private registry need an auth file. Two layers:

1. Create/maintain `auth.json` with `containers.podman.podman_login` (or copy a prebuilt one to
   `/etc/containers/auth.json`).
2. Point the Quadlet at it. There is **no first-class Quadlet auth-file param** — emit the
   `[Service] Environment=REGISTRY_AUTH_FILE=…` line via `quadlet_options`:

```yaml
     quadlet_options:
       - "[Service]"
       - "Environment=REGISTRY_AUTH_FILE=/etc/containers/auth.json"
```

## Health checks

Use the module's first-class health params. The module writes `HealthCmd=` / `HealthInterval=` /
etc. into the `[Container]` section:

```yaml
healthcheck: "curl -f http://localhost:{{ port }}{{ health_path }} || exit 1"
healthcheck_interval: 30s
healthcheck_timeout: 5s
healthcheck_retries: 3
healthcheck_start_period: 120s
```

`healthcheck_start_period` is critical for containers that do slow boot work (run migrations,
warm caches, load large models) — give them headroom before the healthcheck can fail the unit.

## Lifecycle, restart-on-change, ordering

- `state: quadlet` writes the file only. It does **not** reload systemd or start the unit. You
  must `daemon_reload: true` then `enabled: true state: started`.
- Restart-on-change: `register` the module result, then `state: restarted` when `result.changed`,
  else `state: started`.
- Inter-unit ordering goes in `quadlet_options` as `[Unit]` lines — there is no first-class param:

```yaml
    quadlet_options:
      - "[Unit]"
      - "After=myapp.service"
      - "Requires=myapp.service"   # optional; stronger than Wants=
```

- `AutoUpdate=registry` is also a `quadlet_options` line, not a param.
- For a pod + its containers, generate the `.pod` Quadlet first (its own `podman_pod state: quadlet`
  task), then containers with `pod: <podname>` so they join it, and order the containers'
  `[Unit]` lines `After=<pod>-pod.service`.

## Idempotency & verification

- The module diffs the generated file content, so `ansible-playbook --check --diff` shows the
  exact unit-file delta before applying. Run this before every Quadlet change.
- `env_file` does **not** track idempotency (per the module docs) — if you depend on an
  EnvironmentFile, template it separately with `copy`/`template` and accept that a change there
  won't by itself recreate/restart the container. Prefer the `env:` dict for values that should
  drive restarts.
- Rootless Quadlets: omit `become` and the module defaults `quadlet_dir` to
  `~/.config/containers/systemd/`. Root Quadlets need `become: true` and
  `/etc/containers/systemd/`.
- A first run against a host that previously had hand-written Quadlets will usually show a
  one-time cosmetic diff (whitespace/ordering) → expect `changed: true` and a restart that once.

## When to hand-template instead

`state: quadlet` is the right default for new and existing Quadlet deployments. Keep a
`copy`/template approach (or `podman_quadlet` Pattern B for raw files) when:

- You need keys the modules genuinely cannot express and `quadlet_options` would dwarf the
  first-class params (rare).
- You're emitting a `.kube` or `.build` Quadlet — there's no generator module for these; install
  raw files with `podman_quadlet` (Pattern B) or template them.
- A host runs Podman too old for Quadlets (pre-4.4) — use `podman_generate_systemd` there.

## Common mistakes

| Mistake | Fix |
| --------- | ----- |
| Using `restart_policy:` expecting the systemd `Restart=` | `restart_policy` maps to `podman run --restart-policy`, ignored under `state: quadlet`. Put `Restart=always` in `quadlet_options` under `[Service]`. |
| Enabling the Quadlet file name, not the unit name | `foo.container` → enable `foo.service`. |
| Forgetting `daemon_reload: true` after writing | `state: quadlet` writes the file only; systemd won't see it until reloaded. |
| Putting `[Unit]`/`[Service]`/`[Install]` lines as params | They have no first-class params — they go in `quadlet_options` as raw lines. |
| `AuthFile=` as a param | No first-class Quadlet auth param. Emit `Environment=REGISTRY_AUTH_FILE=…` under `[Service]` via `quadlet_options`. |
| Committing secret values | Keep `no_log: true` on `podman_secret`; values come from a lookup/vault, not inline literals. |
| Expecting secret rotation to restart the container | It won't — the `Secret=` line is unchanged. Register `podman_secret` and add it to the restart `when`. |
| Skipping `--check --diff` | Run it before every Quadlet change to catch unxpected restarts. |

## Verification commands

```bash
ansible-playbook playbooks/<pb>.yml --check --diff          # dry-run a Quadlet change
ansible-inventory --host <host>                              # inspect host vars feeding the modules

# On the target host, inspect what landed:
ls /etc/containers/systemd/*.container                       # (or ~/.config/containers/systemd/ rootless)
systemctl status <name>.service
podman quadlet list                                          # shows installed Quadlets + resolved unit names
journalctl -u <name>.service -n 50
```

## Reference

Per-module first-class params vs `quadlet_options` raw lines across all Quadlet types:

→ `references/quadlet-params-cheatsheet.md`

A worked, general deployment (pod + network + volume + two containers, with secrets,
health, registry auth, ordering, and restart-on-change):

→ `examples/deploy-quadlets.yml`
