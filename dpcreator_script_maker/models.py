"""
overall epsilon
"""
from pydantic import \
    (BaseModel, Field,
     ValidationError,
     conlist,
     confloat,
     field_validator,
     model_validator,
     validator)
from typing import List, Literal, Optional, Union
import dpcreator_script_maker.static_vals as dstatic

import warnings

CUSTOM_ERROR_MESSAGES = {
    'epsilon_warning': "Epsilon shouldn't be greater than 5.0",
    'xx-delta_warning': "Delta shouldn't be greater than 1e-5."
}

class Epsilon(BaseModel):
    value: confloat(ge=0)  # Non-negative float

    @field_validator('value')
    @classmethod
    def check_value(cls, value):
        if value > dstatic.EPSILON_WARNING:
            warnings.warn(CUSTOM_ERROR_MESSAGES.get('epsilon_warning'))
        return value


class Delta(BaseModel):
    value: confloat(ge=0.0, le=dstatic.DELTA_10_POWER_NEG_5)  # >= .00001

class Bounds(BaseModel):
    """Object for the min/max bounds. Checks that max > min"""
    min: float
    max: float

    @model_validator(mode='after')
    def check_min_max_constraints(self):
        """Check that max is greater than min"""
        if self.min >= self.max:
            raise ValueError('Maximum value must be greater than minimum value.')
        return self


class ConfidenceLevel(BaseModel):
    value: Literal[*dstatic.CONFIDENCE_LEVELS]

    @field_validator('value')
    def valid_confidence_level(cls, value):
        if value not in dstatic.CONFIDENCE_LEVELS:
            raise ValueError(("Confidence level must be one of'"
                              f" {dstatic.CONFIDENCE_LEVELS}"))
        return value


class PrivacyParameters(BaseModel):
    total_epsilon: Epsilon
    total_delta: Optional[Delta] = None
    confidence_level: Optional[ConfidenceLevel] = None
    number_of_rows_public: bool
    individual_in_at_most_one_row: bool


class Variable(BaseModel):
    name: str
    # var_type: Literal[*dstatic.ALLOWED_VAR_TYPES]  # ["Integer", "Float", "Categorical", "Boolean"]
    var_type: Literal[*dstatic.ALLOWED_VAR_TYPES]
    bounds: Optional[Bounds] = None
    categories: Optional[List[Union[str, float]]] = None
    true_value: Optional[Union[str, float, bool]] = None
    false_value: Optional[Union[str, float, bool]] = None

    @model_validator(mode='after')
    def check_bound_types(self):
        """
        Check the Bounds (min/max) values in relation to var_type.
        Integer - make sure min/max are integers
        Float - allowed
        If var_type is NOT 'Integer' or 'Float':
            - "bounds" should be NOne
        """
        bounds = self.bounds

        # Make sure bounds are set for Integer and Float types
        #
        if self.var_type in [dstatic.VAR_TYPE_INTEGER or dstatic.VAR_TYPE_FLOAT]:
            if not bounds:
                raise ValueError((f"For '{self.var_type}' type, 'bounds' (min/max)"
                                 " must be defined."))
        else:
            # min and max shouldn't be defined for other var types (e.g. categorical, boolean, etc)
            if bounds:
                raise ValueError(f"For '{self.var_type}' type, both min and max should be None.")

        # If var type is an Integer, make sure the bounds are integers
        #
        if self.var_type == dstatic.VAR_TYPE_INTEGER:
            if not bounds.min.is_integer():
                raise ValueError((f"For variable type '{dstatic.VAR_TYPE_INTEGER}',"
                                  " 'min' must be an integer."))
            if not bounds.max.is_integer():
                raise ValueError((f"For variable type '{dstatic.VAR_TYPE_INTEGER}',"
                                  " 'max' must be an integer."))

        return self


    @model_validator(mode='after')
    def check_categorical_constraints(self):
        """
        When var_type is 'Categorical', make sure that 'categories" is populated.
        In addition, var_type is NOT 'Categorical', make sure that 'categories" is None.
        """
        var_type = self.var_type
        categories_val = self.categories

        if var_type == dstatic.VAR_TYPE_CATEGORICAL:
            if not categories_val or not isinstance(categories_val, list) or len(categories_val) == 0:
                raise ValueError(('"categories" must be set and not empty for "{dstatic.VAR_TYPE_CATEGORICAL}"'
                                  'type variables'))
        elif categories_val:
            raise ValueError(f'categories must only be set for "{dstatic.VAR_TYPE_CATEGORICAL}" type variables')

        return self

    @model_validator(mode='after')
    def check_boolean_constraints(self):
        var_type = self.var_type
        true_value = self.true_value
        false_value = self.false_value

        if var_type == dstatic.VAR_TYPE_BOOLEAN:
            if true_value is None and false_value is None:
                pass
                # this is okay, let the pydantic default Boolean value work
            elif true_value is None or false_value is None:
                # Only one value has been set
                #
                raise ValueError((f'For "{dstatic.VAR_TYPE_BOOLEAN}" type variables, either set both'
                                  ' "true_value" and "false_value" OR leave both empty. Do not set'
                                  ' just one of the values.'))
            elif true_value == false_value:
                # True and False shouldn't be equal
                #
                raise ValueError('"true_value" and "false_value" must be different.')
        return self


class Dataset(BaseModel):
    name: str
    description: Optional[str] = None
    variables: List[Variable] = Field(..., min_items=1)


class Statistic(BaseModel):
    var_name: str
    stat_type: Literal[*dstatic.DP_STATS_CHOICES]
    epsilon: Optional[Epsilon]
    confidence_level: Optional[ConfidenceLevel] = None
    delta: Optional[Delta] = None
    # bounds  # for now, default to specs in Variable
    # categories  # for now, default to specs in Variable

'''

{
            "variable": "Income",
            "statistic": "histogram",
            "confidence_level": 0.95,
            "epsilon": 0.1,  # optional
            "delta": None,  # optional
            "missing_value_handling": {
                "type": "insert_fixed",
                "fixed_value": 35
            }
        },
        {
            "statistic": "mean",
            "variable": "TypingSpeed",
            "epsilon": 0.25,
            "delta": None,
            "bounds": {
                "min": 3.0,
                "max": 30.0
            },
            "missing_value_handling": {
                "type": "insert_fixed",
                "fixed_value": 9.0
            },
            "confidence_level": 0.99
        }
'''