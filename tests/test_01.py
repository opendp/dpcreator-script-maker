import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dpcreator_script_maker.dp_script_maker import DPCreatorScriptMaker as ScriptMaker

import unittest

class TestCalculations(unittest.TestCase):

    def test_sum(self):
        self.assertEqual(2, 2)

    def test_init(self):
        sm = ScriptMaker()

if __name__ == '__main__':
    unittest.main()