import csv
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from content.manifest import build, create_run


class ManifestTests(unittest.TestCase):
    def test_order_and_dependencies(self):
        manifest = build("Rainy station")
        self.assertEqual([step["kind"] for step in manifest["steps"]], ["text", "image", "video"])
        self.assertEqual(manifest["steps"][2]["depends_on"], ["text-01", "image-01"])
        self.assertEqual(manifest["base_url"], "https://argolink.io/v1")

    def test_create_run_writes_reviewable_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = create_run("A quiet ocean", root=pathlib.Path(directory) / "out")
            manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
            with (path / "steps.csv").open(newline="", encoding="utf-8") as handle:
                self.assertEqual(next(csv.reader(handle))[0], "step_id")
            self.assertTrue((path / "text").is_dir())
            self.assertEqual(manifest["steps"][0]["model"], "gpt-5.4")

    def test_rejects_empty_or_absolute_output(self):
        with self.assertRaises(ValueError):
            build(" ")
        with self.assertRaises(ValueError):
            build("topic", folder="/tmp/out")


if __name__ == "__main__":
    unittest.main()
