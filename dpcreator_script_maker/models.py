"""
overall epsilon
"""
from pydantic import BaseModel, Field, ValidationError, conlist, confloat, validator
from typing import Union, List
import static_vals as dstatic

import warnings

class Epsilon(BaseModel):
    value: confloat(ge=dstatic.EPSILON_MIN)  # Non-negative float

    @validator('value')
    def check_value(cls, v):
        if v > 5:
            warnings.warn('Epsilon value is over 5. This is just a warning, not a validation error.')
        return v

class Delta(BaseModel):
    value: confloat(lt=dstatic.DELTA_0)  # Float less than 0

    @validator('value')
    def check_value(cls, v):
        if v > dstatic.DELTA_10_NEG_5:
            warnings.warn('Delta value is greater than 1e-95. This is just a warning, not a validation error.')
        return v

class PrivacyParameters(BaseModel):
    total_epsilon: Epsilon
    total_delta: Delta
    number_of_rows_public: bool
    individual_in_at_most_one_row: bool



class MyModel(BaseModel):
    epsilon: Epsilon

# Example usage
model = MyModel(epsilon={'value': 6})

# Accessing the model's attributes to trigger validation
print(model.epsilon.value)

class Column(BaseModel):
    type: str
    name: str
    min: int = None
    max: int = None
    categories: List[Union[str, int, float]] = None

    @validator('min', always=True)
    def check_min(cls, v, values):
        if values.get('type') != 'int' and v is not None:
            raise ValueError('min can only be used when type is int')
        return v

    @validator('max', always=True)
    def check_max(cls, v, values):
        if values.get('type') == 'int':
            if v is None or values.get('min') is None:
                raise ValueError('min and max are required for type int')
            if values['min'] >= v:
                raise ValueError('min must be less than max')
        return v

    @validator('categories', always=True)
    def check_categories(cls, v, values):
        if values.get('type') == 'categorical':
            if not v or not all(isinstance(item, (str, int, float)) for item in v):
                raise ValueError('categories is required and must be a non-empty list of strings, ints, or floats for type categorical')
        return v

class Data(BaseModel):
    epsilon: confloat(gt=1.0, lt=3.0) = Field(..., description="Should be a float between 1.0 and 3.0.")
    columns: conlist(Column, min_items=1) = Field(..., description="Should be a list with at least one entry.")

data = {
    "epsilon": 4.0,
    "columns": [{"type": "int", "name": "age", "min": 15, "max": 60}]
}

try:
    Data(**data)
    print("No validation errors found.")
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors():
        print(f"- {error['loc'][0]}: {error['msg']}")
