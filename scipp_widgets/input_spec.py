# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import ipywidgets as widgets
from scipp_widgets.validators import scipp_object_validator, has_attr_validator
from typing import Any, Sequence, MutableMapping, Dict, Callable
from abc import ABC, abstractmethod


def _wrapped_eval(input, scope):
    try:
        return eval(input, scope)
    except NameError:
        raise ValueError(f"Object of name '{input}' not found in scope.")


class IInputSpec(ABC):
    """
    Interfaces detailing which methods and properties an
    input specification must have.
    """
    @property
    @abstractmethod
    def widget(self):
        pass

    @property
    @abstractmethod
    def function_arguments(self):
        pass


class InputSpecWidgetWrapper(IInputSpec):
    def __init__(self,
                 func_arg_name,
                 widget=widgets.Combobox,
                 validator=lambda input: input,
                 **kwargs):
        self._name = func_arg_name
        self._widget = widget(**kwargs)
        self._validator = validator

    @property
    def function_arguments(self) -> Dict[str, Any]:
        """
        Return function arguments as dict of arg_name: arg_value
        """
        if self.widget.value:
            return {self._name: self._validator(self.widget.value)}
        else:
            return {}

    @property
    def widget(self):
        """
        Returns constructed used-input widget
        """
        return self._widget


class StringInputSpec(InputSpecWidgetWrapper):
    """
    Controls creation and validaton of user-input widgets.
    Processed raw string as input.
    """
    def __init__(self,
                 function_arg_name: str,
                 validator: Callable[[str], str] = lambda input: input,
                 **kwargs):
        """
        Parameters:
        function_arg_name (str): Name of function argument this
        input corresponds to.
        validator (Callable[[str], Any]): Validator function.
        options (List[str]): List of dropdown options.
        tooltip (str): Widget placeholder text.
        scope (Dict[str: Any]): Non default scope to use for evaluation.
        """
        super().__init__(function_arg_name,
                         widget=widgets.Combobox,
                         validator=validator,
                         **kwargs)


class InputSpec(InputSpecWidgetWrapper):
    """
    Controls creation and validaton of user-input widgets.
    Evaluates input string in scope
    """
    def __init__(self,
                 function_arg_name: str,
                 validator: Callable[[Any], Any] = lambda input: input,
                 scope: MutableMapping[str, Any] = {},
                 **kwargs):
        """
        Parameters:
        function_arg_name (str): Name of function argument
        this input maps to.
        validator (Callable[[str], Any]): Validator function.
        options (List[str]): List of dropdown options.
        tooltip (str): Widget placeholder text.
        scope (Dict[str: Any]): Non default scope to use for evaluation.
        """
        super().__init__(function_arg_name,
                         widget=widgets.Combobox,
                         validator=validator,
                         **kwargs)
        scope = scope if scope else get_notebook_global_scope()
        self._validator = lambda input: validator(_wrapped_eval(input, scope))


class ScippInputWithDimSpec(IInputSpec):
    """
    Input widget which takes a scipp object and a linked
    dimension field.
    """
    def __init__(self,
                 func_arg_names: Sequence[str],
                 data_name: str = 'data',
                 scope: MutableMapping[str, Any] = {}):
        self._scope = scope if scope else get_notebook_global_scope()
        self._func_arg_names = func_arg_names
        self._scipp_obj_input = widgets.Text(placeholder=data_name,
                                             continuous_update=False)
        self._dimension_input = widgets.Combobox(placeholder='dim',
                                                 continuous_update=False)
        self._scipp_obj_input.observe(self._handle_scipp_obj_change,
                                      names='value')
        self._widget = widgets.HBox(
            [self._scipp_obj_input, self._dimension_input])
        self._validators = (self._scipp_obj_validator, self._dims_validator)
        self._allowed_dims = []

    @property
    def function_arguments(self):
        return {
            name: validator(widget.value)
            for name, widget, validator in zip(
                self._func_arg_names, self.widget.children, self._validators)
            if widget.value
        }

    @property
    def widget(self):
        return self._widget

    def _handle_scipp_obj_change(self, change):
        try:
            scipp_obj = self._scipp_obj_validator(change['new'])
            dims = scipp_obj.dims
            self._dimension_input.options = dims
            self._allowed_dims = dims
        except ValueError:
            pass

    def _scipp_obj_validator(self, input):
        scipp_object = _wrapped_eval(input, self._scope)
        scipp_object_validator(scipp_object)
        has_attr_validator(scipp_object, 'dims')
        return scipp_object

    def _dims_validator(self, input):
        if not input:
            raise ValueError('No dimension selected')
        if input in self._allowed_dims:
            return input
        else:
            raise ValueError(f'Dimension {input} does no exist in'
                             f' {self._scipp_obj_input.value}')


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
