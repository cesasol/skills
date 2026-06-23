# containers.podman Quadlet parameter cheatsheet

Verified against collection `1.20.2` docs. All resource modules below accept
`state: quadlet` and the four `quadlet_*` controls:

| Param               | Type        | Notes                                                                                                                                                |
| ------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `quadlet_dir`       | path        | Default `/etc/containers/systemd/` (root) or `~/.config/containers/systemd/` (rootless). Set explicitly for clarity.                                 |
| `quadlet_filename`  | string      | Defaults to `name`. Output = `<quadlet_filename>.container` (or `.pod`, etc.).                                                                       |
| `quadlet_file_mode` | any         | Octal (quote it: `"0644"`) or symbolic. New files default to `0640` if unset.                                                                        |
| `quadlet_options`   | list/string | Raw lines appended to the file for keys without a first-class param — incl. `[Unit]`, `[Service]`, `[Install]` section headers and their directives. |

## podman_container → `.container`

First-class params → `[Container]` keys (no need for `quadlet_options`):

| Module param | Quadlet key |
| -------------- | ------------- |
| `name` | `ContainerName=` (and the file/unit name) |
| `image` | `Image=` |
| `network` | `Network=` |
| `publish` | `Publish=` |
| `volumes` | `Volume=` |
| `env` (dict) | `Environment=` per key (idempotent — preferred) |
| `env_file` (list/path) | `EnvironmentFile=` (NOT idempotent — see gotchas) |
| `secrets` (list) | `Secret=` (format `name[,opt=…]`, e.g. `s,type=env,target=ENV`) |
| `command` | `Exec=` |
| `entrypoint` | `Entrypoint=` |
| `label` (dict) | `Label=` |
| `cap_add` / `cap_drop` | `AddCapability=` / `DropCapability=` |
| `hostname` | `HostName=` |
| `log_driver` / `log_opt` | `LogDriver=` / `LogOpt=` |
| `healthcheck` | `HealthCmd=` |
| `healthcheck_interval` | `HealthInterval=` |
| `healthcheck_timeout` | `HealthTimeout=` |
| `healthcheck_retries` | `HealthRetries=` |
| `healthcheck_start_period` | `HealthStartPeriod=` |
| `healthcheck_failure_action` | `HealthOnFailure=` |
| `no_hosts: true` | `NoHostAliases=` |
| `read_only: true` | `ReadOnly=` |
| `shm_size` | `ShmSize=` |
| `user` / `group_add` | `User=` / `Group=` |
| `pid` / `ipc` / `userns` / `uts` | `PID=` / `IPC=` / `UserN=` / `UTS=` |
| `mount` | `Mount=` |
| `device` | `AddDevice=` |
| `dns` / `dns_option` / `dns_search` | `DNS=` / `DNSOption=` / `DNSSearch=` |
| `sysctl` | `Sysctl=` |
| `tmpfs` | `Tmpfs=` |
| `security_opt` | `SecurityLabel=`/`ProcOpts=`/`NoNewPrivileges=` |
| `timezone` | `Timezone=` |
| `pod` | `Pod=` (join a pre-generated `<name>.pod` Quadlet) |
| `ip` / `ip6` | `IP=` / `IP6=` |
| `init: true` | `Init=` |

Things with **no** first-class param → must go in `quadlet_options`:

| Directive | Belongs in `quadlet_options` |
| ----------- | ------------------------------ |
| `[Unit] Description=` | yes |
| `[Unit] After=` / `Requires=` / `Wants=` | yes |
| `[Service] Restart=` (systemd) | yes — NOT the module's `restart_policy` param |
| `[Service] TimeoutStartSec=` | yes |
| `[Service] Type=` / `Notify=` | yes |
| `[Service] Environment=REGISTRY_AUTH_FILE=…` (registry auth) | yes |
| `[Service] StandardOutput=` / `StandardError=` | yes |
| `[Service] ExecStartPre=` / `ExecStartPost=` | yes |
| `[Install] WantedBy=` | yes |
| `AutoUpdate=registry` | yes |
| `Pull=` (image pull policy for the Quadlet) | yes, e.g. `Pull=newer` |
| `Notify=` | yes |

## podman_pod → `.pod`

- First-class: `name`, `network` (Network=), `publish` (Publish=), `hostname`, `add_host`, `dns`, `volume` (Volume= for the pod), `share`, `infra`, `infra_image`, `infra_name`, `infra_conmon_pidfile`,
  `share_parent`, `device`, `label`, `subuidname`, `subgidname`, `no_hosts`, `sysctl`, `cgroup_parent`.
- `quadlet_options`: `[Unit]`/`[Service]`/`[Install]` directives, `PodmanArgs=`, `Network=...` aliases, `Volume=...`/`Publish=...` extras, `ExitPropagationPolicy=`.

## podman_network → `.network`

- First-class: `name`, `state`, `subnet`, `gateway`, `ip_range`, `ipv6`, `internal`, `driver`, `label`, `opt`, `interface_name`, `dns`, `rootless`, `subnets`.
- The generated dial-type Quadlet `.network` → unit `<name>-network.service`.
- `quadlet_options`: `[Unit]`/`[Install]`, `DisableDNS=`, `DNS=`, `IPAMDriver=`, `PubIPLinkLocal=`.

## podman_volume → `.volume`

- First-class: `name`, `state`, `driver`, `label`, `options`, `mountpoint`, `device`, `type`, `copy`.
- `.volume` → unit `<name>-volume.service`.
- `quadlet_options`: `[Unit]`/`[Service]`/`[Install]`, `Device=`, `Type=`, `Options=`, `Copy=` (when the module params aren't enough).

## podman_image → `.image`

- First-class: `name` (image reference), `state`, `tag`, `pull`, `arch`, `os`, `tls_verify`, `build` (build args/context/dockerfile), `buildargs`, `cache`, `force`, `validate_certs`.
- `.image` Quadlet pulls/locks an image → unit `<name>-image.service`. Useful for pinning images that multiple containers share; `AutoUpdate=registry` containers reference them by name.
- `quadlet_options`: `[Unit]`/`[Install]`, `ImageTag=` extras, `AllTags=`, `TLSVerify=`, `Arch=`, `OS=` when you need directives the params can't express.

## podman_quadlet (install/remove layer)

| Param | Notes |
| ------- | ------- |
| `state` | `present` / `absent` |
| `src` | file, directory (top-level files only), or URL |
| `files` | extra files installed alongside `src` (quadlet-app use case) |
| `name` | list, used only with `state: absent` (with or without type suffix) |
| `quadlet_dir` | idempotency-check dir only (NOT passed to Podman; defaults follow Podman) |
| `reload_systemd` | default `true` — runs `--reload-systemd` |
| `force` | default `true` — `--force` on removal |
| `all` | `state: absent` + `all: true` removes every Quadlet — dangerous |
| `executable` / `cmd_args` / `debug` | diagnostics |

Behaviors:

- Local file/dir installs: **idempotent** (content comparison via Podman `.app`/`.asset` manifests).
- Remote URL `src`: **always `changed: true`** (can't verify remote content).
- `.quadlets` multi-section bundles (Podman 6+): each section needs a `# FileName=<name>` comment.
- Updates = remove + reinstall (manifest-driven).
