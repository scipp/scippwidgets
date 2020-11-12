# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

from scipp_widgets.widgets import (DisplayWidget, ProcessWidget)
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