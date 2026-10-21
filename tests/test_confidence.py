import unittest
from apex_agent.schema import confidence, validate, FINDING


class ConfidenceTest(unittest.TestCase):
    def test_scores(self):
        self.assertEqual(confidence({"confidence_deductions": []}), 100)
        self.assertEqual(confidence({}), 100)
        self.assertEqual(confidence({"confidence_deductions": ["partial_path"]}), 80)
        self.assertEqual(confidence({"confidence_deductions": ["partial_path", "bounded_impact", "specific_state"]}), 55)
        self.assertEqual(confidence({"confidence_deductions": ["bounded_impact", "bounded_impact"]}), 85)

    def test_schema_rejects_unknown_deduction(self):
        with self.assertRaises(ValueError):
            validate(["vibes"], FINDING["properties"]["confidence_deductions"])


if __name__ == "__main__":
    unittest.main()
