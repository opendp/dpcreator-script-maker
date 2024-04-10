"""
overall epsilon
"""
from pydantic import BaseModel, Field, ValidationError, conlist, confloat, field_validator
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
    var_type: Literal[*dstatic.ALLOWED_VAR_TYPES]  # ["Integer", "Float", "Categorical", "Boolean"]
    min: Optional[float] = None
    max: Optional[float] = None
    categories: Optional[List[Union[str, float]]] = None
    true_value: Optional[Union[str, float]] = None
    false_value: Optional[Union[str, float]] = None

    '''
    @validator('skycolor', pre=True)
    def convert_color(cls, value):
        if isinstance(value, str):
            if value.lower() == 'blue':
                return True
            elif value.lower() == 'yellow':
                return False
        return value

    @property
    def skycolor_str(self) -> str:
        return 'blue' if self.skycolor else 'yellow'
    '''
