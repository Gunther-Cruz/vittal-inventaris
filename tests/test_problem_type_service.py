import unittest

from app import create_app
from app.domain.enums import ProblemScope
from app.extensions import db
from app.services.problem_type_service import ProblemTypeService


class ProblemTypeServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.problem_type_service = ProblemTypeService()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_problem_type_with_valid_code_and_scope(self):
        problem_type = self.problem_type_service.create_problem_type(
            {
                "code": "3010",
                "scope": "COMPUTER_CASE",
                "name": "Falha de energia do gabinete",
                "description": "Maintenance classification",
            }
        )

        self.assertIsNotNone(problem_type.id)
        self.assertEqual(3010, problem_type.code)
        self.assertEqual(ProblemScope.COMPUTER_CASE, problem_type.scope)
        self.assertTrue(problem_type.active)

    def test_rejects_duplicate_code(self):
        self._create_problem_type(code=3010, scope="COMPUTER_CASE")

        with self.assertRaisesRegex(ValueError, "Problem type code already exists."):
            self._create_problem_type(code=3010, scope="COMPUTER_CASE", name="Duplicated")

    def test_rejects_code_outside_supported_ranges(self):
        with self.assertRaisesRegex(ValueError, "between 1000 and 4999"):
            self._create_problem_type(code=999, scope="LABORATORY")

    def test_rejects_code_incompatible_with_scope(self):
        with self.assertRaisesRegex(ValueError, "incompatible with scope MONITOR"):
            self._create_problem_type(code=3010, scope="MONITOR")

    def test_rejects_invalid_scope(self):
        with self.assertRaisesRegex(ValueError, "Invalid problem scope."):
            self._create_problem_type(code=3010, scope="PRINTER")

    def test_rejects_blank_name(self):
        with self.assertRaisesRegex(ValueError, "Name is required."):
            self._create_problem_type(code=3010, scope="COMPUTER_CASE", name=" ")

    def test_update_changes_only_name_and_description(self):
        problem_type = self._create_problem_type(code=3010, scope="COMPUTER_CASE")

        self.problem_type_service.update_problem_type(
            problem_type,
            {
                "name": "Falha de inicializacao",
                "description": "Updated description",
            },
        )

        self.assertEqual(3010, problem_type.code)
        self.assertEqual(ProblemScope.COMPUTER_CASE, problem_type.scope)
        self.assertEqual("Falha de inicializacao", problem_type.name)
        self.assertEqual("Updated description", problem_type.description)

    def test_update_rejects_code_or_scope_change(self):
        problem_type = self._create_problem_type(code=3010, scope="COMPUTER_CASE")

        with self.assertRaisesRegex(ValueError, "code and scope cannot be changed"):
            self.problem_type_service.update_problem_type(
                problem_type,
                {
                    "code": "3020",
                    "name": "New name",
                    "description": "",
                },
            )

        with self.assertRaisesRegex(ValueError, "code and scope cannot be changed"):
            self.problem_type_service.update_problem_type(
                problem_type,
                {
                    "scope": "MONITOR",
                    "name": "New name",
                    "description": "",
                },
            )

    def test_set_status_and_list_by_scope(self):
        computer_case_type = self._create_problem_type(code=3010, scope="COMPUTER_CASE")
        self._create_problem_type(code=4110, scope="MONITOR")

        self.problem_type_service.set_problem_type_status(computer_case_type, False)

        all_computer_case_types = self.problem_type_service.list_problem_types({"scope": "COMPUTER_CASE"})
        active_computer_case_types = self.problem_type_service.list_active_by_scope("COMPUTER_CASE")

        self.assertEqual(1, len(all_computer_case_types))
        self.assertEqual([], active_computer_case_types)
        self.assertFalse(computer_case_type.active)

    def test_seed_initial_problem_types_is_idempotent(self):
        first = self.problem_type_service.seed_initial_problem_types()
        second = self.problem_type_service.seed_initial_problem_types()

        self.assertEqual(15, first["created"])
        self.assertEqual(0, first["skipped"])
        self.assertEqual(0, second["created"])
        self.assertEqual(15, second["skipped"])

    def test_get_problem_type_not_found(self):
        with self.assertRaises(LookupError):
            self.problem_type_service.get_problem_type(999)

    def _create_problem_type(self, code=3010, scope="COMPUTER_CASE", name="Falha tecnica"):
        return self.problem_type_service.create_problem_type(
            {
                "code": code,
                "scope": scope,
                "name": name,
                "description": "Test classification",
            }
        )


if __name__ == "__main__":
    unittest.main()
