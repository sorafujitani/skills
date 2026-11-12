import copy
import unittest
from control import operation_key, select_project


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.data = {"scope": "current_project", "current_project_id": "a", "projects": [
            {"id": "a", "title": "app", "workspaceRoot": "/code/app"},
            {"id": "b", "title": "app", "workspaceRoot": "/other/app"},
            {"id": "old", "title": "old", "archivedAt": "2026-01-01"}]}

    def test_default_is_current_project(self):
        self.assertEqual(select_project(self.data), {"action": "select", "project_id": "a"})

    def test_explicit_target_overrides_default(self):
        self.data["target"] = {"project_id": "b"}
        self.assertEqual(select_project(self.data)["project_id"], "b")

    def test_conflicting_selectors_do_not_fall_back(self):
        self.data["target"] = {"project_id": "a", "workspace_root": "/other/app"}
        self.assertEqual(select_project(self.data)["reason"], "no_match")

    def test_ambiguous_title_is_order_independent(self):
        self.data["target"] = {"title": "app"}
        expected = select_project(self.data)
        self.data["projects"].reverse()
        self.assertEqual(select_project(self.data), expected)
        self.assertEqual(expected["action"], "clarify")

    def test_missing_folder_requires_verification_not_creation(self):
        self.data["target"] = {"workspace_root": "/new"}
        self.assertEqual(select_project(self.data)["action"], "verify_folder")

    def test_unknown_id_is_not_registered_or_replaced(self):
        self.data["target"] = {"project_id": "missing"}
        self.assertEqual(select_project(self.data)["reason"], "no_match")

    def test_archived_target_is_not_selected(self):
        self.data["target"] = {"project_id": "old"}
        self.assertEqual(select_project(self.data)["action"], "clarify")

    def test_cross_project_without_target_does_not_guess(self):
        self.data["scope"] = "cross_project"
        self.assertEqual(select_project(self.data)["reason"], "target_required")

    def test_duplicate_ids_require_new_snapshot(self):
        self.data["projects"].append(self.data["projects"][0])
        with self.assertRaises(ValueError):
            select_project(self.data)


class KeyTests(unittest.TestCase):
    def setUp(self):
        self.data = dict(environment_id="local-1", controller_id="ctl-1", request_id="msg-1",
                         assignment_id="a1", operation="launch", revision=1,
                         payload={"projectId": "a", "title": "Task", "message": "Do work"})

    def test_same_operation_has_same_key_despite_json_order(self):
        other = dict(reversed(list(self.data.items())))
        other["payload"] = dict(reversed(list(self.data["payload"].items())))
        self.assertEqual(operation_key(self.data), operation_key(other))

    def test_changed_payload_is_detectable_without_changing_retry_key(self):
        old = operation_key(self.data)
        self.data["payload"]["message"] = "Different work"
        new = operation_key(self.data)
        self.assertEqual(old["clientRequestId"], new["clientRequestId"])
        self.assertNotEqual(old["payload_sha256"], new["payload_sha256"])

    def test_new_request_revision_assignment_or_environment_has_new_key(self):
        old = operation_key(self.data)["clientRequestId"]
        for key, value in [("request_id", "msg-2"), ("revision", 2),
                           ("assignment_id", "a2"), ("environment_id", "remote")]:
            with self.subTest(key=key):
                other = copy.deepcopy(self.data)
                other[key] = value
                self.assertNotEqual(old, operation_key(other)["clientRequestId"])

    def test_invalid_revision_rejected(self):
        for revision in [0, -1, True, "1"]:
            self.data["revision"] = revision
            with self.assertRaises(ValueError):
                operation_key(self.data)


if __name__ == "__main__":
    unittest.main()
