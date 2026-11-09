import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("video_pack", ROOT / "scripts/video_pack.py")
vp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vp)
installer_spec = importlib.util.spec_from_file_location("install_skill", ROOT / "scripts/install_skill.py")
installer = importlib.util.module_from_spec(installer_spec)
installer_spec.loader.exec_module(installer)


class TimestampTests(unittest.TestCase):
    def test_time_formats(self):
        self.assertAlmostEqual(vp.seconds("01:02:03,450"), 3723.45)
        self.assertEqual(vp.seconds("03:20"), 200)
        self.assertEqual(vp.stamp(59.9996), "00:01:00.000")

    def test_reject_invalid_or_nonfinite(self):
        for value in [-1, "nan", "inf", True, "00:61:01", "00:60", "1:2:3:4"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                vp.seconds(value)


class SubtitleTests(unittest.TestCase):
    def parse(self, suffix, content):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ("transcript" + suffix)
            path.write_text(content, encoding="utf-8")
            return vp.parse_transcript(path)

    def test_vtt_cue_id_settings_tags_and_entities(self):
        rows = self.parse(".vtt", "WEBVTT\n\nintro\n00:01.200 --> 00:02.800 align:start\n<b>Hello</b> &amp;\nworld\n")
        self.assertEqual(rows, [{"start": 1.2, "end": 2.8, "text": "Hello & world"}])

    def test_srt_comma_and_bom(self):
        rows = self.parse(".srt", "\ufeff1\n00:00:01,000 --> 00:00:02,000\n字幕\n\n")
        self.assertEqual(rows[0]["text"], "字幕")

    def test_canonical_json(self):
        rows = self.parse(".json", '{"segments":[{"start":1,"end":"00:03","text":"ok"}]}')
        self.assertEqual(rows[0]["end"], 3)

    def test_plain_text_does_not_invent_time(self):
        rows = self.parse(".md", "Some text without a time axis")
        self.assertIsNone(rows[0]["start"])

    def test_invalid_cue_order(self):
        with self.assertRaises(ValueError):
            self.parse(".vtt", "00:02.000 --> 00:01.000\nWrong order\n")


class SelectionTests(unittest.TestCase):
    def test_precise_midpoints_and_overlap_deduplication(self):
        rows = vp.frame_plan([{"start": 0, "end": 4}, {"start": 0, "end": 4}], 10, 3, 3)
        self.assertEqual([r["requested_seconds"] for r in rows], [1, 2, 3])

    def test_empty_plan(self):
        self.assertEqual(vp.frame_plan({"key_segments": []}, 10, 3, 12), [])

    def test_range_limit(self):
        for segments in [[{"start": 5, "end": 4}], [{"start": 5, "end": 11}]]:
            with self.assertRaises(ValueError):
                vp.frame_plan(segments, 10, 3, 12)

    def test_frame_budget_rejected_before_decode(self):
        with self.assertRaisesRegex(ValueError, "超过上限"):
            vp.frame_plan([{"start": 0, "end": 10}], 10, 3, 2)


class DownloadTests(unittest.TestCase):
    def test_no_implicit_login_or_config(self):
        cmd = vp.download_command("https://example.org/video?id=1", Path("incoming"))
        self.assertIn("--ignore-config", cmd)
        self.assertNotIn("--cookies", cmd)
        self.assertNotIn("--cookies-from-browser", cmd)
        self.assertEqual(cmd[-2], "--")

    def test_explicit_cookie_file(self):
        cmd = vp.download_command("https://example.org/video", Path("incoming"), Path("explicit.txt"))
        self.assertEqual(cmd[cmd.index("--cookies") + 1], "explicit.txt")

    def test_reject_local_and_option_urls(self):
        for url in ["file:///etc/passwd", "--exec=bad", "not-a-url"]:
            with self.assertRaises(ValueError):
                vp.download_command(url, Path("incoming"))


class InstallTests(unittest.TestCase):
    def test_install_is_portable_and_preserves_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = installer.install(ROOT, Path(tmp))
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertFalse((dest / "examples").exists())
            self.assertFalse(any(dest.rglob("*.pyc")))
            before = (dest / "SKILL.md").read_bytes()
            with self.assertRaises(FileExistsError):
                installer.install(ROOT, Path(tmp))
            self.assertEqual((dest / "SKILL.md").read_bytes(), before)


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg is required for media integration tests")
class MediaIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Spaces and shell metacharacters must remain ordinary filename characters.
        self.video = self.root / "video $(echo unsafe).mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=orange:s=320x180:r=10",
                        "-t", "3", "-c:v", "mpeg4", str(self.video)], check=True)
        self.subs = self.root / "captions.vtt"
        self.subs.write_text("WEBVTT\n\n00:00.000 --> 00:03.000\nOriginal test caption.\n", encoding="utf-8")
        self.pack = self.root / "pack"

    def prepare(self):
        self.assertEqual(vp.main(["prepare", "--video", str(self.video), "--transcript", str(self.subs),
                                  "--output", str(self.pack), "--title", "Test"]), 0)

    def test_real_media_pack_and_frame(self):
        self.prepare()
        data = json.loads((self.pack / "manifest.json").read_text())
        self.assertEqual(data["status"], "ready_for_planning")
        self.assertEqual(data["transcript_backend"]["provider"], "supplied_transcript")
        selection = self.root / "segments.json"
        selection.write_text('[{"start":0,"end":2}]')
        command = ["frames", "--pack", str(self.pack), "--segments", str(selection), "--per-segment", "1"]
        self.assertEqual(vp.main(command), 0)
        info = json.loads((self.pack / "frames.json").read_text())
        self.assertEqual(info["vision_status"], "not_reviewed")
        self.assertEqual(info["frames"][0]["requested_seconds"], 1)
        frame = self.pack / info["frames"][0]["file"]
        self.assertTrue(frame.read_bytes().startswith(b"\xff\xd8"))
        before = frame.read_bytes()
        self.assertEqual(vp.main(command), 1)
        self.assertEqual(frame.read_bytes(), before)

    def test_existing_output_is_preserved(self):
        self.pack.mkdir()
        marker = self.pack / "keep.txt"
        marker.write_text("keep")
        result = vp.main(["prepare", "--video", str(self.video), "--transcript", str(self.subs), "--output", str(self.pack)])
        self.assertEqual(result, 1)
        self.assertEqual(marker.read_text(), "keep")

    def test_failed_subtitles_are_not_ready(self):
        self.subs.write_text("")
        result = vp.main(["prepare", "--video", str(self.video), "--transcript", str(self.subs), "--output", str(self.pack)])
        self.assertEqual(result, 1)
        self.assertEqual(json.loads((self.pack / "manifest.json").read_text())["status"], "failed")

    def test_ffmpeg_failure_keeps_no_partial_frames(self):
        self.prepare()
        selection = self.root / "segments.json"
        selection.write_text('[{"start":0,"end":2}]')
        with patch.object(vp, "run", side_effect=RuntimeError("decoder failed")):
            result = vp.main(["frames", "--pack", str(self.pack), "--segments", str(selection)])
        self.assertEqual(result, 1)
        self.assertFalse((self.pack / "frames").exists())
        self.assertFalse((self.pack / "frames.json").exists())


if __name__ == "__main__":
    unittest.main()
