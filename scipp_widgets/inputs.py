# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew
import ipywidgets as widgets
from scipp_widgets.validators import ScippObjectValidator, AttrValidator
from typing import Any, Sequence, Callable
from abc import ABC, abstractmethod
import os


def _wrapped_eval(input, scope):
    try:
        return eval(input, scope)
    except NameError:
        raise ValueError(f"Object of name '{input}' not found in scope.")


class IInput(ABC):
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


class SingleInput(IInput):
    def __init__(self,
                 func_arg_name: str,
                 widget_type=widgets.Combobox,
                 validator: Callable[[str], Any] = lambda input: input,
                 **kwargs):
        """
        :param function_arg_name: Name of function argument this
            input corresponds to.
        :param widget_type: Type of widget to construct for this input.
        :param validator: Validator function.
        :param kwargs: kwargs to pass to widget constructor.
        :type widget_type:  ipywidget
        """
        self._name = func_arg_name
        self._widget = widget_type(**kwargs)
        self._validator = validator
        if 'placeholder' not in kwargs:
            self._widget.placeholder = func_arg_name

    @property
    def function_arguments(self):
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


class TextInput(SingleInput):
    """
    Controls creation and validaton of user-input widgets.
    Processed raw string as input.
    """
    def __init__(self,
                 function_arg_name: str,
                 validator: Callable[[str], str] = lambda input: input,
                 **kwargs):
        self._name = function_arg_name
        self._widget = widgets.Combobox(**kwargs)
        self._validator = validator
        if 'placeholder' not in kwargs:
            self._widget.placeholder = function_arg_name


class Input(SingleInput):
    """
    Controls creation and validaton of user-input widgets.
    Evaluates input string in scope
    """
    def __init__(self,
                 function_arg_name: str,
                 validator: Callable[[Any], Any] = lambda input: input,
                 **kwargs):
        """
        :param function_arg_name: Name of function argument this
            input corresponds to.
        :param widget_type: Type of widget to construct for this input.
        :param validator: Validator function.
        :param kwargs: kwargs to pass to widget constructor.
        :type widget_type:  ipywidget
        """
        self._name = function_arg_name
        self._widget = widgets.Combobox(**kwargs)
        self.scope = get_notebook_global_scope()
        self._validator = lambda input: validator(
            _wrapped_eval(input, self.scope))
        if 'placeholder' not in kwargs:
            self._widget.placeholder = function_arg_name


scipp_object_validator = ScippObjectValidator()
has_dim_validator = AttrValidator('dims')


class ScippInputWithDim(IInput):
    """
    Input widget which takes a scipp object and a linked
    dimension field.
    """
    def __init__(self,
                 func_arg_names: Sequence[str] = ('x', 'dim'),
                 data_name: str = 'data',
                 **kwargs):
        self._scope = get_notebook_global_scope()
        self._func_arg_names = func_arg_names
        self._scipp_obj_input = widgets.Text(placeholder=data_name,
                                             continuous_update=False,
                                             **kwargs)
        self._dimension_input = widgets.Combobox(placeholder='dim',
                                                 continuous_update=False,
                                                 **kwargs)
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
        has_dim_validator(scipp_object)
        return scipp_object

    def _dims_validator(self, input):
        if not input:
            raise ValueError('No dimension selected')
        if input in self._allowed_dims:
            return input
        else:
            raise ValueError(f'Dimension {input} does no exist in'
                             f' {self._scipp_obj_input.value}')


class FileInput(IInput):
    """
    Allows the user to browse to a file or directory.
    Returning the filepath as a string.
    """
    def __init__(self,
                 function_arg_name: str,
                 default_directory: str = os.getcwd(),
                 validator: Callable[[Any], Any] = lambda value: value,
                 file_filter: str = '',
                 show_only_dirs: bool = False):
        """
        :param function_arg_name: Name of function argument this
            input corresponds to.
        :default_directory: Directory to start browseing in.
        :validator: Validator function.
        :file_filter: String to use to filter displayed files.
            Will only display files which contain the filter string
            string as a substring.
        :param show_only_dirs: If True will only display
            and allow selection of directories.
        """
        from ipyfilechooser import FileChooser
        self._widget = FileChooser(default_directory,
                                   select_desc='Select file',
                                   select_default=True,
                                   change_desc='Select file',
                                   file_filter=f'*{file_filter}*',
                                   show_only_dirs=show_only_dirs)
        self._widget.use_dir_icons = True
        self._param_name = function_arg_name
        self._validator = validator

    @property
    def widget(self):
        return self._widget

    @property
    def function_arguments(self):
        return {self._param_name: self._validator(self._widget.selected)}


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
