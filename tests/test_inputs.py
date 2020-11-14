# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

from scipp_widgets.input_spec import InputSpec, StringInputSpec


def test_InputSpec_creates_widget_with_correct_properties():
    name = 'test_input'
    options = ('x', 'y', 'z')
    tooltip = 'input here'
    input_spec = StringInputSpec(function_arg_name=name,
                                 options=options,
                                 tooltip=tooltip)
    input_spec.widget.value = 'user input'

    assert input_spec.widget.options == options
    assert input_spec.widget.placeholder == tooltip
    assert input_spec.function_arguments == {'test_input': 'user input'}


def test_InputSpec_evaluates_expression_in_scope():
    name = 'test_input'
    scope = {'test_obj': [1, 2, 3, 45]}
    input_spec = InputSpec(function_arg_name=name, scope=scope)
    input_spec.widget.value = 'test_obj'

    assert input_spec.function_arguments == {'test_input': [1, 2, 3, 45]}
