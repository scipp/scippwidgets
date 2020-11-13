# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import ipywidgets as widgets
from scipp_widgets.validators import scipp_object_validator, has_attr_validator


class InputSpecComboboxBase():
    """
    Controls creation and validaton of user-input widgets.
    """
    def __init__(self, name, options=(), tooltip='', scope={}):
        """
        Parameters:
        name (str): Name of function argument this input corresponds to.
        validator (Callable[[str], Any]): Validator function.
        options (List[str]): List of dropdown options.
        tooltip (str): Widget placeholder text.
        scope (Dict[str: Any]): Non default scope to use for evaluation.
        """
        self._name = name
        self._options = options
        self._tooltip = tooltip if tooltip else name
        self._validator = lambda input: input
        self._widget = widgets.Combobox(placeholder=self._tooltip,
                                        continuous_update=False,
                                        options=self._options)

    def create_input_widget(self):
        """
        Creates and returns the relevant user-input ipywidget.
        """
        return self._widget

    def function_arguments(self):
        """
        Return function arguments as dict of arg_name: arg_value
        """
        return {self._name: self._validator(self._widget.value)}


class StringInputSpec(InputSpecComboboxBase):
    """
    Controls creation and validaton of user-input widgets.
    Processed raw string as input.
    """
    def __init__(self,
                 name,
                 validator=lambda input: input,
                 options=(),
                 tooltip='',
                 scope={}):
        """
        Parameters:
        name (str): Name of function argument this input corresponds to.
        validator (Callable[[str], Any]): Validator function.
        options (List[str]): List of dropdown options.
        tooltip (str): Widget placeholder text.
        scope (Dict[str: Any]): Non default scope to use for evaluation.
        """
        super().__init__(name, options, tooltip, scope)
        self._validator = validator


class InputSpec(InputSpecComboboxBase):
    """
    Controls creation and validaton of user-input widgets.
    Evaluates input string in scope
    """
    def __init__(self,
                 name,
                 validator=lambda input: input,
                 options=(),
                 tooltip='',
                 scope={}):
        """
        Parameters:
        name (str): Name of function argument this input corresponds to.
        validator (Callable[[str], Any]): Validator function.
        options (List[str]): List of dropdown options.
        tooltip (str): Widget placeholder text.
        scope (Dict[str: Any]): Non default scope to use for evaluation.
        """
        super().__init__(name, options, tooltip, scope)
        scope = scope if scope else get_notebook_global_scope()
        self._validator = lambda input: validator(eval(input, scope))


class ScippInputWithDimSpec():
    """
    Input widget which takes a scipp object and a linked
    dimension field.
    """
    def __init__(self, func_arg_names, data_name='data', scope={}):
        self._scope = scope if scope else get_notebook_global_scope()
        self._func_arg_names = func_arg_names
        self._scipp_obj_input = widgets.Text(placeholder=data_name,
                                             continuous_update=False)
        self._dimension_input = widgets.Combobox(placeholder='dim',
                                                 continuous_update=False)
        self._scipp_obj_input.observe(self._handle_scipp_obj_change,
                                      names='value')
        self._input_widget = widgets.HBox(
            [self._scipp_obj_input, self._dimension_input])
        self._validators = (self._scipp_obj_validator, self._dims_validator)
        self._allowed_dims = []

    def create_input_widget(self):
        return self._input_widget

    def function_arguments(self):
        return {
            name: validator(widget.value)
            for name, widget, validator in
            zip(self._func_arg_names, self._input_widget.children,
                self._validators)
        }

    def _handle_scipp_obj_change(self, change):
        try:
            scipp_obj = self._scipp_obj_validator(change['new'])
            dims = scipp_obj.dims
            self._dimension_input.options = dims
            self._allowed_dims = dims
        except ValueError:
            pass

    def _scipp_obj_validator(self, input):
        try:
            scipp_object = eval(input, self._scope)
            scipp_object_validator(scipp_object)
            has_attr_validator(scipp_object, 'dim')
            return scipp_object
        except SyntaxError:
            raise ValueError('data oject must be specified')

    def _dims_validator(self, input):
        if input in self._allowed_dims:
            return input
        else:
            raise ValueError(
                f'Dimension {input} does no exist in {self._scipp_obj_input.value}'
            )


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
