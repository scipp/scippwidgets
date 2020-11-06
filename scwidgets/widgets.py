# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import ipywidgets as widgets
import scipp as sc
from scipp.plot import plot
from .inputs import get_notebook_global_scope
from IPython.core.display import display, HTML, Javascript
from typing import (Any, Mapping, Callable, Sequence, MutableMapping)

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


class FunctionWrapperWidget(widgets.Box):
    """
    Provides a simple graphical wrapper around a given callable.
    """
    def __init__(self, callable: Callable, name: str, inputs, hide_code=False):
        """
        Parameters:
        callable (Callable): The function to call
        name: name of widget to display
        inputs (Input object): class containing input data
        """
        super().__init__()
        self.layout.flex_flow = 'column'
        self.callable = callable
        self.inputs = inputs
        self.input_widgets = []
        self._setup_input_widgets(inputs)

        self.button = widgets.Button(description=name)
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
        Creates a Combobox widget for each entry in the inputs dict.
        The placeholder is set based on the descriptions dict and the
        options are set based on the options dict.
        """
        for input in inputs:
            self.input_widgets.append(input.create_input_widget())

    def _retrive_kwargs(self):
        kwargs = {
            input.name: input.validator(item.value)
            for input, item in zip(self.inputs, self.input_widgets)
        }
        return kwargs

    def _on_button_clicked(self, button):
        self.output_area.clear_output()
        with self.output_area:
            try:
                kwargs = self._retrive_kwargs()
            except ValueError as e:
                print(f'Invalid inputs: {e}')
                return

            self._process(kwargs)

    def _process(self, kwargs):
        display(self.callable(**kwargs))


class ProcessWidget(FunctionWrapperWidget):
    """
    Provides a simple graphical wrapper around a given callable.
    """
    def __init__(self, callable: Callable, name: str, inputs, hide_code=False):
        """
        Parameters:
        callable (Callable): The function to call
        name: name of widget to display
        inputs (Input object): class containing input data
        """
        super().__init__(callable, name, inputs, hide_code=hide_code)
        self.scope = get_notebook_global_scope()

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

            Returns: Output of the wrapped callable.
            """
        if self.output.value:
            output_name = self.output.value
        else:
            print('Invalid inputs: No output name specified')
            return

        self.scope[output_name] = self.callable(**kwargs)
        display(self.scope[output_name])


# Method to hide code blocks taken from
# https://stackoverflow.com/questions/27934885/how-to-hide-code-from-cells-in-ipython-notebook-visualized-with-nbviewer
