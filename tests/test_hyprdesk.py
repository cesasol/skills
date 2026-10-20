"""Offline tests for the hyprland-desktop helper; nothing here talks to Hyprland."""

from __future__ import annotations

import importlib.util
import os
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "hyprdesk", REPO_ROOT / "hyprland-desktop" / "scripts" / "hyprdesk.py"
)
assert SPEC and SPEC.loader
hd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hd)


def tiny_png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x00" * 3 * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


class LuaStringTests(unittest.TestCase):
    def test_escapes_quotes_backslashes_and_controls(self) -> None:
        self.assertEqual(hd.lua_str('a"b\\c\nd\x01'), '"a\\"b\\\\c\\nd\\001"')

    def test_keeps_utf8(self) -> None:
        self.assertEqual(hd.lua_str("canción"), '"canción"')


class ComboTests(unittest.TestCase):
    def test_plus_separated_with_aliases(self) -> None:
        self.assertEqual(hd.parse_combo("ctrl+Shift+p"), ("CTRL SHIFT", "p"))
        self.assertEqual(hd.parse_combo("meta+Return"), ("SUPER", "Return"))

    def test_bare_key(self) -> None:
        self.assertEqual(hd.parse_combo("Escape"), ("", "Escape"))

    def test_unknown_modifier_rejected(self) -> None:
        with self.assertRaises(hd.DeskError):
            hd.parse_combo("hyper+x")


class CharMappingTests(unittest.TestCase):
    def test_letters_digits_and_symbols(self) -> None:
        self.assertEqual(hd.char_to_shortcut("a"), ("", "a"))
        self.assertEqual(hd.char_to_shortcut("A"), ("SHIFT", "a"))
        self.assertEqual(hd.char_to_shortcut("7"), ("", "7"))
        self.assertEqual(hd.char_to_shortcut("!"), ("SHIFT", "1"))
        self.assertEqual(hd.char_to_shortcut("?"), ("SHIFT", "slash"))
        self.assertEqual(hd.char_to_shortcut(" "), ("", "space"))
        self.assertEqual(hd.char_to_shortcut("\n"), ("", "Return"))

    def test_non_ascii_rejected(self) -> None:
        with self.assertRaises(hd.DeskError):
            hd.char_to_shortcut("ñ")


class GeometryTests(unittest.TestCase):
    def test_scaled_monitor(self) -> None:
        mon = {
            "x": 3000,
            "y": 0,
            "width": 3840,
            "height": 2160,
            "scale": 1.3333334,
            "transform": 0,
        }
        self.assertEqual(hd.logical_rect(mon), (3000, 0, 2880, 1620))

    def test_rotated_monitor_swaps_axes(self) -> None:
        mon = {
            "x": 1920,
            "y": 0,
            "width": 1920,
            "height": 1080,
            "scale": 1,
            "transform": 1,
        }
        self.assertEqual(hd.logical_rect(mon), (1920, 0, 1080, 1920))

    def test_image_to_global_undoes_downscale(self) -> None:
        meta = {"x": 3000, "y": 0, "img_w": 1568, "img_h": 882, "scale": 1568 / 2880}
        self.assertEqual(hd.image_to_global(meta, 784, 441), (4440, 810))

    def test_image_point_outside_shot_rejected(self) -> None:
        meta = {"x": 0, "y": 0, "img_w": 100, "img_h": 100, "scale": 1.0}
        with self.assertRaises(hd.DeskError):
            hd.image_to_global(meta, 101, 5)

    def test_png_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.png"
            path.write_bytes(tiny_png(7, 3))
            self.assertEqual(hd.png_size(path), (7, 3))


