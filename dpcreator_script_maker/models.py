"""
overall epsilon
"""
from pydantic import \
    (BaseModel, Field,
     ValidationError,
     conlist,
     confloat,
     field_validator, model_validator)
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


class PrivacyParameters(BaseModel):
    total_epsilon: Epsilon
    total_delta: Optional[Delta] = None
    number_of_rows_public: bool
    individual_in_at_most_one_row: bool

class Variable(BaseModel):
    name: str
    # var_type: Literal[*dstatic.ALLOWED_VAR_TYPES]  # ["Integer", "Float", "Categorical", "Boolean"]
    var_type: Literal[*dstatic.ALLOWED_VAR_TYPES]
    min: Optional[float] = None
    max: Optional[float] = None
    categories: Optional[List[Union[str, float]]] = None
    true_value: Optional[Union[str, float, bool]] = None
    false_value: Optional[Union[str, float, bool]] = None

    @model_validator(mode='after')
    def check_min_max_constraints(self):
        """
        Check the min/max values in relations to var_type, including the following constraints:
        - When var_type is either 'Integer' or 'Float':
            - min/max should both be populated
            - max should be greather than min
            - If var_type is 'Integer', min/max should be convertible to integers
        - If var_type is NOT 'Integer' or 'Float':
            - min/max should both be None
        """
        var_type = self.var_type
        min_val = self.min
        max_val = self.max

        # Validating for Integer and Float types
        if var_type in [dstatic.VAR_TYPE_INTEGER, dstatic.VAR_TYPE_FLOAT]:
            if min_val is None or max_val is None:
                raise ValueError(f"For '{var_type}' type, both min and max must be defined.")

            # Ensure min and max are integers if var_type is Integer
            if var_type == 'Integer':
                if min_val and not min_val.is_integer():
                    raise ValueError(f"For '{dstatic.VAR_TYPE_INTEGER}' type, min must be an integer.")
                if max_val and not max_val.is_integer():
                    raise ValueError(f"For '{dstatic.VAR_TYPE_INTEGER}' type, max must be an integer.")

            # Ensure min and max are floats if var_type is Float
            if var_type == 'Float':
                if not isinstance(min_val, float) or not isinstance(max_val, float):
                    if isinstance(min_val, int):  # Allow integers as valid floats
                        min_val = float(min_val)
                        self.min = min_val
                    if isinstance(max_val, int):
                        max_val = float(max_val)
                        self.max = max_val
                    else:
                        raise ValueError(
                            f"For '{dstatic.VAR_TYPE_FLOAT}' type, both min and max must be floats or integers convertible to floats.")

            # Check that max is greater than min
            if max_val <= min_val:
                raise ValueError("max must be greater than min.")

        # Ensuring min and max are None for non-numeric types
        elif var_type in [dstatic.VAR_TYPE_CATEGORICAL, dstatic.VAR_TYPE_BOOLEAN]:
            if min_val is not None or max_val is not None:
                raise ValueError(f"For '{var_type}' type, both min and max should be None.")

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
