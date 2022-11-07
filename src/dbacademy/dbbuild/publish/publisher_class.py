from typing import List
from dbacademy import dbgems, common


class Publisher:
    from dbacademy.dbbuild.build_config_class import BuildConfig
    # from dbacademy.dbbuild.publish.translator_class import Translator
    from dbacademy.dbbuild.publish.notebook_def_class import NotebookDef

    VERSION_INFO_NOTEBOOK = "Version Info"

    KEEPERS = [".gitignore", "README.md", "LICENSE", "docs"]

    def __init__(self, build_config: BuildConfig):
        from dbacademy.dbbuild.build_config_class import BuildConfig

        # Various validation steps
        self.__validated = False
        self.__validated_repo_reset = True
        self.__changes_in_source_repo = None
        self.__changes_in_target_repo = None
        self.__created_docs = False
        self.__created_dbcs = False
        self.__validated_artifacts = False

        self.build_config = common.validate_type(build_config, "build_config", BuildConfig)

        self.client = build_config.client
        self.version = build_config.version
        self.core_version = build_config.core_version
        self.build_name = build_config.build_name

        self.source_dir = build_config.source_dir
        self.source_repo = build_config.source_repo

        self.target_dir = f"{self.source_repo}/Published/{self.build_config.name} - v{self.build_config.version}"
        self.target_repo_url = None

        self.temp_repo_dir = f"/Repos/Temp"
        self.temp_work_dir = f"/Workspace/Users/{build_config.username}/Temp"
        self.username = build_config.username

        self.i18n = build_config.i18n
        self.i18n_resources_dir = f"{self.source_repo}/Resources/{build_config.i18n_language}"
        self.i18n_language = build_config.i18n_language

        if build_config.i18n_language is None:
            self.common_language = "english"
        else:
            # Include the i18n code in the version.
            # This hack just happens to work for japanese and korean
            self.common_language = build_config.i18n_language.split("-")[0]

        self.notebooks = []
        self.__init_notebooks(build_config.notebooks.values())

        self.white_list = build_config.white_list
        self.black_list = build_config.black_list
        self.__validate_white_black_list()

    def __init_notebooks(self, notebooks) -> None:
        from datetime import datetime
        from dbacademy.dbbuild.publish.notebook_def_class import NotebookDef

        for notebook in notebooks:
            assert type(notebook) == NotebookDef, f"Expected the parameter \"notebook\" to be of type \"NotebookDef\", found \"{type(notebook)}\"."

            # Add the universal replacements
            notebook.replacements["version_number"] = self.version
            notebook.replacements["built_on"] = datetime.now().strftime("%b %-d, %Y at %H:%M:%S UTC")

            self.notebooks.append(notebook)

    def __validate_white_black_list(self) -> None:
        if self.white_list or self.black_list:
            assert self.white_list is not None, "The white_list must be specified when specifying a black_list"
            assert self.black_list is not None, "The black_list must be specified when specifying a white_list"

            notebook_paths = [n.path for n in self.notebooks]

            # Validate white and black lists
            for path in self.white_list:
                assert path not in self.black_list, f"The white-list path \"{path}\" was also found in the black-list."
                assert path in notebook_paths, f"The white-list path \"{path}\" does not exist in the complete set of notebooks.\n{notebook_paths}"

            for path in self.black_list:
                assert path not in self.white_list, f"The black-list path \"{path}\" was also found in the white-list."
                assert path in notebook_paths, f"The black-list path \"{path}\" does not exist in the complete set of notebooks.\n{notebook_paths}"

            for path in notebook_paths:
                assert path in self.white_list or path in self.black_list, f"The notebook \"{path}\" was not found in either the white-list or black-list."

    def create_resource_bundle(self, folder_name: str = None, target_dir: str = None) -> str:

        assert self.i18n_language is None, f"Resource bundles are created for the English translations only, found {self.i18n_language}"

        folder_name = folder_name or f"english-v{self.build_config.version}"
        target_dir = target_dir or f"{self.source_repo}/Resources"

        for notebook in self.notebooks:
            notebook.create_resource_bundle(folder_name, self.source_dir, target_dir)

        return f"""<html><body style="font-size:16px">
            <p><a href="/#workspace{target_dir}/{folder_name}/{Publisher.VERSION_INFO_NOTEBOOK}.md" target="_blank">Resource Bundle: {folder_name}</a></p>
        </body></html>"""

    def generate_notebooks(self, *, verbose=False, debugging=False, **kwargs) -> str:
        from ..publish.notebook_def_class import NotebookDef
        from ..build_utils_class import BuildUtils

        assert self.validated, f"Cannot publish notebooks until the publisher passes validation. Ensure that Publisher.validate() was called and that all assignments passed."

        if "mode" in kwargs:
            dbgems.print_warning(title="DEPRECATION WARNING", message=f"The parameter \"mode\" has been deprecated.\nPlease remove the parameter.")

        found_version_info = False
        main_notebooks: List[NotebookDef] = []

        for notebook in self.notebooks:
            if self.black_list is None or notebook.path not in self.black_list:
                found_version_info = True if notebook.path == Publisher.VERSION_INFO_NOTEBOOK else found_version_info
                main_notebooks.append(notebook)

        assert found_version_info, f"The required notebook \"{Publisher.VERSION_INFO_NOTEBOOK}\" was not found."

        print(f"Source: {self.source_dir}")
        print(f"Target: {self.target_dir}")
        print()
        print("Arguments:")
        print(f"  verbose =   {verbose}")
        print(f"  debugging = {debugging}")

        if self.black_list is None:
            print(f"  exclude:    none")
        else:
            self.black_list.sort()
            print(f"\n  exclude:    {self.black_list[0]}")
            for path in self.black_list[1:]:
                print(f"              {path}")

        if self.white_list is None:
            print(f"  include:    none")
        else:
            self.white_list.sort()
            print(f"\n  include:    {self.white_list[0]}")
            for path in self.white_list[1:]:
                print(f"              {path}")

        # Now that we backed up the version-info, we can delete everything.
        target_status = self.client.workspace().get_status(self.target_dir)
        if target_status is not None:
            BuildUtils.print_if(verbose, "-" * 80)
            BuildUtils.clean_target_dir(self.client, self.target_dir, verbose)

        for notebook in main_notebooks:
            notebook.publish(source_dir=self.source_dir,
                             target_dir=self.target_dir,
                             i18n_resources_dir=self.i18n_resources_dir,
                             verbose=verbose, 
                             debugging=debugging,
                             other_notebooks=self.notebooks)

        warnings = 0
        errors = 0

        print("-"*80)
        print(f"All done!")
        print()
        print(f"Found {warnings} warnings")
        print(f"Found {errors} errors")

        html = f"""<html><body style="font-size:16px">
                         <div><a href="{dbgems.get_workspace_url()}#workspace{self.target_dir}/{Publisher.VERSION_INFO_NOTEBOOK}" target="_blank">See Published Version</a></div>"""
        for notebook in main_notebooks:
            errors += len(notebook.errors)
            warnings += len(notebook.warnings)

            if len(notebook.warnings) > 0:
                html += f"""<div style="font-weight:bold; margin-top:1em">{notebook.path}</div>"""
                for warning in notebook.warnings:
                    html += f"""<div style="margin-top:1em; white-space: pre-wrap">{warning.message}</div>"""
        html += """</body></html>"""

        return html

    def create_published_message(self) -> str:
        from .advertiser import Advertiser
        from dbacademy.dbbuild.publish.publishing_info_class import PublishingInfo

        self.assert_validate_artifacts()

        advertiser = Advertiser(source_repo=self.source_repo,
                                name=self.build_config.name,
                                version=self.build_config.version,
                                change_log=self.build_config.change_log,
                                publishing_info=PublishingInfo(self.build_config.publishing_info),
                                common_language=None)
        return advertiser.html

    def validate(self, silent: bool = False) -> None:
        if not silent:
            print(f"Source: {self.source_dir}")
            print(f"Target: {self.target_dir}")
            print()

            if self.build_config.change_log is not None:
                self.build_config.change_log.print()
                print()

        self.__validated = True

    @property
    def validated(self) -> bool:
        # Both have to be true to be considered validated.
        return self.__validated and self.__validated_repo_reset

    def configure_target_repo(self, target_dir: str = None, target_repo_url: str = None, branch: str = "published", **kwargs) -> None:
        from ..build_utils_class import BuildUtils

        # Assume for now that we have failed. This overrides the default
        # of True meaning we have to succeed here to continue
        self.__validated_repo_reset = False

        new_target_dir = f"/Repos/Temp/{self.build_name}"
        if target_dir == new_target_dir:
            dbgems.print_warning(title="DEPRECATION WARNING", message=f"The value of the parameter \"target_dir\" is the same as the default value.\nConsider removing the parameter.")
        target_dir = target_dir or new_target_dir

        new_target_repo_url = f"https://github.com/databricks-academy/{self.build_name}.git"
        if target_repo_url == new_target_repo_url:
            dbgems.print_warning(title="DEPRECATION WARNING", message=f"The value of the parameter \"target_repo_url\" is the same as the default value.\nConsider removing the parameter.")
        target_repo_url = target_repo_url or new_target_repo_url

        if "target_url" in kwargs:
            dbgems.print_warning(title="DEPRECATION WARNING", message=f"The parameter \"target_url\" has been deprecated.\nUse \"target_repo_url\" instead.")
            target_repo_url = kwargs.get("target_url")

        self.target_dir = common.validate_type(target_dir, "target_dir", str)
        self.target_repo_url = common.validate_type(target_repo_url, "target_repo_url", str)

        BuildUtils.reset_git_repo(client=self.client, directory=self.target_dir, repo_url=self.target_repo_url, branch=branch, which=None)

        self.__validated_repo_reset = True

    def generate_published_docs(self) -> str:
        import os, shutil

        source_docs_path = f"{self.source_repo}/docs"
        target_docs_path = f"{self.target_dir}/docs/v{self.build_config.version}"

        print(f"Source: {source_docs_path}")
        print(f"Target: {target_docs_path}")

        if os.path.exists(f"/Workspace/{target_docs_path}"):
            shutil.rmtree(f"/Workspace/{target_docs_path}")

        shutil.copytree(src=f"/Workspace/{source_docs_path}",
                        dst=f"/Workspace/{target_docs_path}")

        print("-" * 80)
        for file in os.listdir(f"/Workspace/{target_docs_path}"):
            print(file)

        html = f"""<html><body style="font-size:16px">
                         <div><a href="{dbgems.get_workspace_url()}#workspace{target_docs_path}/index.html" target="_blank">See Published Version</a></div>
                   </body></html>"""
        return html

    # Used by notebooks
    # TODO Cannot define return type without circular dependencies
    def to_translator(self):
        from dbacademy.dbbuild.publish.translator_class import Translator
        assert self.validated, f"Cannot translate until the publisher's configuration passes validation. Ensure that Publisher.validate() was called and that all assignments passed"

        return Translator(self)

    # Used by notebooks
    # TODO Cannot define return type without circular dependencies
    def to_test_suite(self, test_type: str = None, keep_success: bool = False):
        from dbacademy.dbbuild.test.test_suite_class import TestSuite

        return TestSuite(build_config=self.build_config,
                         test_dir=self.target_dir,
                         test_type=test_type,
                         keep_success=keep_success)

    def __generate_html(self, notebook: NotebookDef) -> None:
        import time

        if notebook.test_round < 2:
            return  # Skip for rounds 0 & 1

        start = int(time.time())

        path = f"../Source/{notebook.path}"
        dbgems.dbutils.notebook.run(path, timeout_seconds=60 * 5, arguments={
            "version": self.build_config.version,
            dbgems.GENERATING_DOCS: "true"
        })

        print(f"Generated docs for \"{notebook.path}\"...({int(time.time()) - start} seconds)")

    def generate_source_docs(self, asynchronous: bool = True) -> None:
        from multiprocessing.pool import ThreadPool

        if asynchronous:
            with ThreadPool(len(self.build_config.notebooks)) as pool:
                pool.map(self.__generate_html, self.build_config.notebooks.values())
        else:
            for notebook in self.build_config.notebooks.values():
                self.__generate_html(notebook)

    def assert_created_dbcs(self) -> None:
        assert self.__created_dbcs, "The DBCS have not yet been created. See Publisher.create_dbcs()"

    def create_dbcs(self) -> str:
        from ..build_utils_class import BuildUtils

        assert self.validated, f"Cannot create DBCs until the publisher passes validation. Ensure that Publisher.validate() was called and that all assignments passed."
        self.assert_no_changes_in_target_repo()

        print(f"Exporting DBC from \"{self.target_dir}\"")
        data = self.build_config.client.workspace.export_dbc(self.target_dir)

        BuildUtils.write_file(data=data,
                              overwrite=False,
                              target_name="Distributions system (versioned)",
                              target_file=f"dbfs:/mnt/secured.training.databricks.com/distributions/{self.build_config.build_name}/v{self.build_config.version}/{self.build_config.build_name}-v{self.build_config.version}-notebooks.dbc")

        BuildUtils.write_file(data=data,
                              overwrite=False,
                              target_name="Distributions system (latest)",
                              target_file=f"dbfs:/mnt/secured.training.databricks.com/distributions/{self.build_config.build_name}/vLATEST/notebooks.dbc")

        BuildUtils.write_file(data=data,
                              overwrite=True,
                              target_name="workspace-local FileStore",
                              target_file=f"dbfs:/FileStore/tmp/{self.build_config.build_name}-v{self.build_config.version}/{self.build_config.build_name}-v{self.build_config.version}-notebooks.dbc")

        url = f"/files/tmp/{self.build_config.build_name}-v{self.build_config.version}/{self.build_config.build_name}-v{self.build_config.version}-notebooks.dbc"

        self.__created_dbcs = True

        return f"""<html><body style="font-size:16px"><div><a href="{url}" target="_blank">Download DBC</a></div></body></html>"""

    def assert_created_docs(self) -> None:
        assert self.__created_docs, "The docs have not yet been created. See Publisher.create_docs()"

    def create_docs(self) -> str:
        from dbacademy.dbbuild.publish.docs_publisher import DocsPublisher
        from dbacademy.dbbuild.publish.publishing_info_class import PublishingInfo

        self.assert_created_dbcs()

        info = PublishingInfo(self.build_config.publishing_info)
        translation = info.translations.get(self.common_language)
        docs_publisher = DocsPublisher(build_name=self.build_config.build_name,
                                       version=self.version,
                                       translation=translation)
        docs_publisher.process_pdfs()
        print()
        print("-"*80)
        print()
        docs_publisher.process_google_slides()
        html = docs_publisher.to_html()

        self.__created_docs = True
        return html

    def assert_validate_artifacts(self) -> None:
        assert self.__validated_artifacts, "The published artifacts have not been verified. See Publisher.validate_artifacts()"

    def validate_artifacts(self) -> None:
        from dbacademy.dbbuild.publish.artifact_validator_class import ArtifactValidator

        self.assert_created_docs()

        ArtifactValidator.from_publisher(self).validate_publishing_processes()

        self.__validated_artifacts = True

    def assert_no_changes_in_source_repo(self) -> None:
        method = "Publisher.validate_no_changes_in_source_repo()"
        assert self.__changes_in_source_repo is not None, f"The source repository was not tested for changes. Please run {method} to update the build state."
        assert self.__changes_in_source_repo == 0, f"Found {self.__changes_in_source_repo} changes(s) in the source repository. Please commit any changes before continuing and re-run {method} to update the build state."

    def validate_no_changes_in_source_repo(self, skip_validation=False) -> None:
        from ..build_utils_class import BuildUtils

        if skip_validation:
            dbgems.print_warning(f"SKIPPING VALIDATION", "The source directory is not being evaluated for pending changes")
            self.__changes_in_source_repo = 0

        else:
            repo_name = f"{self.build_name}-source.git"
            results = BuildUtils.validate_no_changes_in_repo(client=self.client,
                                                             build_name=self.build_name,
                                                             repo_url=f"https://github.com/databricks-academy/{repo_name}",
                                                             directory=self.source_repo)
            self.__changes_in_source_repo = len(results)
            self.assert_no_changes_in_source_repo()

    def assert_no_changes_in_target_repo(self) -> None:
        method = "Publisher.validate_no_changes_in_target_repo()"
        assert self.__changes_in_target_repo is not None, f"The source repository was not tested for changes. Please run {method} to update the build state."
        assert self.__changes_in_target_repo == 0, f"Found {self.__changes_in_target_repo} changes(s) in the target repository. Please commit any changes before continuing and re-run {method} to update the build state."

    def validate_no_changes_in_target_repo(self, skip_validation=False) -> None:
        from ..build_utils_class import BuildUtils

        if skip_validation:
            dbgems.print_warning(f"SKIPPING VALIDATION", "The target directory is not being evaluated for pending changes")
            self.__changes_in_target_repo = 0

        else:
            repo_name = f"{self.build_name}.git"
            results = BuildUtils.validate_no_changes_in_repo(client=self.client,
                                                             build_name=self.build_name,
                                                             repo_url=f"https://github.com/databricks-academy/{repo_name}",
                                                             directory=self.target_dir)
            self.__changes_in_target_repo = len(results)
            self.assert_no_changes_in_target_repo()
