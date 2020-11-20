# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

from scipp_widgets.input import (Input, StringInput, ScippInputWithDim)
import scipp as sc
import numpy as np
import pytest
import ipywidgets


def test_Input_creates_widget_with_correct_properties():
    name = 'test_input'
    options = ('x', 'y', 'z')
    tooltip = 'input here'
    input = StringInput(function_arg_name=name,
                        options=options,
                        placeholder=tooltip)
    input.widget.value = 'user input'

    assert input.widget.options == options
    assert input.widget.placeholder == tooltip
    assert input.function_arguments == {'test_input': 'user input'}


def test_Input_evaluates_expression_in_scope():
    name = 'test_input'
    scope = {'test_obj': [1, 2, 3, 45]}
    input = Input(function_arg_name=name, scope=scope)
    input.widget.value = 'test_obj'

    assert input.function_arguments == {'test_input': [1, 2, 3, 45]}


def _create_scipp_obj():
    return sc.Dataset(
        {
            'alice':
            sc.Variable(['z', 'y', 'x'],
                        values=np.random.rand(10, 10, 10),
                        variances=0.1 * np.random.rand(10, 10, 10)),
        },
        coords={
            'x': sc.Variable(['x'], values=np.arange(11.0), unit=sc.units.m),
            'y': sc.Variable(['y'], values=np.arange(11.0), unit=sc.units.m),
            'z': sc.Variable(['z'], values=np.arange(11.0), unit=sc.units.m)
        })


def test_ScippInputWithDim_returns_correct_function_args():
    scipp_obj = _create_scipp_obj()
    function_args = ['arg1', 'arg2']
    scope = {'scipp_obj': scipp_obj}
    input = ScippInputWithDim(function_args, 'input-data', scope=scope)

    input.widget.children[0].value = 'scipp_obj'
    input.widget.children[1].value = 'y'

    assert input.function_arguments == {'arg1': scipp_obj, 'arg2': 'y'}


def test_ScippInputWithDim_throws_for_invalid_dimension():
    scipp_obj = _create_scipp_obj()
    function_args = ['arg1', 'arg2']
    scope = {'scipp_obj': scipp_obj}
    input = ScippInputWithDim(function_args, 'input-data', scope=scope)

    print(ipywidgets.__version__)
    input.widget.children[0].value = 'scipp_obj'
    input.widget.children[1].value = 'invalid'

    with pytest.raises(ValueError) as exp:
        input.function_arguments

    assert str(exp.value) == 'Dimension invalid does no exist in scipp_obj'


def test_ScippInputWithDim_throws_for_non_scipp_object():
    scipp_obj = [1, 2, 3, 4, 5]
    function_args = ['arg1', 'arg2']
    scope = {'scipp_obj': scipp_obj}
    input = ScippInputWithDim(function_args, 'input-data', scope=scope)

    input.widget.children[0].value = 'scipp_obj'

    with pytest.raises(ValueError):
        input.function_arguments
