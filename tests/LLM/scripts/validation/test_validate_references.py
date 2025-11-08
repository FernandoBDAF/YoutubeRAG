"""Unit tests for validate_references.py - Markdown reference validation."""

import unittest
import sys
import tempfile
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from LLM.scripts.validation.validate_references import (
    find_markdown_files,
    extract_references,
    validate_reference,
    scan_project,
    generate_report,
)


class TestFindMarkdownFiles(unittest.TestCase):
    """Test find_markdown_files function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_find_markdown_files_in_root(self):
        """Test finding markdown files in root."""
        Path("file1.md").write_text("# File 1\n")
        Path("file2.md").write_text("# File 2\n")

        result = find_markdown_files(Path("."), ignore_archives=False)
        self.assertEqual(len(result), 2)
        self.assertTrue(any(f.name == "file1.md" for f in result))
        self.assertTrue(any(f.name == "file2.md" for f in result))

    def test_find_markdown_files_in_subdirectories(self):
        """Test finding markdown files in subdirectories."""
        Path("subdir").mkdir()
        Path("subdir/file1.md").write_text("# File 1\n")
        Path("subdir/file2.md").write_text("# File 2\n")

        result = find_markdown_files(Path("."), ignore_archives=False)
        self.assertEqual(len(result), 2)

    def test_ignore_archives(self):
        """Test ignoring archive directories."""
        Path("documentation/archive/test").mkdir(parents=True, exist_ok=True)
        Path("documentation/archive/test/file.md").write_text("# File\n")
        Path("file.md").write_text("# File\n")

        result = find_markdown_files(Path("."), ignore_archives=True)
        # Should only find file.md, not archive file
        self.assertEqual(len(result), 1)
        self.assertTrue(any(f.name == "file.md" for f in result))

    def test_include_archives(self):
        """Test including archive directories when not ignoring."""
        Path("documentation/archive/test").mkdir(parents=True, exist_ok=True)
        Path("documentation/archive/test/file.md").write_text("# File\n")
        Path("file.md").write_text("# File\n")

        result = find_markdown_files(Path("."), ignore_archives=False)
        # Should find both files
        self.assertEqual(len(result), 2)

    def test_skip_hidden_directories(self):
        """Test skipping hidden directories."""
        Path(".hidden").mkdir()
        Path(".hidden/file.md").write_text("# File\n")
        Path("file.md").write_text("# File\n")

        result = find_markdown_files(Path("."), ignore_archives=False)
        # Should only find file.md, not hidden file
        self.assertEqual(len(result), 1)
        self.assertTrue(any(f.name == "file.md" for f in result))

    def test_find_no_files(self):
        """Test finding with no markdown files."""
        result = find_markdown_files(Path("."), ignore_archives=False)
        self.assertEqual(len(result), 0)

    def test_sorted_results(self):
        """Test that results are sorted."""
        Path("z_file.md").write_text("# Z File\n")
        Path("a_file.md").write_text("# A File\n")
        Path("m_file.md").write_text("# M File\n")

        result = find_markdown_files(Path("."), ignore_archives=False)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].name, "a_file.md")
        self.assertEqual(result[1].name, "m_file.md")
        self.assertEqual(result[2].name, "z_file.md")


class TestExtractReferences(unittest.TestCase):
    """Test extract_references function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        self.root_dir = Path(".")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_extract_markdown_links(self):
        """Test extracting markdown links."""
        content = """# Document

See [file1.md](file1.md) for details.
Also check [file2.md](file2.md).
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "file1.md")
        self.assertEqual(result[1][0], "file2.md")

    def test_extract_with_link_text(self):
        """Test extracting links with text."""
        content = """# Document

See [this file](file1.md) for details.
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "file1.md")
        self.assertEqual(result[0][2], "this file")

    def test_skip_external_urls_http(self):
        """Test skipping external HTTP URLs."""
        content = """# Document

See [external](http://example.com) link.
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 0)

    def test_skip_external_urls_https(self):
        """Test skipping external HTTPS URLs."""
        content = """# Document

See [external](https://example.com) link.
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 0)

    def test_skip_external_urls_mailto(self):
        """Test skipping mailto URLs."""
        content = """# Document

Contact [email](mailto:test@example.com).
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 0)

    def test_skip_section_anchors(self):
        """Test skipping section anchors."""
        content = """# Document

See [section](#section-name).
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 0)

    def test_handle_section_anchors_in_path(self):
        """Test handling section anchors in file paths."""
        content = """# Document

See [file](file.md#section-name).
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 1)
        # Section anchor should be removed
        self.assertEqual(result[0][0], "file.md")

    def test_skip_empty_references(self):
        """Test skipping empty references."""
        content = """# Document

