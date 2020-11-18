# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

from scipp_widgets.widgets import (DisplayWidget, ProcessWidget)
from scipp_widgets.input_spec import StringInputSpec
import pytest


@pytest.fixture(autouse=True)
def no_display(monkeypatch):
    """
    Remove IPython.core.display.display for all tests.
    This does not appear to be strictly neccecary but feels safer
    to do so anyway.
    """
    def display_stub(input):
        pass

    monkeypatch.setattr("scipp_widgets.widgets.display", display_stub)


def test_can_create_and_run_display_widget():
    def test_func():
        return 'func_return'

    widget = DisplayWidget(test_func, [])
    widget._on_button_clicked(0)


def test_can_create_and_run_process_widget():
    def test_func():
        return 'func_return'

    scope = {'test': 'one'}

    widget = ProcessWidget(test_func, [], scope=scope)
    widget.output.value = 'obj_name'
    widget._on_button_clicked(0)

    assert scope['obj_name'] == 'func_return'


def test_function_with_args_and_kwargs():
    """
    Checking that different the different parameter types available
    in python work. Note currently does not support POSITIONAL_ONLY or *arg
    params. See https://docs.python.org/3/library/inspect.html#inspect.Parameter
    """
    def test_func(p_or_k='io', k_only='k_only', **kwargs):
        return f'{p_or_k} {k_only} {kwargs}'

    scope = {'test': 'one'}
    input_1 = StringInputSpec('p_or_k')
    input_2 = StringInputSpec('k_only')
    input_3 = StringInputSpec('var_keyword')
    widget = ProcessWidget(test_func, [input_1, input_2, input_3], scope=scope)
    widget.output.value = 'obj_name'
    input_1.widget.value = 'input_1'
    input_2.widget.value = 'input_2'
    input_3.widget.value = 'input_3'

    widget._on_button_clicked(0)

    assert scope['obj_name'] == "input_1 input_2 {'var_keyword': 'input_3'}"


def test_default_func_args_used_if_they_exist():
    def test_func(arg1, arg2='input_2'):
        return f'{arg1} {arg2}'

    scope = {'test': 'one'}
    input_1 = StringInputSpec('arg1')
    input_2 = StringInputSpec('arg2')
    widget = ProcessWidget(test_func, [input_1, input_2], scope=scope)
    widget.output.value = 'obj_name'
    input_1.widget.value = 'input_1'
    input_2.widget.value = ''

    widget._on_button_clicked(0)

    assert scope['obj_name'] == "input_1 input_2"
