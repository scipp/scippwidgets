# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import ipywidgets as widgets
from .inputs import get_notebook_global_scope, IInput, Input
from IPython.core.display import display, Javascript
from typing import Callable, Iterable, Dict, Any
import pathlib

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
    Toggles the visibilty of the code block, in which this is created.
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
    Abstract base class for scippwidgets.
    """
    def __init__(self,
                 wrapped_func: Callable,
                 inputs: Iterable[IInput],
                 button_name: str = 'Process',
                 layout='row wrap',
                 hide_code: bool = False):
        """
        :param wrapped_func: The function to call.
        :param inputs: List of input specifiers.
        :param button_name: Text to display on process button.
        :param layout: Controls the layout of widgets. Sets as the flex-flow
            property of the underlying container.
            Common useful options are: row, column, row wrap.
            For a full list of options see
            https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Styling.html
        :param hide_code: Flag controlling whether to hide code.
        """
        super().__init__()
        self.layout.flex_flow = 'column'
        self.callable = wrapped_func
        self.inputs = inputs
        self.input_widgets = []
        self._setup_input_widgets(inputs)

        self.button = widgets.Button(description=button_name)
        self.button.on_click(self._on_button_clicked)
        self.button_widgets = [self.button]
        if (hide_code):
            self.button_widgets += (HideCodeWidget(True), )

        self.output_area = widgets.Output()
        self.output_widgets = widgets.VBox([self.output_area])

        self.widget_area = widgets.Box(self.input_widgets + self.button_widgets)
        self.widget_area.layout.flex_flow = layout

        self.children = [self.widget_area, self.output_widgets]

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
                 button_name: str = 'Display',
                 layout: str = 'row wrap',
                 hide_code=False):
        super().__init__(wrapped_func, inputs, button_name, layout, hide_code)

    def _process(self, kwargs):
        display(self.callable(**kwargs))


def PlotWidget(hide_code=False, layout='row wrap'):
    import scipp as sc
    return DisplayWidget(wrapped_func=sc.plot.plot,
                         inputs=(Input('scipp_obj'), ),
                         button_name='Plot',
                         layout=layout,
                         hide_code=hide_code)


class ProcessWidget(WidgetBase):
    """
    Provides a simple graphical wrapper around a given callable,
    adding the return value to the notebooks scope.
    """
    def __init__(self,
                 wrapped_func: Callable,
                 inputs: Iterable[IInput],
                 button_name: str = 'Process',
                 hide_code: bool = False,
                 layout='row wrap'):
        super().__init__(wrapped_func,
                         inputs,
                         button_name,
                         hide_code=hide_code,
                         layout=layout)
        self.scope = get_notebook_global_scope()

        self.output = widgets.Text(placeholder='output name',
                                   value='',
                                   continuous_update=False)
        self.widget_area.children = self.input_widgets + [self.output
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


class LoadWidget(WidgetBase):
    """
    Provides a simple graphical wrapper around a load function,
    adding the return value to the notebooks scope labelled
    by file name.
    """
    def __init__(self,
                 wrapped_func: Callable,
                 inputs: Iterable[IInput],
                 button_name: str = 'Load',
                 layout='row wrap',
                 obj_name_generator: Callable[
                     [Dict[str, Any]],
                     str] = lambda kwargs: pathlib.Path(kwargs['filename']).stem,
                 hide_code: bool = False):
        """
        :param obj_name_factory: This is a callable
            which takes as input the kwargs passed to
            the load function and returns the name
            to use for the loaded object.
        """
        super().__init__(wrapped_func,
                         inputs,
                         button_name,
                         hide_code=hide_code,
                         layout=layout)
        self.scope = get_notebook_global_scope()
        self._obj_name_generator = obj_name_generator

    def _process(self, kwargs):
        """
        Calls the wrapped function using the
        parameter values specified.
        """
        output = self.callable(**kwargs)
        name = self._obj_name_generator(kwargs)
        self.scope[name] = output