See [empty]() link.
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 0)

    def test_multiple_links_per_line(self):
        """Test handling multiple links per line."""
        content = """# Document

See [file1](file1.md) and [file2](file2.md) for details.
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 2)

    def test_line_numbers(self):
        """Test that line numbers are correct."""
        content = """# Document

Line 3: [file1](file1.md)

Line 5: [file2](file2.md)
"""
        file_path = Path("doc.md")
        file_path.write_text(content)

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], 3)  # Line number
        self.assertEqual(result[1][1], 5)  # Line number

    def test_missing_file(self):
        """Test handling missing file."""
        file_path = Path("nonexistent.md")

        result = extract_references(file_path, self.root_dir)
        self.assertEqual(result, [])


class TestValidateReference(unittest.TestCase):
    """Test validate_reference function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        self.root_dir = Path(".")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_validate_absolute_path(self):
        """Test validating absolute path from root."""
        Path("target.md").write_text("# Target\n")
        source_file = Path("source.md")
        source_file.write_text("# Source\n")

        is_valid, resolved_path = validate_reference("/target.md", source_file, self.root_dir)
        self.assertTrue(is_valid)
        self.assertTrue(resolved_path.exists())

    def test_validate_relative_path(self):
        """Test validating relative path."""
        Path("subdir").mkdir()
        Path("subdir/target.md").write_text("# Target\n")
        source_file = Path("subdir/source.md")
        source_file.write_text("# Source\n")

        is_valid, resolved_path = validate_reference("target.md", source_file, self.root_dir)
        self.assertTrue(is_valid)
        self.assertTrue(resolved_path.exists())

    def test_validate_nonexistent_file(self):
        """Test validating non-existent file."""
        source_file = Path("source.md")
        source_file.write_text("# Source\n")

        is_valid, resolved_path = validate_reference("nonexistent.md", source_file, self.root_dir)
        self.assertFalse(is_valid)
        self.assertFalse(resolved_path.exists())

    def test_validate_relative_path_parent(self):
        """Test validating relative path to parent directory."""
        Path("target.md").write_text("# Target\n")
        Path("subdir").mkdir()
        source_file = Path("subdir/source.md")
        source_file.write_text("# Source\n")

        is_valid, resolved_path = validate_reference("../target.md", source_file, self.root_dir)
        self.assertTrue(is_valid)
        self.assertTrue(resolved_path.exists())


