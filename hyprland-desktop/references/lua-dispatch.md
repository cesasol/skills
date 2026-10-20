# Raw Hyprland Dispatch (Lua API, 0.55+)

Since the Lua config landed, `hyprctl dispatch` evaluates `return hl.dispatch(<expr>)`. The old
`hyprctl dispatch movecursor 10 10` form fails with `')' expected`. Pass one Lua expression, quoted for
the shell:

```bash
hyprctl dispatch 'hl.dsp.window.float({ action = "toggle" })'
```

The authoritative list of dispatchers is the stub file shipped with the package:
`/usr/share/hypr/stubs/hl.meta.lua` (search for `HL.Dsp`). The stubs type every argument as `(...)`, so
the shapes below were confirmed against Hyprland 0.56.

## Verified Argument Shapes

| Goal                         | Expression                                                                                                       |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Warp pointer (global)        | `hl.dsp.cursor.move({x=4400, y=800})`                                                                            |
| Focus window                 | `hl.dsp.focus({window="address:0x55ea88e07e00"})`                                                                |
| Focus by direction / monitor | `hl.dsp.focus({direction="left"})`, `hl.dsp.focus({monitor="DP-3"})`                                             |
| Key to a window, no focus    | `hl.dsp.send_shortcut({mods="CTRL SHIFT", key="t", window="address:0x..."})`                                     |
| Key down/up/repeat           | `hl.dsp.send_key_state({mods="", key="a", state="down"})`                                                        |
| Run a program                | `hl.dsp.exec_cmd("kitty")`                                                                                       |
| Run on a workspace, silently | `hl.dsp.exec_cmd("kitty", {workspace="20 silent"})`                                                              |
| Close politely               | `hl.dsp.window.close({window="address:0x..."})`                                                                  |
| Move to workspace            | `hl.dsp.window.move({workspace="5", window="address:0x..."})`                                                    |
| Move in a direction          | `hl.dsp.window.move({direction="l"})`                                                                            |
| Resize (pixels)              | `hl.dsp.window.resize({x=1200, y=800, relative=false})`                                                          |
| Float / fullscreen / pin     | `hl.dsp.window.float({action="toggle"})`, `hl.dsp.window.fullscreen({mode="fullscreen"})`, `hl.dsp.window.pin()` |
| Special workspace            | `hl.dsp.workspace.toggle_special("social")`                                                                      |
| Show workspace N             | `hl.dsp.focus({workspace=14})` (switches the monitor that owns N and focuses it)                                 |
| Clear maximize / fullscreen  | `hl.dsp.window.fullscreen_state({internal=0, client=0})`                                                         |
| Toggle fullscreen / maximize | `hl.dsp.window.fullscreen({mode="fullscreen"})` or `mode="maximized"`                                            |

`resize`, `move` (`x`/`y`), `float`, and `fullscreen*` act on the **active** window. Focus the target
first, and refocus the user's window afterward. `resize` and `move` are refused with
`Window is fullscreen` on a maximized window; clear that state first.

`exec_cmd` rules: `workspace="N silent"` and `float=true` apply. `size="W H"` returns `ok` and is
ignored, so resize after the window maps.

A floating window moved to coordinates on another monitor renders there but keeps its original
workspace. `hyprctl -j clients` still reports the old `monitor` id.

`focus` accepts exactly one of `direction`, `monitor`, `window`, `workspace`, `urgent_or_last`, `last`. `window.move`
accepts one of `direction`, `x`+`y` (`relative`), `workspace`, `into_group`, `out_of_group`.

## Traps

- **`ok` is not success.** Nonexistent addresses, unknown keys inside the table, and selectors that
  match nothing all return `ok` and do nothing. Re-query `hyprctl -j clients` / `activewindow` to confirm.
- **Unknown arguments may still act.** `toggle_special({bogus=1})` returned `ok` and opened the
  default `special:special` workspace. Never probe a dispatcher with made-up arguments on a live
  session. Read the stub, or call it with no table and read the `'x' is required` error.
- **Errors that name arguments are safe to provoke.** A missing required field is rejected before
  anything runs. For example, `hl.dsp.cursor.move({})` prints `'x' is required`.
- **Special workspaces:** `exec_cmd(cmd, {workspace="special:NAME silent"})` creates and fills one
  hidden. `window.move({workspace="special:NAME", follow=false, window="address:0x..."})` moves in
  or out without touching focus. Omitting `follow=false` switches the monitor and steals focus.
  `toggle_special` has no monitor argument: run `focus({monitor="M"})` first. While a special
  workspace is shown, focusing a window on that monitor's regular workspace hides it. Focusing
  windows on other monitors does not. A `workspace_rule` with `monitor = ...` for a special
  workspace does **not** stop `toggle_special` from opening it on the focused monitor; read the
  pin from `hyprctl -j workspacerules` (`workspaceString`, `monitor`) and focus that monitor first.
- **On-screen notifications:** `hyprctl notify ICON MS COLOR TEXT` (ICON -1..5, COLOR like
  `rgb(61afef)`) and `hyprctl dismissnotify`. They render top-right on the focused monitor, and
  grim captures them.
- **Workspace-relative dispatchers act on the focused monitor.** `toggle_special` shows the workspace
  on whichever monitor has focus, not where it was last shown.
- **`wl-copy` never exits while it owns the clipboard.** Run from an agent shell with captured
  output, it holds the session open, and killing that session wipes the clipboard. Use the helper's
  `paste`, or `setsid -f wl-copy < file >/dev/null 2>&1`.
- **`pkill -f PATTERN` matches its own shell** when the pattern appears in the command line. Use
  `pkill -f '[h]yprdesk'`.
- The user's config may wrap workspace binds through a plugin module, such as `smw.lua` for
  split-monitor-workspaces. Read `~/.config/hypr/*.lua` before assuming workspace numbers map 1:1.

## Read-Only Queries

`hyprctl -j <what>` still uses the classic request names. Each is safe to call at any time:

| Request        | Use                                                            |
| -------------- | -------------------------------------------------------------- |
| `monitors`     | Geometry, scale, transform, active and special workspace       |
| `clients`      | Every window: `address`, `class`, `title`, `at`, `size`, `pid` |
| `activewindow` | The focused window                                             |
| `workspaces`   | Workspace names, monitors, window counts                       |
| `layers`       | Bars, notifications, launchers (layer-shell surfaces)          |
| `devices`      | Keyboards (layout, active keymap) and pointers                 |
| `cursorpos`    | Plain `x, y` text, not JSON                                    |
| `binds`        | The user's keybindings, useful to discover app shortcuts       |
