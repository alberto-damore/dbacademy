import unittest
from dbacademy.workspaces_3_0.uc_storage_config_class import UcStorageConfig


class TestUCStorageConfig(unittest.TestCase):

    def test_create(self):
        storage_config = UcStorageConfig(storage_root="def", storage_root_credential_id="ghi", region="jkl", owner="instructors")
        self.assertIsNone(storage_config.meta_store_name)
        self.assertEqual("def", storage_config.storage_root)
        self.assertEqual("ghi", storage_config.storage_root_credential_id)
        self.assertEqual("jkl", storage_config.region)

    # def test_create_meta_store_name(self):
    #     from dbacademy_test.workspaces_3_0 import test_assertion_error
    #
    #     # noinspection PyTypeChecker
    #     test_assertion_error(self, """The parameter "meta_store_name" must be a string value, found <class 'int'>.""", lambda: UcStorageConfig(meta_store_name=0, storage_root="def", storage_root_credential_id="ghi", region="jkl"))
    #     # noinspection PyTypeChecker
    #     test_assertion_error(self, """The parameter "meta_store_name" must be a string value, found <class 'NoneType'>.""", lambda: UcStorageConfig(meta_store_name=None, storage_root="def", storage_root_credential_id="ghi", region="jkl"))
    #     test_assertion_error(self, """The parameter "meta_store_name" must be specified, found "".""", lambda: UcStorageConfig(meta_store_name="", storage_root="def", storage_root_credential_id="ghi", region="jkl"))

    def test_create_storage_root(self):
        from dbacademy_test.workspaces_3_0 import test_assertion_error

        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "storage_root" must be a string value, found <class 'int'>.""", lambda: UcStorageConfig(storage_root=0, storage_root_credential_id="ghi", region="jkl", owner="instructors"))
        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "storage_root" must be a string value, found <class 'NoneType'>.""", lambda: UcStorageConfig(storage_root=None, storage_root_credential_id="ghi", region="jkl", owner="instructors"))
        test_assertion_error(self, """The parameter "storage_root" must be specified, found "".""", lambda: UcStorageConfig(storage_root="", storage_root_credential_id="ghi", region="jkl", owner="instructors"))

    def test_create_storage_root_credential_id(self):
        from dbacademy_test.workspaces_3_0 import test_assertion_error

        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "storage_root_credential_id" must be a string value, found <class 'int'>.""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id=0, region="jkl", owner="instructors"))
        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "storage_root_credential_id" must be a string value, found <class 'NoneType'>.""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id=None, region="jkl", owner="instructors"))
        test_assertion_error(self, """The parameter "storage_root_credential_id" must be specified, found "".""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id="", region="jkl", owner="instructors"))

    def test_create_region(self):
        from dbacademy_test.workspaces_3_0 import test_assertion_error

        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "region" must be a string value, found <class 'int'>.""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id="ghi", region=0, owner="instructors"))
        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "region" must be a string value, found <class 'NoneType'>.""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id="ghi", region=None, owner="instructors"))
        test_assertion_error(self, """The parameter "region" must be specified, found "".""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id="ghi", region="", owner="instructors"))

    def test_create_owner(self):
        from dbacademy_test.workspaces_3_0 import test_assertion_error

        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "owner" must be a string value, found <class 'int'>.""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id="ghi", region="jkl", owner=0))
        # noinspection PyTypeChecker
        test_assertion_error(self, """The parameter "owner" must be a string value, found <class 'NoneType'>.""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id="ghi", region="jkl", owner=None))
        test_assertion_error(self, """The parameter "owner" must be specified, found "".""", lambda: UcStorageConfig(storage_root="def", storage_root_credential_id="ghi", region="jkl", owner=""))


if __name__ == '__main__':
    unittest.main()
