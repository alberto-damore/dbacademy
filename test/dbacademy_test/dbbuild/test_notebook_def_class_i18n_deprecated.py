import unittest
import typing

from dbacademy.dbbuild.publish.notebook_def_class import NotebookDef, NotebookError


class TestNotebookDef(unittest.TestCase):

    def __init__(self, method_name):
        super().__init__(method_name)

    def assert_n_errors(self, expected, notebook: NotebookDef):
        message = f"Expected {expected} errors, found {len(notebook.errors)}"
        for error in notebook.errors:
            message += f"\n{error.message}"

        self.assertEqual(expected, len(notebook.errors), f"Expected {expected} errors, found {len(notebook.errors)}")

    def assert_n_warnings(self, expected, notebook: NotebookDef):
        message = f"Expected {expected} errors, found {len(notebook.warnings)}"
        for warning in notebook.warnings:
            message += f"\n{warning.message}"

        self.assertEqual(expected, len(notebook.warnings), message)

    @staticmethod
    def create_notebook():
        from dbacademy.dbbuild import BuildConfig

        version = "1.2.3"
        build_config = BuildConfig(name="Unit Test",
                                   version=version)

        return NotebookDef(build_config=build_config,
                           path="Agenda",
                           replacements={},
                           include_solution=False,
                           test_round=2,
                           ignored=False,
                           order=0,
                           i18n=True,
                           i18n_language="English",
                           ignoring=[],
                           version=version)

    def test_good_single_space_i18n(self):
        command = """
# MAGIC %md --i18n-TBD
# MAGIC 
# MAGIC # Build-Time Substitutions""".strip()

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command, i=3, i18n_guid_map={"--i18n-TBD": "whatever"}, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(0, notebook)

        self.assertEqual(1, len(notebook.i18n_guids), f"Expected 1 GUID, found {len(notebook.i18n_guids)}")
        self.assertEqual("--i18n-TBD", notebook.i18n_guids[0])

    def test_good_double_spaced_i18n(self):
        command = """
# MAGIC %md  --i18n-TBD
# MAGIC 
# MAGIC # Build-Time Substitutions""".strip()

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command, i=3, i18n_guid_map={"--i18n-TBD": "whatever"}, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(0, notebook)

        self.assertEqual(1, len(notebook.i18n_guids), f"Expected 1 GUID, found {len(notebook.i18n_guids)}")
        self.assertEqual("--i18n-TBD", notebook.i18n_guids[0])

    def test_good_md_sandbox_i18n(self):
        command = """
# MAGIC %md-sandbox --i18n-TBD
# MAGIC 
# MAGIC # Build-Time Substitutions""".strip()

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command, i=3, i18n_guid_map={"--i18n-TBD": "whatever"}, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(0, notebook)

        self.assertEqual(1, len(notebook.i18n_guids), f"Expected 1 GUID, found {len(notebook.i18n_guids)}")
        self.assertEqual("--i18n-TBD", notebook.i18n_guids[0])

    def test_missing_i18n_multi(self):
        command = """
# MAGIC %md
# MAGIC 
# MAGIC # Build-Time Substitutions""".strip()

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command, i=3, i18n_guid_map={"--i18n-TBD": "whatever"}, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(1, notebook)

        self.assertEqual("Cmd #4 | Missing the i18n directive: %md", notebook.errors[0].message)

    def test_missing_i18n_single(self):
        command = "# MAGIC %md | # Build-Time Substitutions".strip()

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command, i=3, i18n_guid_map={"--i18n-TBD": "whatever"}, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(1, notebook)

        self.assertEqual("Cmd #4 | Expected MD to have more than 1 line of code with i18n enabled: %md | # Build-Time Substitutions", notebook.errors[0].message)

    def test_extra_word_i18n(self):
        command = """
# MAGIC %md --i18n-TBD # Title
# MAGIC 
# MAGIC # Build-Time Substitutions""".strip()

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command, i=3, i18n_guid_map={"--i18n-TBD": "whatever"}, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(1, notebook)

        self.assertEqual("Cmd #4 | Expected the first line of MD to have only two words, found 4: %md --i18n-TBD # Title", notebook.errors[0].message)

    def test_duplicate_i18n_guid(self):
        command_a = """
            # MAGIC %md --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a
            # MAGIC # Some Title""".strip()
        command_b = """
            # MAGIC %md --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a
            # MAGIC # Some Title""".strip()

        i18n_guid_map = {
            "--i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a": "whatever"
        }

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command_a, i=3, i18n_guid_map=i18n_guid_map, other_notebooks=[])
        notebook.update_md_cells(language="Python", command=command_b, i=4, i18n_guid_map=i18n_guid_map, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(1, notebook)

        self.assertEqual("Cmd #5 | Duplicate i18n GUID found: --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a", notebook.errors[0].message)

    def test_unique_i18n_guid(self):
        guid_a = "--i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a"
        command_a = f"""
            # MAGIC %md {guid_a}
            # MAGIC # Some Title""".strip()

        guid_b = "--i18n-9d06d80d-2381-42d5-8f9e-cc99ee3cd82a"
        command_b = f"""
            # MAGIC %md {guid_b}
            # MAGIC # Some Title""".strip()

        i18n_guid_map_a = {guid_a: "# MAGIC # Some Title"}
        i18n_guid_map_b = {guid_b: "# MAGIC # Some Title"}

        notebook = self.create_notebook()
        notebook.update_md_cells(language="Python", command=command_a, i=3, i18n_guid_map=i18n_guid_map_a, other_notebooks=[])
        notebook.update_md_cells(language="Python", command=command_b, i=4, i18n_guid_map=i18n_guid_map_b, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(0, notebook)

    def test_md_i18n_guid_replacement(self):
        command = """# MAGIC %md --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a\n# MAGIC # Some Title""".strip()

        i18n_guid_map = {"--i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a": "# MAGIC # Some Title"}

        notebook = self.create_notebook()
        actual = notebook.update_md_cells(language="Python", command=command, i=4, i18n_guid_map=i18n_guid_map, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(0, notebook)

        expected = """# MAGIC %md <i18n value="a6e39b59-1715-4750-bd5d-5d638cf57c3a"/>\n# MAGIC # Some Title""".strip()
        self.assertEqual(expected, actual)

    def test_md_sandbox_i18n_guid_replacement(self):
        command = """# MAGIC %md-sandbox --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a\n# MAGIC # Some Title""".strip()

        i18n_guid_map = {"--i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a": "# MAGIC # Some Title"}

        notebook = self.create_notebook()
        actual = notebook.update_md_cells(language="Python", command=command, i=4, i18n_guid_map=i18n_guid_map, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(0, notebook)

        expected = """# MAGIC %md-sandbox <i18n value="a6e39b59-1715-4750-bd5d-5d638cf57c3a"/>\n# MAGIC # Some Title""".strip()
        self.assertEqual(expected, actual)

    def test_i18n_sql(self):
        command = """-- MAGIC %md-sandbox --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a\n-- MAGIC # Some Title""".strip()

        i18n_guid_map = {"--i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a": "-- MAGIC # Some Title"}

        notebook = self.create_notebook()
        actual = notebook.update_md_cells(language="SQL", command=command, i=4, i18n_guid_map=i18n_guid_map, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(0, notebook)

        expected = """-- MAGIC %md-sandbox <i18n value="a6e39b59-1715-4750-bd5d-5d638cf57c3a"/>\n-- MAGIC # Some Title""".strip()
        self.assertEqual(expected, actual)

    def test_i18n_single_line(self):
        command = """-- MAGIC %md --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a # Some Title""".strip()

        notebook = self.create_notebook()
        notebook.update_md_cells(language="SQL", command=command, i=4, i18n_guid_map={"--i18n-TBD": "whatever"}, other_notebooks=[])

        self.assert_n_warnings(0, notebook)
        self.assert_n_errors(1, notebook)

        self.assertEqual("Cmd #5 | Expected MD to have more than 1 line of code with i18n enabled: %md --i18n-a6e39b59-1715-4750-bd5d-5d638cf57c3a # Some Title", notebook.errors[0].message)


if __name__ == '__main__':
    unittest.main()
