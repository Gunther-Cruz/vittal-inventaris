import unittest

from app import create_app
from app.extensions import db


class ProblemTypeCommandsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_seed_problem_types_is_idempotent(self):
        first = self.runner.invoke(args=["problem-types", "seed"])
        second = self.runner.invoke(args=["problem-types", "seed"])

        self.assertEqual(0, first.exit_code)
        self.assertIn("15 created, 0 skipped", first.output)
        self.assertEqual(0, second.exit_code)
        self.assertIn("0 created, 15 skipped", second.output)


if __name__ == "__main__":
    unittest.main()
