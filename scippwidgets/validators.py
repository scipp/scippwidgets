# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import pathlib


class Validator():
    """
    Creates a validator callable from a predicate.
    """
    def __init__(self, predicate):
        self.predicate = predicate

    def __call__(self, input):
        if not self.predicate(input):
            raise ValueError(f'{input} is invalid')
        return input


class TypeValidator():
    """
    Creates a validator callable from tuple of allowed types.
    """
    def __init__(self, allowed_types):
        self.allowed_types = allowed_types

    def __call__(self, input):
        if not isinstance(input, self.allowed_types):
            raise ValueError(
                f'{input} of invalid type {type(input)}. Valid types are'
                f': {self.allowed_types}')
        return input


class ValueValidator():
    """
    Creates a validator callable from tuple of allowed values.
    """
    def __init__(self, allowed_values):
        self.allowed_values = allowed_values

    def __call__(self, input):
        if input not in self.allowed_values:
            raise ValueError(f'{input} is invalid. Allowed values are: '
                             f'{self.allowed_values}')
        return input


def ScippObjectValidator():
    import scipp as sc

    scipp_object = (sc.DataArray, sc.Dataset, sc.Variable)
    return TypeValidator(scipp_object)


class AttrValidator():
    """
    Checks whether an input has a specified attribute.
    """
    def __init__(self, required_attr):
        self._required_attr = required_attr

    def __call__(self, input):
        if hasattr(input, self._required_attr):
            return input

        raise ValueError(
            f'{input} does not have require attribute {self._required_attr}')


class FilepathValidator():
    """
    Checks whether a given file exists and has correct extensions.
    """
    def __init__(self, allowed_extensions=tuple()):
        self.allowed_extensions = allowed_extensions

    def __call__(self, input):
        path = pathlib.Path(input)

        if not path.is_file():
            raise ValueError(f'Filepath {input} was not found.')

        if self.allowed_extensions and str(
                path.suffix) not in self.allowed_extensions:
            raise ValueError(
                f'File has incorrect extension {path.suffix}.'
                f' Allowed extensions are {self.allowed_extensions}')

        return str(path)
