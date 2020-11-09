# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

from scipp_widgets.input_spec import InputSpec


def test_InputSpec_creates_widget_with_correct_properties():
    name = 'test_input'
    options = ('x', 'y', 'z')
    tooltip = 'input here'
    input_spec = InputSpec(name=name, options=options, tooltip=tooltip)

    input_widget = input_spec.create_input_widget()

    assert input_widget.options == options
    assert input_widget.placeholder == tooltip
    assert input_spec.name == name


def test_setting_eval_true_evaluates_expression_in_scope():
    name = 'test_input'
    scope = {'test_obj': [1, 2, 3, 45]}
    input_spec = InputSpec(name=name, eval_input=True, scope=scope)

    assert input_spec.validate('test_obj') == eval('test_obj', scope)
