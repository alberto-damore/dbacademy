import unittest

from dbacademy_test.clients.databricks import DBACADEMY_UNIT_TESTS


class TestGroups(unittest.TestCase):

    def setUp(self) -> None:
        from dbacademy.clients import databricks

        self.__client = databricks.from_token(scope=DBACADEMY_UNIT_TESTS)
        self.tearDown()

    def tearDown(self) -> None:
        groups = self.client.scim.groups.list()
        for group in groups:
            display_name = group.get("displayName")
            if display_name not in ["users", "admins"]:
                group_id = group.get("id")
                self.client.scim.groups.delete_by_id(group_id)

    @property
    def client(self):
        return self.__client

    def test_create(self):
        user = self.client.scim.users.get_by_username("jacob.parr@databricks.com")
        group = self.client.scim.groups.create("dummies", members=[user.get("id")], entitlements=["allow-cluster-create"])
        
        self.assertIsNotNone(group.get("id"))
        self.assertEquals("dummies", group.get("displayName"))
        self.assertEquals("WorkspaceGroup", group.get("meta").get("resourceType"))

        entitlements = group.get("entitlements")
        self.assertEquals(1, len(entitlements))
        self.assertEquals({"value": "allow-cluster-create"}, entitlements[0])

        members = group.get("members")
        self.assertEquals(1, len(members))

        self.assertEqual(3, len(members[0]))
        self.assertEqual("Jacob Parr", members[0].get("display"))
        self.assertEqual("8598139271121446", members[0].get("value"))
        self.assertEqual("Users/8598139271121446", members[0].get("$ref"))

        groups = group.get("groups")
        self.assertEquals(0, len(groups))

        schemas = group.get("schemas")
        self.assertEquals(1, len(schemas))
        self.assertEquals("urn:ietf:params:scim:schemas:core:2.0:Group", schemas[0])

    def test_list(self):
        groups = self.client.scim.groups.list()
        self.assertEquals(2, len(groups))

        group_names = [g.get("displayName") for g in groups]
        self.assertTrue("users" in group_names)
        self.assertTrue("admins" in group_names)

    def test_get_by(self):
        group = self.client.scim.groups.get_by_name("admins")
        group_id = group.get("id")
        group = self.client.scim.groups.get_by_id(group_id)
        self.assertEquals("admins", group.get("displayName"))

        self.assertIsNone(self.client.scim.groups.get_by_id("asdf"))
        self.assertIsNone(self.client.scim.groups.get_by_name("asdf"))

    def test_delete(self):
        user = self.client.scim.users.get_by_username("jacob.parr@databricks.com")

        group = self.client.scim.groups.create("dummies", members=[user.get("id")], entitlements=["allow-cluster-create"])
        group_id = group.get("id")
        self.assertIsNone(self.client.scim.groups.delete_by_id(group_id))

        self.client.scim.groups.create("dummies", members=[user.get("id")], entitlements=["allow-cluster-create"])

        group = self.client.scim.groups.get_by_name("dummies")
        self.assertIsNotNone(group)

        group = self.client.scim.groups.delete_by_name("dummies")
        self.assertIsNone(group)

        group = self.client.scim.groups.get_by_name("dummies")
        self.assertIsNone(group)


if __name__ == "__main__":
    unittest.main()
