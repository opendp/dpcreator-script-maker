from dpcreator_script_maker.dp_script_maker import DPCreatorScriptMaker as ScriptMaker
from dpcreator_script_maker.models import \
    (CUSTOM_ERROR_MESSAGES,
     Delta,
     Epsilon,
     PrivacyParameters)
from pydantic import ValidationError as PydanticValidationError
import dpcreator_script_maker.static_vals as dstatic
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))


class TestValidation(unittest.TestCase):

    def test_epsilon(self):
        """Test the Epsilon class"""

        # acceptable epsilons
        for epval in [0, 0.7, 1, 4.999]:
            e = Epsilon(**{'value': epval})
            self.assertEqual(e.value, epval)

        # warnings if epsilon is gt 5.0
        for epval in [5.000001, 6, 10, 1000]:
            with self.assertWarns(Warning) as context:
                _e = Epsilon(**{'value': epval})
            self.assertEqual(CUSTOM_ERROR_MESSAGES['epsilon_warning'], str(context.warning))

        # can't be negative
        with self.assertRaises(PydanticValidationError) as context:
            Epsilon(**{'value': -2})
        self.assertEqual(context.exception.errors()[0].get('msg'),
                         'Input should be greater than or equal to 0')

    def test_delta(self):
        """Test the Delta class"""

        # acceptable delta
        for dval in [dstatic.DELTA_10_POWER_NEG_5, dstatic.DELTA_10_POWER_NEG_6]:
            d = Delta(**{'value': dval})
            self.assertEqual(d.value, dval)

        # has to be less than or equal to 10^-5
        for dval2 in [0.2, 0.1, 0.001, 0.0001]:
            with self.assertRaises(PydanticValidationError) as context:
                _d = Delta(**{'value': dval2})
            self.assertEqual(context.exception.errors()[0].get('msg'),
                             'Input should be less than or equal to 0.00001')

        # can't be negative
        with self.assertRaises(PydanticValidationError) as context:
            _d = Delta(**{'value': -2})
        self.assertEqual(context.exception.errors()[0].get('msg'),
                         'Input should be greater than or equal to 0')

    def test_good_privacy_parameters(self):

        # All privacy parameters
        #
        privacy_parameters_input = {
            "total_epsilon": {"value": 2.5},
            "total_delta": {"value": .000005},
            "number_of_rows_public": True,
            "individual_in_at_most_one_row": False
        }

        p = PrivacyParameters(**privacy_parameters_input)
        self.assertEqual(p.model_dump(), privacy_parameters_input)

        # Privacy parameters without delta
        #
        privacy_parameters_input_2 = dict(privacy_parameters_input)
        privacy_parameters_input_2.pop('total_delta')  # remove total_delta

        p2 = PrivacyParameters(**privacy_parameters_input_2)
        p2_dict = p2.model_dump()

        # total_delta should be in the PrivacyParameters as "None"
        self.assertIn('total_delta', p2_dict)
        self.assertEqual(p2_dict['total_delta'], None)

        # check against the original input
        p2_dict.pop('total_delta')
        self.assertEqual(p2_dict, privacy_parameters_input_2)

        # Privacy parameters with booleans changed
        #
        privacy_parameters_input_3 = {
            "total_epsilon": {"value": 2.5},
            "total_delta": {"value": .000005},
            "number_of_rows_public": False,
            "individual_in_at_most_one_row": True
        }
        p3 = PrivacyParameters(**privacy_parameters_input_3)
        self.assertEqual(p3.model_dump(), privacy_parameters_input_3)

    @unittest.skip('skip for now')
    def test_bad_privacy_parameters(self):

        privacy_parameters_input = {
            "total_epsilon": {"value": 2.5},
            "total_delta": {"value": .000005},
            "number_of_rows_public": "blue",
            "individual_in_at_most_one_row": "sky"
        }

        p = PrivacyParameters(**privacy_parameters_input)


    def test_sum(self):
        self.assertEqual(2, 2)

    @unittest.skip('skipping')
    def test_init(self):
        sm = ScriptMaker()


if __name__ == '__main__':
    unittest.main()
