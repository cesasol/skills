#!/usr/bin/env python3
"""Drive a Hyprland (Lua-config era, 0.55+) desktop for an agent.

Coordinates are always GLOBAL LOGICAL pixels (the space `hyprctl` reports for
monitors, windows and the cursor) unless `--image` is passed, in which case the
pair is read as pixels in the most recent `shot` image and mapped back through
that shot's origin and scale.

Dependencies: hyprctl, jq-free (JSON parsed here), grim, ydotool + ydotoold,
optional tesseract (find-text) and wl-clipboard (paste).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

Json = dict[str, Any]

STATE_DIR = Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}") / "hyprdesk"
LAST_SHOT = STATE_DIR / "last-shot.json"
ORIGINS = STATE_DIR / "origins.json"
AGENT_WS = f"special:{os.environ.get('HYPRDESK_WORKSPACE', 'agent')}"
FEEDBACK = os.environ.get("HYPRDESK_FEEDBACK", "on").lower() not in ("0", "off", "false", "no")
FEEDBACK_UNTIL = STATE_DIR / "feedback-until"
FEEDBACK_STYLE = {"look": ("1", "rgb(61afef)", 1200), "act": ("2", "rgb(e5c07b)", 1500),
                  "window": ("5", "rgb(98c379)", 1500), "warn": ("0", "rgb(e06c75)", 5000)}
DEFAULT_MAX_EDGE = 1568  # long edge most vision models see without resampling

BUTTONS = {"left": 0x00, "right": 0x01, "middle": 0x02, "back": 0x06, "forward": 0x05}
MOUSE_DOWN = 0x40
MOUSE_UP = 0x80

# US-layout keysyms for ASCII characters sent through send_shortcut.
UNSHIFTED = {
    " ": "space", "`": "grave", "-": "minus", "=": "equal", "[": "bracketleft",
    "]": "bracketright", "\\": "backslash", ";": "semicolon", "'": "apostrophe",
    ",": "comma", ".": "period", "/": "slash", "\n": "Return", "\t": "Tab",
}
SHIFTED = dict(zip('~!@#$%^&*()_+{}|:"<>?', "`1234567890-=[]\\;',./"))
MOD_ALIASES = {
    "CTRL": "CTRL", "CONTROL": "CTRL", "SHIFT": "SHIFT", "ALT": "ALT",
    "SUPER": "SUPER", "META": "SUPER", "WIN": "SUPER", "MOD4": "SUPER",
}


class DeskError(RuntimeError):
    pass




def lua_str(value: str) -> str:
    out: list[str] = ['"']
    for ch in value:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.append(f"\\{ord(ch):03d}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def parse_combo(combo: str) -> tuple[str, str]:
    parts = [p for p in re.split(r"[+\s]+", combo.strip()) if p]
    if not parts:
        raise DeskError("empty key combo")
    *mods, key = parts
    norm = []
    for mod in mods:
        alias = MOD_ALIASES.get(mod.upper())
        if alias is None:
            raise DeskError(f"unknown modifier {mod!r}; use CTRL, SHIFT, ALT, SUPER")
        norm.append(alias)
    return " ".join(norm), key


def char_to_shortcut(ch: str) -> tuple[str, str]:
    if ch.isascii() and ch.isalnum():
        return ("SHIFT", ch.lower()) if ch.isupper() else ("", ch)
    if ch in UNSHIFTED:
        return "", UNSHIFTED[ch]
    if ch in SHIFTED:
        base = SHIFTED[ch]
        return "SHIFT", UNSHIFTED.get(base, base)
    raise DeskError(f"cannot send {ch!r} as a key; use `paste` for non-ASCII text")


def logical_rect(mon: Json) -> tuple[int, int, int, int]:
    w, h = mon["width"], mon["height"]
    if mon.get("transform", 0) % 2 == 1:
        w, h = h, w
    scale = mon.get("scale", 1) or 1
    return mon["x"], mon["y"], round(w / scale), round(h / scale)


def image_to_global(meta: Json, px: float, py: float) -> tuple[int, int]:
    if not (0 <= px <= meta["img_w"] and 0 <= py <= meta["img_h"]):
        raise DeskError(f"({px}, {py}) is outside the {meta['img_w']}x{meta['img_h']} shot")
    return round(meta["x"] + px / meta["scale"]), round(meta["y"] + py / meta["scale"])


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise DeskError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def monitor_at(mons: list[Json], x: int, y: int) -> Json | None:
    for mon in mons:
        mx, my, mw, mh = logical_rect(mon)
        if mx <= x < mx + mw and my <= y < my + mh:
            return mon
    return None


def require_on_screen(mons: list[Json], x: int, y: int) -> str:
    mon = monitor_at(mons, x, y)
    if mon is None:
        layout = ", ".join(f"{m['name']}={logical_rect(m)}" for m in mons)
        raise DeskError(f"({x}, {y}) is not on any monitor (gap or off-screen); monitors: {layout}")
    return mon["name"]


def run(cmd: list[str], *, input_text: str | None = None) -> str:
    proc = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
    if proc.returncode != 0:
        raise DeskError(f"{cmd[0]} failed ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout


def hypr_json(what: str) -> Any:
    return json.loads(run(["hyprctl", "-j", what]))


def dispatch(lua_expr: str) -> None:
    """Run one `hl.dsp.*` dispatcher. 'ok' only means it parsed, not that it acted."""
    out = run(["hyprctl", "dispatch", lua_expr]).strip()
    if out != "ok":
        raise DeskError(f"dispatch {lua_expr!r}: {out}")


def monitors() -> list[Json]:
    return hypr_json("monitors")


def clients() -> list[Json]:
    return hypr_json("clients")


def visible_workspace_ids() -> set[int]:
    ids: set[int] = set()
    for mon in monitors():
        ids.add(mon["activeWorkspace"]["id"])
        if mon.get("specialWorkspace", {}).get("id"):
            ids.add(mon["specialWorkspace"]["id"])
    return ids


def resolve_window(selector: str) -> Json:
    """Resolve an address (0x...), 'class=substr', 'title=substr', or 'active'."""
    if selector == "active":
        win = hypr_json("activewindow")
        if not win:
            raise DeskError("no active window")
        return win
    wins = [w for w in clients() if w.get("mapped", True)]
    if selector.startswith("0x"):
        matches = [w for w in wins if w["address"] == selector]
    else:
        field, sep, needle = selector.partition("=")
        if not sep or field not in ("class", "title"):
            raise DeskError("window selector must be 0xADDR, class=..., title=... or active")
        matches = [w for w in wins if needle.lower() in w[field].lower()]
    if len(matches) != 1:
        found = ", ".join(f"{w['address']} [{w['class']}] {w['title'][:40]!r}" for w in matches)
        raise DeskError(f"selector {selector!r} matched {len(matches)} windows: {found or 'none'}")
    return matches[0]


def ancestor_pids(pid: int | None = None) -> set[int]:
    chain: set[int] = set()
    current = pid or os.getpid()
    while current > 1 and current not in chain:
        chain.add(current)
        try:
            stat = Path(f"/proc/{current}/stat").read_text()
        except OSError:
            break
        current = int(stat.rsplit(")", 1)[1].split()[1])
    return chain


def feedback(kind: str, text: str) -> None:
    if not FEEDBACK:
        return
    icon, color, ms = FEEDBACK_STYLE[kind]
    proc = subprocess.run(["hyprctl", "notify", icon, str(ms), color, f"[agent] {text}"],
                          capture_output=True, text=True)
    if proc.returncode != 0 or proc.stdout.strip() != "ok":
        print(f"hyprdesk: feedback notification failed: {proc.stdout.strip() or proc.stderr.strip()}",
              file=sys.stderr)
        return
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _ = FEEDBACK_UNTIL.write_text(str(time.time() + ms / 1000))


def clear_feedback() -> None:
    try:
        until = float(FEEDBACK_UNTIL.read_text())
    except (OSError, ValueError):
        return
    FEEDBACK_UNTIL.unlink(missing_ok=True)
    if time.time() < until:
        _ = run(["hyprctl", "dismissnotify"])
        time.sleep(0.08)  # let the compositor render a frame without the notification


def keyboard_target(selector: str | None, action: str) -> str:
    win = resolve_window(selector or "active")
    if win["pid"] in ancestor_pids():
        raise DeskError(
            f"refusing keyboard input to {win['address']} [{win['class']}]: it hosts this agent "
            "(its pid is an ancestor of this process); focus or name another window"
        )
    feedback("act", f"{action} -> {win['class']}{'' if selector else ' (focused)'}")
    return win["address"]


def ensure_ydotoold() -> None:
    sock = os.environ.get("YDOTOOL_SOCKET") or f"/run/user/{os.getuid()}/.ydotool_socket"
    if Path(sock).exists():
        return
    if shutil.which("systemctl"):
        subprocess.run(["systemctl", "--user", "start", "ydotool.service"], capture_output=True)
        for _ in range(20):
            if Path(sock).exists():
                return
            time.sleep(0.05)
    raise DeskError(
        "ydotoold is not running; start it with `systemctl --user start ydotool` "
        "(needs rw access to /dev/uinput)"
    )


def ydotool(*args: str, input_text: str | None = None) -> None:
    ensure_ydotoold()
    run(["ydotool", *args], input_text=input_text)


def move_cursor(x: int, y: int) -> None:
    dispatch(f"hl.dsp.cursor.move({{x={x}, y={y}}})")


def send_shortcut(mods: str, key: str, address: str | None) -> None:
    target = f", window={lua_str('address:' + address)}" if address else ""
    dispatch(f"hl.dsp.send_shortcut({{mods={lua_str(mods)}, key={lua_str(key)}{target}}})")




def target_rect(args: argparse.Namespace) -> tuple[tuple[int, int, int, int], str]:
    if args.region:
        x, y, w, h = (int(v) for v in re.split(r"[,x\s]+", args.region.strip()))
        return (x, y, w, h), f"region {x},{y} {w}x{h}"
    if args.window:
        win = resolve_window(args.window)
        if win["workspace"]["id"] not in visible_workspace_ids():
            raise DeskError(
                f"window {win['address']} is on hidden workspace {win['workspace']['name']}; "
                "grim only captures what is on screen - focus it first"
            )
        (x, y), (w, h) = win["at"], win["size"]
        return (x, y, w, h), f"window {win['address']} [{win['class']}]"
    mons = monitors()
    if args.all:
        rects = [logical_rect(m) for m in mons]
        x0, y0 = min(r[0] for r in rects), min(r[1] for r in rects)
        x1, y1 = max(r[0] + r[2] for r in rects), max(r[1] + r[3] for r in rects)
        return (x0, y0, x1 - x0, y1 - y0), "all monitors"
    if args.monitor:
        mon = next((m for m in mons if m["name"] == args.monitor), None)
        if mon is None:
            raise DeskError(f"no monitor {args.monitor!r}; have {[m['name'] for m in mons]}")
    else:
        mon = next((m for m in mons if m["focused"]), mons[0])
    return logical_rect(mon), f"monitor {mon['name']}"


def capture(args: argparse.Namespace, *, scale: float | None) -> Json:
    (x, y, w, h), label = target_rect(args)
    clear_feedback()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if getattr(args, "out", None) else STATE_DIR / f"shot-{int(time.time() * 1000)}.png"
    cmd = ["grim", "-g", f"{x},{y} {w}x{h}"]
    if scale is not None:
        cmd += ["-s", f"{scale:.4f}"]
    run([*cmd, str(out)])
    img_w, img_h = png_size(out)
    meta = {"path": str(out), "target": label, "x": x, "y": y, "w": w, "h": h,
            "img_w": img_w, "img_h": img_h, "scale": img_w / w}
    return meta


def cmd_shot(args: argparse.Namespace) -> Json:
    (_, _, w, h), _ = target_rect(args)
    scale = min(1.0, args.max / max(w, h)) if args.max else 1.0
    meta = capture(args, scale=scale)
    if args.all:
        meta["monitors"] = {m["name"]: logical_rect(m) for m in monitors()}
        meta["note"] = "areas outside every monitor rect are black gaps; points there are rejected"
    LAST_SHOT.write_text(json.dumps(meta))
    return meta


def load_last_shot() -> Json:
    if not LAST_SHOT.exists():
        raise DeskError("no shot yet; run `hyprdesk shot` before using --image")
    return json.loads(LAST_SHOT.read_text())


def point(args: argparse.Namespace, x: float, y: float) -> tuple[int, int, str]:
    gx, gy = image_to_global(load_last_shot(), x, y) if args.image else (round(x), round(y))
    return gx, gy, require_on_screen(monitors(), gx, gy)


def window_summary(w: Json, visible: set[int], active: str | None) -> Json:
    mon_names = {m["id"]: m["name"] for m in monitors()}
    return {"address": w["address"], "class": w["class"], "title": w["title"],
            "workspace": w["workspace"]["name"], "monitor": mon_names.get(w["monitor"]),
            "at": w["at"], "size": w["size"],
            "floating": w["floating"], "visible": w["workspace"]["id"] in visible,
            "focused": w["address"] == active, "pid": w["pid"],
            "self": w["pid"] in ancestor_pids()}


def cmd_state(_args: argparse.Namespace) -> Json:
    vis = visible_workspace_ids()
    active = (hypr_json("activewindow") or {}).get("address")
    cx, cy = (int(v) for v in run(["hyprctl", "cursorpos"]).split(","))
    return {
        "monitors": [{"name": m["name"], "focused": m["focused"], "rect": logical_rect(m),
                      "scale": m["scale"], "workspace": m["activeWorkspace"]["name"],
                      "special": m.get("specialWorkspace", {}).get("name") or None}
                     for m in monitors()],
        "cursor": [cx, cy],
        "active": active,
        "windows": [window_summary(w, vis, active) for w in clients() if w.get("mapped", True)],
        "agent": agent_status(),
    }


def cmd_find_text(args: argparse.Namespace) -> Json:
    if not shutil.which("tesseract"):
        raise DeskError("tesseract is not installed")
    meta = capture(args, scale=None)  # native resolution reads best
    langs = [l.strip() for l in run(["tesseract", "--list-langs"]).splitlines()[1:]]
    lang = args.lang or ("eng" if "eng" in langs else "+".join(l for l in langs if l != "osd"))
    if not lang:
        raise DeskError("no tesseract language data installed (pacman -S tesseract-data-eng)")
    tsv = run(["tesseract", meta["path"], "-", "-l", lang, "--psm", "11", "tsv"])
    lines: dict[tuple[str, ...], list[Json]] = {}
    for row in tsv.splitlines()[1:]:
        cols = row.split("\t")
        if len(cols) < 12 or not cols[11].strip() or float(cols[10]) < 0:
            continue
        key = tuple(cols[1:5])
        lines.setdefault(key, []).append({"text": cols[11], "conf": float(cols[10]),
                                          "box": [int(c) for c in cols[6:10]]})
    needle = args.text.lower().split()
    matches: list[Json] = []
    for words in lines.values():
        low = [w["text"].lower() for w in words]
        for i in range(len(low) - len(needle) + 1):
            window = low[i:i + len(needle)]
            hit = window == needle if args.exact else all(n in t for n, t in zip(needle, window))
            if not hit:
                continue
            span = words[i:i + len(needle)]
            left = min(w["box"][0] for w in span)
            top = min(w["box"][1] for w in span)
            right = max(w["box"][0] + w["box"][2] for w in span)
            bottom = max(w["box"][1] + w["box"][3] for w in span)
            cx, cy = image_to_global(meta, (left + right) / 2, (top + bottom) / 2)
            matches.append({"text": " ".join(w["text"] for w in span), "x": cx, "y": cy,
                            "conf": round(min(w["conf"] for w in span), 1)})
    os.unlink(meta["path"])
    return {"lang": lang, "target": meta["target"], "matches": matches}


def cmd_move(args: argparse.Namespace) -> Json:
    x, y, mon = point(args, args.x, args.y)
    feedback("act", f"pointer to {x},{y} on {mon}")
    move_cursor(x, y)
    return {"cursor": [x, y], "monitor": mon}


def cmd_click(args: argparse.Namespace) -> Json:
    x, y, mon = point(args, args.x, args.y)
    feedback("act", f"{args.button} click{' x' + str(args.count) if args.count > 1 else ''} at {x},{y} on {mon}")
    move_cursor(x, y)
    code = f"0x{BUTTONS[args.button] | MOUSE_DOWN | MOUSE_UP:02X}"
    ydotool("click", "-r", str(args.count), "-D", "60", code)
    return {"clicked": [x, y], "monitor": mon, "button": args.button, "count": args.count}


def cmd_drag(args: argparse.Namespace) -> Json:
    x1, y1, mon1 = point(args, args.x1, args.y1)
    x2, y2, mon2 = point(args, args.x2, args.y2)
    feedback("act", f"drag {x1},{y1} -> {x2},{y2}")
    move_cursor(x1, y1)
    ydotool("click", f"0x{BUTTONS['left'] | MOUSE_DOWN:02X}")
    try:
        for step in range(1, args.steps + 1):
            t = step / args.steps
            move_cursor(round(x1 + (x2 - x1) * t), round(y1 + (y2 - y1) * t))
            time.sleep(0.016)
    finally:
        ydotool("click", f"0x{BUTTONS['left'] | MOUSE_UP:02X}")
    return {"dragged": [[x1, y1], [x2, y2]], "monitors": [mon1, mon2]}


def cmd_scroll(args: argparse.Namespace) -> Json:
    x, y, mon = point(args, args.x, args.y)
    feedback("act", f"scroll {'down' if args.down >= 0 else 'up'} at {x},{y} on {mon}")
    move_cursor(x, y)
    # evdev REL_WHEEL: positive is away from the user (content moves toward start).
    ydotool("mousemove", "-w", "-x", str(-args.right), "-y", str(-args.down))
    return {"scrolled_at": [x, y], "monitor": mon, "down": args.down, "right": args.right}


def cmd_type(args: argparse.Namespace) -> Json:
    address = keyboard_target(args.window, f"typing {len(args.text)} chars")
    if args.window:
        for ch in args.text:
            mods, key = char_to_shortcut(ch)
            send_shortcut(mods, key, address)
        return {"typed": len(args.text), "window": address, "delivery": "background"}
    ydotool("type", "-d", "8", "-H", "8", "-f", "-", input_text=args.text)
    return {"typed": len(args.text), "window": address, "delivery": "focused"}


def cmd_key(args: argparse.Namespace) -> Json:
    target = keyboard_target(args.window, "keys " + " ".join(args.combo))
    address = target if args.window else None
    for combo in args.combo:
        mods, key = parse_combo(combo)
        send_shortcut(mods, key, address)
    return {"keys": args.combo, "window": address or "focused"}


def cmd_paste(args: argparse.Namespace) -> Json:
    target = keyboard_target(args.window, f"pasting {len(args.text)} chars")
    address = target if args.window else None
    # wl-copy forks a server that keeps any captured pipe open, so never capture its output.
    if subprocess.run(["wl-copy"], input=args.text, text=True, stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode != 0:
        raise DeskError("wl-copy failed")
    mods = "CTRL SHIFT" if args.terminal else "CTRL"
    send_shortcut(mods, "v", address)
    return {"pasted": len(args.text), "window": address or "focused", "clipboard": "overwritten"}


def cmd_focus(args: argparse.Namespace) -> Json:
    win = resolve_window(args.window)
    dispatch(f"hl.dsp.focus({{window={lua_str('address:' + win['address'])}}})")
    for _ in range(20):
        if hypr_json("activewindow").get("address") == win["address"]:
            return {"focused": win["address"], "workspace": win["workspace"]["name"]}
        time.sleep(0.05)
    raise DeskError(f"focus did not land on {win['address']}")


def cmd_close(args: argparse.Namespace) -> Json:
    win = resolve_window(args.window)
    dispatch(f"hl.dsp.window.close({{window={lua_str('address:' + win['address'])}}})")
    for _ in range(40):
        if all(w["address"] != win["address"] for w in clients()):
            return {"closed": win["address"]}
        time.sleep(0.05)
    return {"close_requested": win["address"], "still_open": True,
            "hint": "the app may be showing a save/confirm dialog; take a shot"}


def cmd_shape(args: argparse.Namespace) -> Json:
    win = resolve_window(args.window)
    if win["pid"] in ancestor_pids():
        raise DeskError("refusing to reshape the window hosting this agent")
    previous = (hypr_json("activewindow") or {}).get("address")
    w, h = (int(v) for v in args.size.lower().split("x"))
    mons = monitors()
    mon = next((m for m in mons if m["name"] == args.monitor), None) if args.monitor else None
    if args.monitor and mon is None:
        raise DeskError(f"no monitor {args.monitor!r}; have {[m['name'] for m in mons]}")
    _ = cmd_focus(argparse.Namespace(window=win["address"]))
    if win["fullscreen"]:
        dispatch("hl.dsp.window.fullscreen_state({internal=0, client=0})")
    if not win["floating"]:
        dispatch('hl.dsp.window.float({action="toggle"})')
    dispatch(f"hl.dsp.window.resize({{x={w}, y={h}, relative=false}})")
    if mon is not None:
        mx, my, mw, mh = logical_rect(mon)
        dispatch(f"hl.dsp.window.move({{x={mx + max(0, (mw - w) // 2)}, y={my + max(0, (mh - h) // 2)}}})")
    time.sleep(0.2)
    after = resolve_window(win["address"])
    if previous and previous != win["address"]:
        _ = cmd_focus(argparse.Namespace(window=previous))
    if after["size"] != [w, h]:
        raise DeskError(f"asked for {w}x{h}, window is {after['size']} (min-size rule or app constraint?)")
    landed = monitor_at(mons, *after["at"])
    return {"shaped": win["address"], "at": after["at"], "size": after["size"],
            "monitor": landed["name"] if landed else None, "refocused": previous}


def pick_agent_monitor(mons: list[Json], self_monitors: set[str], user_monitor: str | None) -> Json:
    def rank(m: Json) -> tuple[bool, bool, bool]:
        return (m["name"] == user_monitor, m["name"] in self_monitors, m.get("scale", 1) != 1)
    return sorted(mons, key=rank)[0]


def agent_status() -> Json:
    wins = [w for w in clients() if w["workspace"]["name"] == AGENT_WS]
    shown = [m["name"] for m in monitors() if m.get("specialWorkspace", {}).get("name") == AGENT_WS]
    origins = json.loads(ORIGINS.read_text()) if ORIGINS.exists() else {}
    return {"workspace": AGENT_WS, "shown_on": shown[0] if shown else None,
            "windows": [{"address": w["address"], "class": w["class"], "title": w["title"],
                         "origin": origins.get(w["address"])} for w in wins]}


def save_origins(origins: dict[str, str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _ = ORIGINS.write_text(json.dumps(origins))


def move_silent(address: str, workspace: str) -> None:
    dispatch(f"hl.dsp.window.move({{workspace={lua_str(workspace)}, follow=false, "
             f"window={lua_str('address:' + address)}}})")
    for _ in range(20):
        if resolve_window(address)["workspace"]["name"] == workspace:
            return
        time.sleep(0.05)
    raise DeskError(f"{address} did not move to {workspace}")


def cmd_adopt(args: argparse.Namespace) -> Json:
    win = resolve_window(args.window)
    if win["pid"] in ancestor_pids():
        raise DeskError("refusing to adopt the window hosting this agent")
    origins: dict[str, str] = json.loads(ORIGINS.read_text()) if ORIGINS.exists() else {}
    if win["workspace"]["name"] != AGENT_WS:
        _ = origins.setdefault(win["address"], win["workspace"]["name"])
        save_origins(origins)
        move_silent(win["address"], AGENT_WS)
    return {"adopted": win["address"], "origin": origins.get(win["address"]), "agent": agent_status()}


def cmd_release(args: argparse.Namespace) -> Json:
    origins: dict[str, str] = json.loads(ORIGINS.read_text()) if ORIGINS.exists() else {}
    if args.window:
        targets = [resolve_window(args.window)["address"]]
    else:
        targets = list(origins)
    released, gone = [], []
    for address in targets:
        if address not in origins:
            raise DeskError(f"{address} was not adopted (launched in {AGENT_WS}?); close it or move it by hand")
        try:
            move_silent(address, origins[address])
            released.append({"address": address, "workspace": origins[address]})
        except DeskError:
            if any(w["address"] == address for w in clients()):
                raise
            gone.append(address)
        del origins[address]
    save_origins(origins)
    return {"released": released, "already_closed": gone, "agent": agent_status()}


def toggle_agent_on(monitor_name: str) -> None:
    dispatch(f"hl.dsp.focus({{monitor={lua_str(monitor_name)}}})")
    dispatch(f"hl.dsp.workspace.toggle_special({lua_str(AGENT_WS.removeprefix('special:'))})")


def pinned_monitor(rules: list[Json], mons: list[Json]) -> str | None:
    for rule in rules:
        target = rule.get("monitor") or ""
        if rule.get("workspaceString") != AGENT_WS or not rule.get("enabled", True) or not target:
            continue
        for mon in mons:
            if target == mon["name"] or (target.startswith("desc:")
                                         and mon.get("description", "").startswith(target[5:])):
                return mon["name"]
    return None


def cmd_stage(args: argparse.Namespace) -> Json:
    status = agent_status()
    if not status["windows"]:
        raise DeskError(f"{AGENT_WS} is empty; `launch` or `adopt` a window first")
    mons = monitors()
    active = hypr_json("activewindow") or {}
    previous = active.get("address")
    mon_names = {m["id"]: m["name"] for m in mons}
    user_monitor = mon_names.get(active.get("monitor", -1)) if previous else None
    pinned = pinned_monitor(hypr_json("workspacerules"), mons)
    if pinned and args.monitor and args.monitor != pinned:
        raise DeskError(f"{AGENT_WS} is pinned to {pinned} by a workspace rule; drop --monitor or edit the rule")
    if pinned and not args.monitor:
        args.monitor = pinned
    if args.monitor:
        found = next((m for m in mons if m["name"] == args.monitor), None)
        if found is None:
            raise DeskError(f"no monitor {args.monitor!r}; have {[m['name'] for m in mons]}")
        mon = found
    else:
        selves = {mon_names.get(w["monitor"], "") for w in clients() if w["pid"] in ancestor_pids()}
        mon = pick_agent_monitor(mons, selves, user_monitor)
    if status["shown_on"] == mon["name"]:
        return {"staged_on": mon["name"], "changed": False, "agent": status}
    toggle_agent_on(mon["name"])
    # Focusing a regular-workspace window on the same monitor would hide the overlay again.
    covers_user = user_monitor == mon["name"]
    if previous and not covers_user:
        _ = cmd_focus(argparse.Namespace(window=previous))
    status = agent_status()
    if status["shown_on"] != mon["name"]:
        raise DeskError(f"{AGENT_WS} is shown on {status['shown_on']}, expected {mon['name']}")
    result: Json = {"staged_on": mon["name"], "changed": True, "refocused": None if covers_user else previous,
                    "agent": status}
    if covers_user:
        result["warning"] = (f"staged over the user's active window {previous} on {mon['name']}; "
                             "their focus moved to the agent workspace. Tell the user, and unstage soon")
    return result


def cmd_unstage(_args: argparse.Namespace) -> Json:
    status = agent_status()
    if status["shown_on"] is None:
        return {"hidden": True, "changed": False}
    previous = (hypr_json("activewindow") or {}).get("address")
    if previous in {w["address"] for w in status["windows"]}:
        previous = None
    toggle_agent_on(status["shown_on"])
    status = agent_status()
    if previous:
        _ = cmd_focus(argparse.Namespace(window=previous))
    if status["shown_on"] is not None:
        raise DeskError(f"{AGENT_WS} is still shown on {status['shown_on']}")
    return {"hidden": True, "changed": True, "refocused": previous}


def cmd_launch(args: argparse.Namespace) -> Json:
    before = {w["address"] for w in clients()}
    workspace = args.workspace or f"{AGENT_WS} silent"
    rules = f", {{workspace={lua_str(workspace)}}}"
    dispatch(f"hl.dsp.exec_cmd({lua_str(args.command)}{rules})")
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        new = [w for w in clients() if w["address"] not in before]
        if new:
            vis = visible_workspace_ids()
            active = (hypr_json("activewindow") or {}).get("address")
            return {"windows": [window_summary(w, vis, active) for w in new]}
        time.sleep(0.1)
    raise DeskError(f"no new window within {args.timeout}s (it may reuse an existing instance)")


def cmd_wait_window(args: argparse.Namespace) -> Json:
    deadline = time.monotonic() + args.timeout
    last_err = ""
    while time.monotonic() < deadline:
        try:
            win = resolve_window(args.window)
            return {"address": win["address"], "class": win["class"], "title": win["title"]}
        except DeskError as err:
            last_err = str(err)
        time.sleep(0.1)
    raise DeskError(f"timed out: {last_err}")


SESSION_VARS = ("XDG_CURRENT_DESKTOP", "XDG_SESSION_DESKTOP", "DESKTOP_SESSION", "XDG_SESSION_TYPE",
                "XDG_BACKEND", "WAYLAND_DISPLAY", "DISPLAY", "HYPRLAND_INSTANCE_SIGNATURE")

PACKAGES: dict[str, dict[str, str]] = {
    "hyprctl": {"pacman": "hyprland", "apt": "hyprland", "dnf": "hyprland", "zypper": "hyprland"},
    "grim": {"pacman": "grim", "apt": "grim", "dnf": "grim", "zypper": "grim"},
    "ydotool": {"pacman": "ydotool", "apt": "ydotool", "dnf": "ydotool", "zypper": "ydotool"},
    "wl-clipboard": {"pacman": "wl-clipboard", "apt": "wl-clipboard", "dnf": "wl-clipboard",
                     "zypper": "wl-clipboard"},
    "tesseract": {"pacman": "tesseract", "apt": "tesseract-ocr", "dnf": "tesseract",
                  "zypper": "tesseract-ocr"},
    "tesseract-eng": {"pacman": "tesseract-data-eng", "apt": "tesseract-ocr-eng",
                      "dnf": "tesseract-langpack-eng", "zypper": "tesseract-ocr-traineddata-english"},
}
INSTALL_PREFIX = {"pacman": "sudo pacman -S --needed", "apt": "sudo apt install",
                  "dnf": "sudo dnf install", "zypper": "sudo zypper install"}
UINPUT_RULE = 'KERNEL=="uinput", GROUP="input", MODE="0660", TAG+="uaccess", OPTIONS+="static_node=uinput"'


def choose_instance(instances: list[Json], alive: set[int]) -> Json | None:
    live = [i for i in instances if i.get("pid") in alive]
    if len(live) > 1:
        raise DeskError("several Hyprland instances are running (" + ", ".join(i["instance"] for i in live)
                        + "); export HYPRLAND_INSTANCE_SIGNATURE and WAYLAND_DISPLAY for the right one")
    return live[0] if live else None


def adopt_session() -> Json | None:
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE") and os.environ.get("WAYLAND_DISPLAY"):
        return None
    named = [d.lower() for d in re.split(r"[:;]", os.environ.get("XDG_CURRENT_DESKTOP", "")) if d]
    if named and "hyprland" not in named:
        return None
    if not shutil.which("hyprctl"):
        return None
    _ = os.environ.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    proc = subprocess.run(["hyprctl", "instances", "-j"], capture_output=True, text=True)
    try:
        instances = json.loads(proc.stdout) if proc.returncode == 0 else []
    except json.JSONDecodeError:
        instances = []
    alive = {i["pid"] for i in instances if Path(f"/proc/{i.get('pid')}").exists()}
    chosen = choose_instance(instances, alive)
    if chosen is None:
        return None
    adopted = {"HYPRLAND_INSTANCE_SIGNATURE": chosen["instance"]}
    if chosen.get("wl_socket"):
        adopted["WAYLAND_DISPLAY"] = chosen["wl_socket"]
    for key, value in adopted.items():
        _ = os.environ.setdefault(key, value)
    return adopted


def detect_session(env: dict[str, str]) -> Json:
    desktops = [d for d in re.split(r"[:;]", env.get("XDG_CURRENT_DESKTOP", "")) if d]
    desktops += [env[k] for k in ("XDG_SESSION_DESKTOP", "DESKTOP_SESSION") if env.get(k)]
    hyprland = bool(env.get("HYPRLAND_INSTANCE_SIGNATURE")) or any(
        d.lower() == "hyprland" for d in desktops)
    session_type = (env.get("XDG_SESSION_TYPE") or env.get("XDG_BACKEND") or "").lower()
    if not session_type:
        session_type = "wayland" if env.get("WAYLAND_DISPLAY") else "x11" if env.get("DISPLAY") else ""
    label = env.get("XDG_CURRENT_DESKTOP") or (desktops[0] if desktops else None)
    return {"hyprland": hyprland, "desktop": label,
            "session_type": session_type or None,
            "vars": {k: env.get(k) for k in SESSION_VARS}}


def package_manager(os_release: str) -> str | None:
    fields = dict(re.findall(r'^(\w+)="?([^"\n]*)"?$', os_release, re.M))
    ids = [fields.get("ID", ""), *fields.get("ID_LIKE", "").split()]
    for distro_id in ids:
        if distro_id in ("arch", "manjaro", "endeavouros", "cachyos"):
            return "pacman"
        if distro_id in ("debian", "ubuntu"):
            return "apt"
        if distro_id in ("fedora", "rhel"):
            return "dnf"
        if distro_id.startswith("opensuse") or distro_id == "suse":
            return "zypper"
    return None


def install_command(manager: str | None, components: list[str]) -> str | None:
    if not components:
        return None
    if manager is None:
        return "install with your package manager: " + ", ".join(components)
    pkgs = dict.fromkeys(PACKAGES[c][manager] for c in components)
    return f"{INSTALL_PREFIX[manager]} {' '.join(pkgs)}"


def parse_version(text: str) -> tuple[int, ...] | None:
    found = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text)
    return tuple(int(g) for g in found.groups() if g is not None) if found else None


def cmd_doctor(_args: argparse.Namespace) -> Json:
    checks: list[Json] = []
    missing: list[str] = []

    def check(name: str, status: str, detail: str, fix: str | None = None,
              component: str | None = None) -> None:
        checks.append({"check": name, "status": status, "detail": detail,
                       **({"fix": fix} if fix else {})})
        if component and status != "ok":
            missing.append(component)

    try:
        adopted = adopt_session()
    except DeskError as err:
        check("instance", "fail", str(err))
        return {"supported": False, "ready": False, "session": detect_session(dict(os.environ)),
                "checks": checks}
    session = detect_session(dict(os.environ))
    if adopted:
        session["adopted"] = adopted
    os_release = Path("/etc/os-release").read_text() if Path("/etc/os-release").exists() else ""
    manager = package_manager(os_release)
    report: Json = {"supported": False, "ready": False, "session": session,
                    "package_manager": manager, "checks": checks}

    if not session["hyprland"]:
        name = session["desktop"] or "no graphical session"
        check("desktop", "fail", f"desktop is {name!r}, not Hyprland",
              "this skill only drives Hyprland; use a tool built for this desktop"
              if session["desktop"] else
              "run from inside the Hyprland session (a terminal there), or export "
              "WAYLAND_DISPLAY, XDG_RUNTIME_DIR and HYPRLAND_INSTANCE_SIGNATURE from it")
        return report
    evidence = [k for k in ("XDG_CURRENT_DESKTOP", "XDG_SESSION_DESKTOP", "DESKTOP_SESSION")
                if "hyprland" in (session["vars"][k] or "").lower()]
    check("desktop", "ok", f"Hyprland per {', '.join(evidence) or 'HYPRLAND_INSTANCE_SIGNATURE'}")
    if session["session_type"] != "wayland":
        check("session-type", "fail", f"session type is {session['session_type']!r}, need wayland")
        return report
    check("session-type", "ok", "wayland")
    if not session["vars"]["HYPRLAND_INSTANCE_SIGNATURE"]:
        check("instance", "fail", "no running Hyprland instance found (`hyprctl instances` is empty)",
              "run from inside the Hyprland session, or export HYPRLAND_INSTANCE_SIGNATURE, "
              "WAYLAND_DISPLAY and XDG_RUNTIME_DIR from it")
        return report
    if adopted:
        check("instance", "warn", "session env was missing; adopted the only running instance: "
              + ", ".join(f"{k}={v}" for k, v in adopted.items()),
              "none needed; every helper command adopts it the same way")
    report["supported"] = True

    if not shutil.which("hyprctl"):
        check("hyprctl", "fail", "hyprctl not found", component="hyprctl")
    else:
        proc = subprocess.run(["hyprctl", "-j", "version"], capture_output=True, text=True)
        try:
            tag = json.loads(proc.stdout).get("tag", "")
        except json.JSONDecodeError:
            tag = ""
        version = parse_version(tag)
        if proc.returncode != 0 or version is None:
            check("hyprctl", "fail", f"hyprctl cannot reach the compositor: {proc.stderr.strip()[:120]}")
        elif version < (0, 55):
            check("hyprctl", "warn", f"Hyprland {tag}: input commands need the Lua dispatch API (0.55+)",
                  "upgrade Hyprland, or drive input with classic `hyprctl dispatch` by hand")
        else:
            check("hyprctl", "ok", f"Hyprland {tag}")

    if sys.version_info < (3, 10):
        check("python", "warn", f"Python {sys.version.split()[0]}; 3.10+ is the tested baseline")
    else:
        check("python", "ok", f"Python {sys.version.split()[0]}")

    if shutil.which("grim"):
        check("grim", "ok", "screenshots available")
    else:
        check("grim", "fail", "grim not found: no screenshots", component="grim")

    if not (shutil.which("ydotool") and shutil.which("ydotoold")):
        check("ydotool", "fail", "ydotool/ydotoold not found: no pointer input or focused typing",
              component="ydotool")
    else:
        help_text = subprocess.run(["ydotool", "click", "--help"], capture_output=True,
                                   text=True).stdout
        if "0x40" not in help_text:
            check("ydotool", "fail", "ydotool is older than 1.0 (incompatible CLI; Debian/Ubuntu ship 0.1.x)",
                  "install ydotool 1.x from upstream releases or a newer repository")
        else:
            check("ydotool", "ok", "ydotool 1.x")
        if os.access("/dev/uinput", os.R_OK | os.W_OK):
            check("uinput", "ok", "/dev/uinput is writable")
        else:
            check("uinput", "fail", "/dev/uinput is not writable by this user; ydotoold cannot inject input",
                  f"echo '{UINPUT_RULE}' | sudo tee /etc/udev/rules.d/60-uinput.rules && "
                  "sudo udevadm control --reload && sudo udevadm trigger /dev/uinput; "
                  "then log out and back in")
        sock = os.environ.get("YDOTOOL_SOCKET") or f"/run/user/{os.getuid()}/.ydotool_socket"
        if Path(sock).exists():
            check("ydotoold", "ok", f"daemon socket {sock}")
        else:
            check("ydotoold", "warn", "ydotoold is not running (the helper starts it on first input)",
                  "systemctl --user enable --now ydotool")

    if shutil.which("wl-copy") and shutil.which("wl-paste"):
        check("wl-clipboard", "ok", "paste available")
    else:
        check("wl-clipboard", "warn", "wl-clipboard not found: `paste` unavailable", component="wl-clipboard")

    if not shutil.which("tesseract"):
        check("tesseract", "warn", "tesseract not found: `find-text` unavailable",
              component="tesseract")
        missing.append("tesseract-eng")
    else:
        langs = run(["tesseract", "--list-langs"]).splitlines()[1:]
        if "eng" in langs:
            check("tesseract", "ok", f"OCR languages: {', '.join(langs)}")
        else:
            check("tesseract", "warn", f"no English OCR data (have: {', '.join(langs) or 'none'})",
                  component="tesseract-eng")

    report["install"] = install_command(manager, missing)
    report["ready"] = not any(c["status"] == "fail" for c in checks)
    return report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hyprdesk", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def targets(sp: argparse.ArgumentParser) -> None:
        g = sp.add_mutually_exclusive_group()
        g.add_argument("--monitor", help="monitor name (default: focused monitor)")
        g.add_argument("--window", help="0xADDR, class=..., title=..., or active")
        g.add_argument("--region", help="global logical 'X,Y,W,H'")
        g.add_argument("--all", action="store_true", help="every monitor")

    sp = sub.add_parser("doctor", help="read-only preflight: session, dependencies, install hints")
    sp.set_defaults(fn=cmd_doctor)

    sp = sub.add_parser("state", help="monitors, cursor, windows as JSON")
    sp.set_defaults(fn=cmd_state)

    sp = sub.add_parser("shot", help="screenshot; prints path and the pixel->global mapping")
    targets(sp)
    sp.add_argument("--max", type=int, default=DEFAULT_MAX_EDGE,
                    help=f"downscale so the long edge <= this (default {DEFAULT_MAX_EDGE}; 0 = logical size)")
    sp.add_argument("--out", help="output PNG path")
    sp.set_defaults(fn=cmd_shot)

    sp = sub.add_parser("find-text", help="OCR a fresh capture and return global click points")
    targets(sp)
    sp.add_argument("text")
    sp.add_argument("--exact", action="store_true", help="whole-word match instead of substring")
    sp.add_argument("--lang", help="tesseract language(s), e.g. eng or eng+spa")
    sp.set_defaults(fn=cmd_find_text)

    def xy(sp: argparse.ArgumentParser, *names: str) -> None:
        for n in names:
            sp.add_argument(n, type=float)
        sp.add_argument("--image", action="store_true", help="coordinates are pixels in the last shot")

    sp = sub.add_parser("move", help="warp the pointer")
    xy(sp, "x", "y")
    sp.set_defaults(fn=cmd_move)

    sp = sub.add_parser("click", help="move then click")
    xy(sp, "x", "y")
    sp.add_argument("--button", choices=sorted(BUTTONS), default="left")
    sp.add_argument("--count", type=int, default=1, help="2 for double-click")
    sp.set_defaults(fn=cmd_click)

    sp = sub.add_parser("drag", help="left-button drag from (x1,y1) to (x2,y2)")
    xy(sp, "x1", "y1", "x2", "y2")
    sp.add_argument("--steps", type=int, default=12)
    sp.set_defaults(fn=cmd_drag)

    sp = sub.add_parser("scroll", help="wheel at a point; positive --down scrolls toward the end")
    xy(sp, "x", "y")
    sp.add_argument("--down", type=int, default=3, help="wheel notches; negative scrolls up")
    sp.add_argument("--right", type=int, default=0, help="horizontal notches")
    sp.set_defaults(fn=cmd_scroll)

    sp = sub.add_parser("type", help="type text (focused window, or --window for background ASCII)")
    sp.add_argument("text")
    sp.add_argument("--window", help="deliver to this window without focusing it (ASCII only)")
    sp.set_defaults(fn=cmd_type)

    sp = sub.add_parser("key", help="send key combos, e.g. ctrl+l Return 'ctrl+shift+t'")
    sp.add_argument("combo", nargs="+")
    sp.add_argument("--window", help="deliver to this window without focusing it")
    sp.set_defaults(fn=cmd_key)

    sp = sub.add_parser("paste", help="put text on the clipboard and send Ctrl+V (overwrites clipboard)")
    sp.add_argument("text")
    sp.add_argument("--window")
    sp.add_argument("--terminal", action="store_true", help="send Ctrl+Shift+V instead")
    sp.set_defaults(fn=cmd_paste)

    for name, fn, help_ in (("focus", cmd_focus, "focus a window and verify"),
                            ("close", cmd_close, "politely close a window and verify")):
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("window")
        sp.set_defaults(fn=fn)

    sp = sub.add_parser("shape", help="float, un-maximize, resize, and center a window you own")
    sp.add_argument("window")
    sp.add_argument("--size", required=True, help="logical WxH, e.g. 1000x700")
    sp.add_argument("--monitor", help="center on this monitor (pick scale 1 for crisp, large text)")
    sp.set_defaults(fn=cmd_shape)

    sp = sub.add_parser("launch", help=f"exec a command into {AGENT_WS} (hidden) and report the new window(s)")
    sp.add_argument("command")
    sp.add_argument("--workspace", help=f"override the exec workspace rule (default: '{AGENT_WS} silent')")
    sp.add_argument("--timeout", type=float, default=10)
    sp.set_defaults(fn=cmd_launch)

    sp = sub.add_parser("adopt", help=f"silently move a window into {AGENT_WS}, remembering where it was")
    sp.add_argument("window")
    sp.set_defaults(fn=cmd_adopt)

    sp = sub.add_parser("release", help="return adopted windows to their original workspaces")
    g = sp.add_mutually_exclusive_group(required=True)
    g.add_argument("window", nargs="?")
    g.add_argument("--all", action="store_true")
    sp.set_defaults(fn=cmd_release)

    sp = sub.add_parser("stage", help=f"show {AGENT_WS} on a monitor (default: one without the agent's terminal)")
    sp.add_argument("--monitor")
    sp.set_defaults(fn=cmd_stage)

    sp = sub.add_parser("unstage", help=f"hide {AGENT_WS}; the user's workspaces never changed")
    sp.set_defaults(fn=cmd_unstage)

    sp = sub.add_parser("wait-window", help="wait until a selector matches exactly one window")
    sp.add_argument("window")
    sp.add_argument("--timeout", type=float, default=10)
    sp.set_defaults(fn=cmd_wait_window)
    return p


def announce(cmd: str, result: Json) -> None:
    if cmd == "shot":
        feedback("look", f"captured {result['target']}")
    elif cmd == "find-text":
        feedback("look", f"read text on {result['target']}: {len(result['matches'])} match(es)")
    elif cmd == "launch":
        feedback("window", "launched " + ", ".join(w["class"] for w in result["windows"])
                 + f" in {result['windows'][0]['workspace']}")
    elif cmd == "adopt":
        feedback("window", f"borrowed {result['adopted']} from workspace {result['origin']}")
    elif cmd == "release" and result["released"]:
        feedback("window", f"returned {len(result['released'])} window(s) to their workspaces")
    elif cmd == "stage" and result.get("changed"):
        feedback("warn" if result.get("warning") else "window",
                 result.get("warning") or f"working on {result['staged_on']}")
    elif cmd == "unstage" and result.get("changed"):
        feedback("window", "done; agent workspace hidden")
    elif cmd in ("focus", "close", "shape"):
        target = result.get("focused") or result.get("closed") or result.get("shaped") \
            or result.get("close_requested")
        feedback("window", f"{cmd} {target}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd != "doctor":
            _ = adopt_session()
        result = args.fn(args)
    except DeskError as err:
        print(json.dumps({"error": str(err)}), file=sys.stderr)
        return 1
    announce(args.cmd, result)
    print(json.dumps(result, ensure_ascii=False))
    if args.cmd == "doctor":
        return 0 if result["ready"] else 1 if result["supported"] else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