class TestScanProject(unittest.TestCase):
    """Test scan_project function."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        self.root_dir = Path(".")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_scan_with_valid_references(self):
        """Test scanning with valid references."""
        Path("target1.md").write_text("# Target 1\n")
        Path("target2.md").write_text("# Target 2\n")
        Path("source.md").write_text("# Source\n[target1](target1.md)\n[target2](target2.md)\n")

        findings = scan_project(self.root_dir, ignore_archives=False, verbose=False)
        self.assertEqual(findings["total_files"], 3)
        self.assertEqual(findings["total_references"], 2)
        self.assertEqual(findings["valid_references"], 2)
        self.assertEqual(len(findings["broken_references"]), 0)

    def test_scan_with_broken_references(self):
        """Test scanning with broken references."""
        Path("source.md").write_text("# Source\n[broken](nonexistent.md)\n")

        findings = scan_project(self.root_dir, ignore_archives=False, verbose=False)
        self.assertEqual(findings["total_files"], 1)
        self.assertEqual(findings["total_references"], 1)
        self.assertEqual(findings["valid_references"], 0)
        self.assertEqual(len(findings["broken_references"]), 1)

    def test_scan_with_mixed_references(self):
        """Test scanning with mixed valid/broken references."""
        Path("target.md").write_text("# Target\n")
        Path("source.md").write_text("# Source\n[valid](target.md)\n[broken](nonexistent.md)\n")

        findings = scan_project(self.root_dir, ignore_archives=False, verbose=False)
        self.assertEqual(findings["total_files"], 2)
        self.assertEqual(findings["total_references"], 2)
        self.assertEqual(findings["valid_references"], 1)
        self.assertEqual(len(findings["broken_references"]), 1)

    def test_scan_ignore_archives(self):
        """Test scanning with ignore_archives flag."""
        Path("documentation/archive/test").mkdir(parents=True, exist_ok=True)
        Path("documentation/archive/test/file.md").write_text("# File\n[broken](nonexistent.md)\n")
        Path("source.md").write_text("# Source\n")

        findings = scan_project(self.root_dir, ignore_archives=True, verbose=False)
        # Should not find archive file
        self.assertEqual(findings["total_files"], 1)
        self.assertEqual(findings["total_references"], 0)

    def test_scan_files_with_issues(self):
        """Test tracking files with issues."""
        Path("source1.md").write_text("# Source 1\n[broken1](nonexistent1.md)\n")
        Path("source2.md").write_text("# Source 2\n[broken2](nonexistent2.md)\n")

        findings = scan_project(self.root_dir, ignore_archives=False, verbose=False)
        self.assertEqual(len(findings["files_with_issues"]), 2)


class TestGenerateReport(unittest.TestCase):
    """Test generate_report function."""

    def test_human_readable_report_no_issues(self):
        """Test human-readable report with no issues."""
        findings = {
            "total_files": 10,
            "total_references": 20,
            "broken_references": [],
            "files_with_issues": set(),
            "valid_references": 20,
        }

        report = generate_report(findings, output_json=False)
        self.assertIn("MARKDOWN REFERENCE VALIDATION REPORT", report)
        self.assertIn("Files Scanned: 10", report)
        self.assertIn("Total References: 20", report)
        self.assertIn("Valid References: 20", report)
        self.assertIn("✅ SUCCESS", report)

    def test_human_readable_report_with_issues(self):
        """Test human-readable report with issues."""
        findings = {
            "total_files": 5,
            "total_references": 10,
            "broken_references": [
                {
                    "file": "source.md",
                    "line": 3,
                    "reference": "broken.md",
                    "link_text": "broken link",
                    "resolved_path": "/path/to/broken.md",
                }
            ],
            "files_with_issues": {"source.md"},
            "valid_references": 9,
        }

        report = generate_report(findings, output_json=False)
        self.assertIn("MARKDOWN REFERENCE VALIDATION REPORT", report)
        self.assertIn("Broken References: 1", report)
        self.assertIn("⚠️  BROKEN REFERENCES FOUND", report)
        # Check for content without ANSI codes
        self.assertIn("source.md", report)
        self.assertIn(":3", report)
        self.assertIn("STATUS: FAILED", report)

    def test_json_report(self):
        """Test JSON report generation."""
        findings = {
            "total_files": 5,
            "total_references": 10,
            "broken_references": [
                {
                    "file": "source.md",
                    "line": 3,
                    "reference": "broken.md",
                    "link_text": "broken link",
                    "resolved_path": "/path/to/broken.md",
                }
            ],
            "files_with_issues": {"source.md"},
            "valid_references": 9,
        }

        report = generate_report(findings, output_json=True)
        parsed = json.loads(report)
        self.assertEqual(parsed["total_files"], 5)
        self.assertEqual(parsed["total_references"], 10)
        self.assertEqual(len(parsed["broken_references"]), 1)
        # files_with_issues should be converted to list
        self.assertIsInstance(parsed["files_with_issues"], list)

    def test_color_coding(self):
        """Test color coding in report."""
        findings = {
            "total_files": 5,
            "total_references": 10,
            "broken_references": [
                {
                    "file": "source.md",
                    "line": 3,
                    "reference": "broken.md",
                    "link_text": "broken link",
                    "resolved_path": "/path/to/broken.md",
                }
            ],
            "files_with_issues": {"source.md"},
            "valid_references": 9,
        }

        report = generate_report(findings, output_json=False)
        # Check that report contains color codes (ANSI escape sequences)
        self.assertIn("\033[", report)  # ANSI color codes


class TestIntegration(unittest.TestCase):
    """Integration tests with real documentation structures."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        self.root_dir = Path(".")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_complete_valid_documentation(self):
        """Test with complete valid documentation."""
        Path("doc1.md").write_text("# Doc 1\n[doc2](doc2.md)\n")
        Path("doc2.md").write_text("# Doc 2\n[doc3](doc3.md)\n")
        Path("doc3.md").write_text("# Doc 3\n")

        findings = scan_project(self.root_dir, ignore_archives=False, verbose=False)
        self.assertEqual(findings["total_files"], 3)
        self.assertEqual(findings["total_references"], 2)
        self.assertEqual(findings["valid_references"], 2)
        self.assertEqual(len(findings["broken_references"]), 0)

    def test_documentation_with_broken_links(self):
        """Test with documentation containing broken links."""
        Path("doc1.md").write_text("# Doc 1\n[broken](nonexistent.md)\n")

        findings = scan_project(self.root_dir, ignore_archives=False, verbose=False)
        self.assertEqual(findings["total_files"], 1)
        self.assertEqual(findings["total_references"], 1)
        self.assertEqual(findings["valid_references"], 0)
        self.assertEqual(len(findings["broken_references"]), 1)

    def test_documentation_with_external_urls(self):
        """Test with documentation containing external URLs."""
        Path("doc1.md").write_text(
            "# Doc 1\n[external](https://example.com)\n[local](doc2.md)\n"
        )
        Path("doc2.md").write_text("# Doc 2\n")

        findings = scan_project(self.root_dir, ignore_archives=False, verbose=False)
        # External URL should be skipped
        self.assertEqual(findings["total_references"], 1)
        self.assertEqual(findings["valid_references"], 1)


if __name__ == "__main__":
    unittest.main()

