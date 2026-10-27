import tempfile
import unittest
from pathlib import Path

from file_organizer import (
    build_plan,
    get_category,
    get_unique_path,
    organize_files,
)


class TestFileOrganizer(unittest.TestCase):
    def test_known_extension(self):
        self.assertEqual(get_category(Path("report.pdf")), "PDF_Files")

    def test_uppercase_extension(self):
        self.assertEqual(get_category(Path("PHOTO.JPG")), "Images")

    def test_unknown_extension(self):
        self.assertEqual(get_category(Path("archive.xyz")), "Others")

    def test_extensionless_file(self):
        self.assertEqual(get_category(Path("README")), "Others")

    def test_unique_path_avoids_existing_name(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "report.pdf"
            original.touch()
            self.assertEqual(get_unique_path(original).name, "report_1.pdf")

    def test_unique_path_skips_multiple_conflicts(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "report.pdf").touch()
            (folder / "report_1.pdf").touch()
            self.assertEqual(get_unique_path(folder / "report.pdf").name, "report_2.pdf")

    def test_build_plan_does_not_move_files(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "report.pdf"
            source.write_text("sample", encoding="utf-8")
            plan = build_plan(folder)
            self.assertEqual(len(plan), 1)
            self.assertEqual(plan[0][0], source)
            self.assertTrue(source.exists())
            self.assertFalse((folder / "PDF_Files").exists())

    def test_dry_run_does_not_change_filesystem(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "report.pdf"
            source.write_text("sample", encoding="utf-8")
            result = organize_files(folder, dry_run=True)
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["moved"], 0)
            self.assertTrue(source.exists())
            self.assertFalse((folder / "PDF_Files").exists())

    def test_apply_moves_file(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "report.pdf"
            source.write_text("sample", encoding="utf-8")
            result = organize_files(folder, dry_run=False)
            self.assertEqual(result["moved"], 1)
            self.assertFalse(source.exists())
            self.assertTrue((folder / "PDF_Files" / "report.pdf").exists())

    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            result = organize_files(temp, dry_run=True)
            self.assertEqual(result["total"], 0)

    def test_invalid_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing"
            with self.assertRaises(FileNotFoundError):
                organize_files(missing, dry_run=True)


if __name__ == "__main__":
    unittest.main()
