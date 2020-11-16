# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import pathlib
import scipp as sc

scipp_object_mutable = (sc.DataArray, sc.Dataset, sc.Variable,
                        sc.DataArrayView, sc.DatasetView, sc.VariableView)

scipp_object = scipp_object_mutable + (
    sc.DataArrayConstView, sc.DatasetConstView, sc.VariableConstView)


class Validator():
    def __init__(self, boolean_expression):
        self.boolean_expression = boolean_expression

    def __call__(self, input):
        if not self.boolean_expression(input):
            raise ValueError(f'{input} is invalid')
        return input


class TypeValidator():
    def __init__(self, allowed_types):
        self.allowed_types = allowed_types

    def __call__(self, input):
        if not isinstance(input, self.allowed_types):
            raise ValueError(
                f'{input} of invalid type {type(input)}. Valid types are'
                f': {self.allowed_types}')
        return input


class ValueValidator():
    def __init__(self, allowed_values):
        self.allowed_values = allowed_values

    def __call__(self, input):
        if input not in self.allowed_values:
            raise ValueError(f'{input} is invalid. Allowed values are: '
                             f'{self.allowed_values}')
        return input


scipp_object_validator = TypeValidator(scipp_object)


def has_attr_validator(input, attr):
    if hasattr(input, attr):
        return input
    raise ValueError(f'{input} does not have require attribute {attr}')


class FilepathValidator():
    def __init__(self, data_directory=pathlib.Path.cwd()):
        self.data_directory = data_directory

    def __call__(self, input):
        path = pathlib.Path(input)

        if path.is_file():
            return str(path)

        path = self.data_directory / path

        if path.is_file():
            return str(path)

        raise ValueError(f'Filepath {input} was not found.')
