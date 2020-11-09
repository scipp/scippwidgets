# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import ipywidgets as widgets
from abc import ABC, abstractmethod


class IInputSpec(ABC):
    """
    Interfaces detailing which methods and properties as
    InputSpecifier must have.
    """
    @abstractmethod
    def validator(self, input):
        pass

    @abstractmethod
    def create_input_widget(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass


class InputSpec(IInputSpec):
    def __init__(self,
                 name,
                 validator=lambda input: input,
                 options=(),
                 tooltip='',
                 eval_input=False,
                 scope={}):
        self._name = name
        self._options = options
        self._tooltip = tooltip if tooltip else name

        if eval_input:
            self._scope = scope if scope else get_notebook_global_scope()
            self._validator = lambda input: validator(eval(input, scope))
        else:
            self._validator = validator

    def create_input_widget(self):
        return widgets.Combobox(placeholder=self._tooltip,
                                continuous_update=False,
                                options=self._options)

    def validator(self, input):
        return self._validator(input)

    @property
    def name(self):
        return self._name


def get_notebook_global_scope():
    """
    This gets the global scope of the notebook. It
    assumes the first module called __main__ on the stack
    is the correct one.
    """
    import inspect
    for module in inspect.stack():
        if module[0].f_globals['__name__'] == '__main__':
            return module[0].f_globals
