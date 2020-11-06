# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import ipywidgets as widgets


class Input():
    def __init__(self,
                 name,
                 validator=lambda input: input,
                 options=(),
                 tooltip=''):
        self.name = name
        self.validator = validator
        self._options = options
        self._tooltip = tooltip if tooltip else name

    def create_input_widget(self):
        return widgets.Combobox(placeholder=self._tooltip,
                                continuous_update=False,
                                options=self._options)


class EvalInput():
    def __init__(self,
                 name,
                 validator=lambda input: input,
                 options=(),
                 tooltip=''):
        self.name = name
        self._validator = validator
        self._options = options
        self._tooltip = tooltip if tooltip else name
        self._scope = get_notebook_global_scope()

    def validator(self, input):
        return self._validator(eval(input, self._scope))

    def create_input_widget(self):
        return widgets.Combobox(placeholder=self._tooltip,
                                continuous_update=False,
                                options=self._options)


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