class MultiMonitorTests(unittest.TestCase):
    PORTRAIT = {
        "name": "HDMI-A-3",
        "x": 1920,
        "y": 0,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "transform": 1,
    }
    SCALED = {
        "name": "DP-3",
        "x": 3000,
        "y": 0,
        "width": 3840,
        "height": 2160,
        "scale": 1.3333334,
        "transform": 0,
    }
    LEFT = {
        "name": "eDP-1",
        "x": -1920,
        "y": 300,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "transform": 0,
    }

    def mons(self) -> list[dict[str, Any]]:
        return [self.PORTRAIT, self.SCALED, self.LEFT]

    def test_points_resolve_to_their_monitor(self) -> None:
        self.assertEqual(hd.require_on_screen(self.mons(), 1920, 1919), "HDMI-A-3")
        self.assertEqual(hd.require_on_screen(self.mons(), 3000, 0), "DP-3")
        self.assertEqual(hd.require_on_screen(self.mons(), -1, 300), "eDP-1")

    def test_gap_below_shorter_monitor_rejected(self) -> None:
        with self.assertRaises(hd.DeskError):
            hd.require_on_screen(self.mons(), 5000, 1800)

    def test_agent_monitor_avoids_user_then_self_then_prefers_scale_1(self) -> None:
        mons = [
            dict(self.PORTRAIT, focused=False),
            dict(self.SCALED, focused=True),
            dict(self.LEFT, focused=False),
        ]
        pick = hd.pick_agent_monitor
        self.assertEqual(pick(mons, {"HDMI-A-3"}, "DP-3")["name"], "eDP-1")
        self.assertEqual(pick(mons[:2], {"HDMI-A-3"}, "DP-3")["name"], "HDMI-A-3")
        self.assertEqual(pick(mons[:2], {"HDMI-A-3"}, None)["name"], "DP-3")
        self.assertEqual(pick(mons[:2], set(), None)["name"], "HDMI-A-3")

    def test_pinned_monitor_by_name_or_description(self) -> None:
        mons = [
            dict(self.PORTRAIT, description="Dell Inc. DELL P2419H ABC"),
            self.SCALED,
        ]
        rule = {
            "workspaceString": "special:agent",
            "enabled": True,
            "monitor": "HDMI-A-3",
        }
        self.assertEqual(hd.pinned_monitor([rule], mons), "HDMI-A-3")
        by_desc = dict(rule, monitor="desc:Dell Inc. DELL P2419H")
        self.assertEqual(hd.pinned_monitor([by_desc], mons), "HDMI-A-3")
        self.assertIsNone(hd.pinned_monitor([dict(rule, enabled=False)], mons))
        self.assertIsNone(
            hd.pinned_monitor([dict(rule, workspaceString="special:social")], mons)
        )

    def test_right_and_bottom_edges_are_exclusive(self) -> None:
        self.assertIsNone(hd.monitor_at(self.mons(), 5880, 10))
        self.assertIsNone(hd.monitor_at(self.mons(), -10, 1380))


class PreflightTests(unittest.TestCase):
    def test_hyprland_session_detected(self) -> None:
        env = {
            "XDG_CURRENT_DESKTOP": "Hyprland",
            "XDG_SESSION_TYPE": "wayland",
            "XDG_BACKEND": "wayland",
            "HYPRLAND_INSTANCE_SIGNATURE": "abc",
        }
        session = hd.detect_session(env)
        self.assertTrue(session["hyprland"])
        self.assertEqual(session["session_type"], "wayland")

    def test_other_desktop_keeps_full_label(self) -> None:
        session = hd.detect_session(
            {"XDG_CURRENT_DESKTOP": "ubuntu:GNOME", "XDG_SESSION_TYPE": "wayland"}
        )
        self.assertFalse(session["hyprland"])
        self.assertEqual(session["desktop"], "ubuntu:GNOME")

    def test_session_type_falls_back_to_backend_then_display(self) -> None:
        self.assertEqual(
            hd.detect_session({"XDG_BACKEND": "wayland"})["session_type"], "wayland"
        )
        self.assertEqual(hd.detect_session({"DISPLAY": ":0"})["session_type"], "x11")
        self.assertIsNone(hd.detect_session({})["session_type"])

    def test_package_manager_from_os_release(self) -> None:
        self.assertEqual(hd.package_manager("ID=arch\n"), "pacman")
        self.assertEqual(hd.package_manager('ID=pop\nID_LIKE="ubuntu debian"\n'), "apt")
        self.assertEqual(hd.package_manager('ID="opensuse-tumbleweed"\n'), "zypper")
        self.assertIsNone(hd.package_manager("ID=gentoo\n"))

    def test_install_command_maps_and_dedupes(self) -> None:
        self.assertEqual(
            hd.install_command("apt", ["grim", "tesseract", "tesseract-eng", "grim"]),
            "sudo apt install grim tesseract-ocr tesseract-ocr-eng",
        )
        self.assertIsNone(hd.install_command("pacman", []))
        self.assertIn("grim", hd.install_command(None, ["grim"]) or "")

    def test_choose_instance_ignores_dead_and_rejects_ambiguity(self) -> None:
        instances = [
            {"instance": "a", "pid": 10, "wl_socket": "wayland-1"},
            {"instance": "b", "pid": 20, "wl_socket": "wayland-2"},
        ]
        self.assertEqual(hd.choose_instance(instances, {20})["instance"], "b")
        self.assertIsNone(hd.choose_instance(instances, set()))
        with self.assertRaises(hd.DeskError):
            hd.choose_instance(instances, {10, 20})

    def test_parse_version(self) -> None:
        self.assertEqual(hd.parse_version("v0.56.2"), (0, 56, 2))
        self.assertEqual(hd.parse_version("0.54"), (0, 54))
        self.assertIsNone(hd.parse_version("unknown"))


class AncestorTests(unittest.TestCase):
    def test_includes_self_and_parent(self) -> None:
        chain = hd.ancestor_pids()
        self.assertIn(os.getpid(), chain)
        self.assertIn(os.getppid(), chain)


if __name__ == "__main__":
    unittest.main()
