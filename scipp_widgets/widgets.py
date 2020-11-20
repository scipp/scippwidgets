# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import ipywidgets as widgets
from .inputs import get_notebook_global_scope, IInput, EvalInput
from IPython.core.display import display, Javascript
from typing import Any, MutableMapping, Callable, Iterable
import scipp as sc

javascript_functions = {False: "hide()", True: "show()"}


def toggle_code(state, output_widget=None):
    """
    Toggles the JavaScript show()/hide() function on the div.input element.
    """
    output_string = "this.element.closest('.cell').children('.input').{}"
    output_args = (javascript_functions[state], )
    output = output_string.format(*output_args)

    if (output_widget):
        output_widget.clear_output()
        with output_widget:
            display(Javascript(output))
    else:
        display(Javascript(output))


class HideCodeWidget(widgets.Box):
    """
    Toggles the visibilty of the code block.
    """
    def __init__(self, state):
        super().__init__()
        self.output_widget = widgets.Output()
        self.button = widgets.ToggleButton(not state, description='Py')
        self.button.observe(self._on_button_toggle, "value")
        self.button.layout.flex = '0 1 40px'
        self.button.layout.align_self = 'flex-end'

        self.children = [self.button, self.output_widget]
        self.layout.align_self = 'flex-end'
        toggle_code(not state)

    def _on_button_toggle(self, value):
        toggle_code(value.new, self.output_widget)


class WidgetBase(widgets.Box):
    """
    Abstract base class for scipp-widgets
    """
    def __init__(self,
                 wrapped_func: Callable,
                 inputs: Iterable[IInput],
                 button_name: str = '',
                 hide_code: bool = False):
        """
        Parameters:
        wrapped_func (Callable): The function to call
        inputs (list): class containing input data
        name (str): name of widget to display
        hide_code (bool): hide the code block containing this class
        """
        super().__init__()
        self.layout.flex_flow = 'column'
        self.callable = wrapped_func
        self.inputs = inputs
        self.input_widgets = []
        self._setup_input_widgets(inputs)

        button_name = button_name if button_name else wrapped_func.__name__
        self.button = widgets.Button(description=button_name)
        self.button.on_click(self._on_button_clicked)
        self.button_widgets = [self.button]
        if (hide_code):
            self.button_widgets += (HideCodeWidget(True), )

        self.output_area = widgets.Output()
        self.output_widgets = widgets.VBox([self.output_area])

        self.row_widgets = widgets.HBox(self.input_widgets +
                                        self.button_widgets)
        self.row_widgets.layout.flex_flow = 'row wrap'

        self.children = [self.row_widgets, self.output_widgets]

    def _setup_input_widgets(self, inputs):
        """
        Creates a user-input widget for each item in inputs
        """
        for spec in inputs:
            self.input_widgets.append(spec.widget)

    def _retrieve_kwargs(self):
        kwargs = {}
        for input in self.inputs:
            kwargs.update(input.function_arguments)

        # Remove entries with an empty string value
        # to allow default parameter values to kick
        # in if possible.
        {key: item for key, item in kwargs.items() if item != ''}
        return kwargs

    def _on_button_clicked(self, button):
        self.output_area.clear_output()
        with self.output_area:
            try:
                kwargs = self._retrieve_kwargs()
            except ValueError as e:
                print(f'Invalid inputs: {e}')
                return

            self._process(kwargs)

    def _process(self, kwargs):
        pass


class DisplayWidget(WidgetBase):
    """
    Provides a simple graphical wrapper around a given callable,
    displaying the return value.
    """
    def __init__(self,
                 wrapped_func: Callable,
                 inputs: Iterable[IInput],
                 button_name: str = '',
                 hide_code=False):
        """
        Parameters:
        wrapped_func (Callable): The function to call
        inputs (list): class containing input data
        name (str): name of widget to display
        hide_code (bool): hide the code block containing this class
        """
        super().__init__(wrapped_func, inputs, button_name, hide_code)

    def _process(self, kwargs):
        display(self.callable(**kwargs))


def PlotWidget(hide_code=False):
    return DisplayWidget(wrapped_func=sc.plot.plot,
                         inputs=(EvalInput('scipp_obj'), ),
                         button_name='plot',
                         hide_code=hide_code)


class ProcessWidget(WidgetBase):
    """
    Provides a simple graphical wrapper around a given callable,
    adding the return value to the notebooks scope.
    """
    def __init__(self,
                 wrapped_func: Callable,
                 inputs: Iterable[IInput],
                 button_name: str = '',
                 hide_code: bool = False,
                 scope: MutableMapping[str, Any] = {}):
        """
        Parameters:
        wrapped_func (Callable): The function to call
        inputs (list): class containing input data
        button_name (str): name of widget to display
        hide_code (bool): hide the code block containing this class
        """
        super().__init__(wrapped_func,
                         inputs,
                         button_name,
                         hide_code=hide_code)
        self.scope = scope if scope else get_notebook_global_scope()

        self.output = widgets.Text(placeholder='output name',
                                   value='',
                                   continuous_update=False)
        self.row_widgets.children = self.input_widgets + [
            self.output
        ] + self.button_widgets

    def _process(self, kwargs):
        """
        Calls the wrapped function using the
        parameter values specified.
        """
        if self.output.value:
            output_name = self.output.value
        else:
            print('Invalid inputs: No output name specified')
            return
        output = self.callable(**kwargs)
        self.scope[output_name] = output
        display(self.scope[output_name])
