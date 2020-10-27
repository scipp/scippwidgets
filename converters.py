# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import scipp as sc
import pathlib


def filepath_converter(filepath, data_directory=pathlib.Path.cwd()):
    """
    Checks the validity of the filepath provided,
    returns it is valid. Otherwise tries to form a valid
    filepath assuming a filename has been provided instead.

    Throws if file not found.
    """
    path = pathlib.Path(filepath)

    if path.is_file():
        return filepath

    path = data_directory / path

    if path.is_file():
        return str(path)

    raise ValueError(f'Filepath {filepath} was not found.')


def scope_converter(object_name, scope={}):
    """
    Attempts to convert the string input into an object by 
    assuming it names an object in the provided scope.

    Throws if not object of correct name found.
    """
    if object_name in scope:
        return scope[object_name]

    raise ValueError(
        f'Object of name {object_name} does not exist within scope.')
