import unittest
import ast
from fsm_extractor import FSMExtractor


class TestFSMExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = FSMExtractor(state_var="state")

    def test_constant_assignment(self):
        code = 'STATE_ARMING = "ARMING"\nSTATE_ACTIVE = "ACTIVE"'
        tree = ast.parse(code)
        self.extractor.visit(tree)
        self.assertEqual(self.extractor.constants["STATE_ARMING"], "ARMING")
        self.assertEqual(self.extractor.constants["STATE_ACTIVE"], "ACTIVE")

    def test_simple_transition(self):
        code = """
STATE_ARMING = "ARMING"
STATE_ACTIVE = "ACTIVE"
state = STATE_ARMING
if state == STATE_ARMING:
    if check_sensors():
        state = STATE_ACTIVE
"""
        tree = ast.parse(code)
        self.extractor.visit(tree)
        transitions = self.extractor.transitions
        self.assertIn(("ARMING", "ARMING", "active block"), transitions)
        self.assertIn(("ARMING", "ACTIVE", "check_sensors()"), transitions)

    def test_multiple_source_states(self):
        code = """
STATE_A = "A"
STATE_B = "B"
STATE_C = "C"
if state in (STATE_A, STATE_B):
    if trigger_condition():
        state = STATE_C
"""
        tree = ast.parse(code)
        self.extractor.visit(tree)
        transitions = self.extractor.transitions
        self.assertIn(("A", "A", "active block"), transitions)
        self.assertIn(("B", "B", "active block"), transitions)
        self.assertIn(("A", "C", "trigger_condition()"), transitions)
        self.assertIn(("B", "C", "trigger_condition()"), transitions)

    def test_trigger_extraction(self):
        code = """
state == "IDLE"

if state == "IDLE":
  if temperature > 100:
    state = "OVERHEAT"
"""
        tree = ast.parse(code)
        self.extractor.visit(tree)
        transitions = self.extractor.transitions
        self.assertIn(("IDLE", "IDLE", "active block"), transitions)
        self.assertIn(("IDLE", "OVERHEAT", "temperature > 100"), transitions)
