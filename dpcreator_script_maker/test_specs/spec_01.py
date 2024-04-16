"""
Test spec
"""
script_spec = \
{
    "name": "Plan 3",
    "differentially_private_library": {
        "name": "OpenDP",
        "url": "https://github.com/opendp/opendp",
        "version": "0.9.2"
    },
    "dataset": {
        "name": "Teacher Survey",
        "description": None,
        "variables": [
            {
            "name": "Income",
            "var_type": "Integer",
            "min": 0,
            "max": 500_000  # $5 M
            },
            {
                "name": "State",
                "var_type": "Categorical",
                "categories": ["CT", "ME", "MA", "NH", "RI", "VT"],  # handling large numbers of categories?
            },
            {
                "name": "smoker",
                "var_type": "Boolean",
            },
            {
                "name": "previous_diagnosis",
                "var_type": "Boolean",
                "true_value": 1,
                "false_value": 2
            }
        ]
    },
    "privacy_parameters": {
        "total_epsilon": 1.0,  # force to float? validate against columns
        "total_delta": 1e-05,  # can be None, validate against columns
        "number_of_rows_public": True,  # if False, need extra query
        "individual_in_at_most_one_row": True,  # Does each individual appear in only one row?"
    },
    "statistics": [
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
    ]
}
