# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import pytest
from converters import (filepath_converter, scope_converter,
                        typed_scope_converter, string_allowed_values_converter)


@pytest.fixture
def temp_filepath(tmp_path, scope="module"):
    tmp_file = tmp_path / "test_file.txt"
    tmp_file.write_text('content')

    return tmp_file


def test_filepath_converter_returns_input_for_existing_filepath(temp_filepath):
    converted_filepath = filepath_converter(str(temp_filepath))

    assert converted_filepath == str(temp_filepath)


def test_filepath_converter_returns_full_path_if_provided_with_just_filename(
        temp_filepath):
    converted_filepath = filepath_converter(str(temp_filepath.name),
                                            data_directory=str(
                                                temp_filepath.parent))

    assert converted_filepath == str(temp_filepath)


def test_filepath_converter_throws_value_error_for_unfound_file(temp_filepath):
    with pytest.raises(ValueError) as excinfo:
        filepath_converter('non_existent_file.txt')

    assert str(
        excinfo.value) == 'Filepath non_existent_file.txt was not found.'


def test_scope_converter_returns_object_if_in_scope():
    scope = {'test_object': [1, 2, 3, 4, 5]}

    converted_object = scope_converter('test_object', scope)

    assert converted_object is scope['test_object']


def test_scope_converter_throws_exception_if_object_not_found():
    with pytest.raises(ValueError) as excinfo:
        scope_converter('test_object', {})

    assert str(excinfo.value
               ) == 'Object of name test_object does not exist within scope.'


def test_typed_scope_converter_returns_object_if_in_scope():
    scope = {'test_object': [1, 2, 3, 4, 5]}

    converted_object = typed_scope_converter('test_object', (list, ), scope)

    assert converted_object is scope['test_object']


def test_typed_scope_converter_throws_exception_if_object_is_not_allowed_type(
):
    scope = {'test_object': [1, 2, 3, 4, 5]}

    with pytest.raises(ValueError) as excinfo:
        typed_scope_converter('test_object', (dict, ), scope)

    assert str(
        excinfo.value) == 'test_object of invalid type. Valid types are: dict'


def test_string_allowed_values_converter():
    converted_object = string_allowed_values_converter('tof', ('tof', ))

    assert converted_object == 'tof'

    with pytest.raises(ValueError) as excinfo:
        string_allowed_values_converter('tof', ('wavelength', ))

    assert str(excinfo.value
               ) == 'tof not an allowed value. Valid values are: wavelength'
