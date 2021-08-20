# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import pytest
import tempfile
from scippwidgets.validators import (FilepathValidator, TypeValidator, ValueValidator)


def test_filepath_validator_returns_input_for_existing_filepath():
    filepath_validator = FilepathValidator()
    with tempfile.NamedTemporaryFile() as temp_file:
        converted_filepath = filepath_validator(temp_file.name)
        assert converted_filepath == temp_file.name


def test_filepath_validator_throws_value_error_for_unfound_file():
    filepath_validator = FilepathValidator()
    with pytest.raises(ValueError) as excinfo:
        filepath_validator('non_existent_file.txt')

    assert str(excinfo.value) == 'Filepath non_existent_file.txt was not found.'


def test_typed_validator_returns_object():
    test_object = [1, 2, 3, 4, 5]
    list_validator = TypeValidator((list, ))

    converted_object = list_validator(test_object)

    assert converted_object is test_object


def test_typed_validator_throws_exception_if_object_is_not_allowed_type():
    test_object = [1, 2, 3, 4, 5]
    dict_validator = TypeValidator((dict, ))

    with pytest.raises(ValueError) as excinfo:
        dict_validator(test_object)

    assert str(excinfo.value) == (f"{test_object} of invalid type <class 'list'>."
                                  " Valid types are: (<class 'dict'>,)")


def test_string_allowed_values_converter():
    string_allowed_values_validator = ValueValidator(('tof', ))
    converted_object = string_allowed_values_validator('tof')

    assert converted_object == 'tof'

    with pytest.raises(ValueError) as excinfo:
        string_allowed_values_validator('wavelength')

    assert str(
        excinfo.value) == f'wavelength is invalid. Allowed values are: {("tof", )}'
