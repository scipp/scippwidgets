# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import ipywidgets as widgets
import scipp as sc
from scipp.plot import plot
from .inputs import get_notebook_global_scope
from IPython.core.display import display, HTML
from typing import (Any, Mapping, Callable, Sequence, MutableMapping)


class FunctionWrapperWidget(widgets.Box):
    """
    Provides a simple graphical wrapper around a given callable.
    """
    def __init__(self, callable: Callable, name: str, inputs):
        """
        Parameters:
        callable (Callable): The function to call
        name: name of widget to display
        inputs (Input object): class containing input data
        """
        super().__init__()
        self.callable = callable
        self.inputs = inputs
        self.input_widgets = []
        self._setup_input_widgets(inputs)

        self.button = widgets.Button(description=name)
        self.button.on_click(self._on_button_clicked)

        self.output_area = widgets.Output()

        self.children = [
            widgets.VBox([
                widgets.HBox(self.input_widgets + [self.button]),
                self.output_area
            ])
        ]

    def _setup_input_widgets(self, inputs):
        """
        Creates a Combobox widget for each entry in the inputs dict.
        The placeholder is set based on the descriptions dict and the
        options are set based on the options dict.
        """
        for input in inputs:
            placeholder = input.tooltip
            option = input.options
            self.input_widgets.append(
                widgets.Combobox(placeholder=placeholder,
                                 continuous_update=False,
                                 options=option))

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
    def __init__(self, callable: Callable, name: str, inputs):
        """
        Parameters:
        callable (Callable): The function to call
        name: name of widget to display
        inputs (Input object): class containing input data
        """
        super().__init__(callable, name, inputs)
        self.scope = get_notebook_global_scope()

        self.output = widgets.Text(placeholder='output name',
                                   value='',
                                   continuous_update=False)

        self.children = [
            widgets.VBox([
                widgets.HBox(self.input_widgets + [self.output, self.button]),
                self.output_area
            ])
        ]

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
javascript_functions = {False: "hide()", True: "show()"}
button_descriptions = {False: "Show code", True: "Hide code"}


def toggle_code(state):
    """
    Toggles the JavaScript show()/hide() function on the div.input element.
    """

    output_string = "<script>$(\"div.input\").{}</script>"
    output_args = (javascript_functions[state], )
    output = output_string.format(*output_args)

    display(HTML(output))


def button_action(value):
    """
    Calls the toggle_code function and updates the button description.
    """

    state = value.new

    toggle_code(state)

    value.owner.description = button_descriptions[state]


def setup_code_hiding():
    """
    Sets up the hiding of code blocks in the notebook at
    any point after this is called. Toggled by the button
    this creates.
    """
    state = False
    toggle_code(state)

    button = widgets.ToggleButton(state,
                                  description=button_descriptions[state])
    button.observe(button_action, "value")
    return button
