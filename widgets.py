# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2020 Scipp contributors (https://github.com/scipp)
# @file
# @author Matthew Andrew

import ipywidgets as widgets
import scipp as sc
from scipp.plot import plot
import IPython.display as disp


class ProcessWidget(widgets.Box):
    """
    A this widget wrapper around a callable.
    """
    def __init__(self,
                 scope,
                 callable,
                 name,
                 inputs,
                 descriptions={},
                 options={}):
        """
        Parameters:
        scope (dict): The scope you wish to add the outputs of the function to
        callable (Callable): The function to call
        name: name of widget to display
        inputs (dict): dict of parameter_name: paramter_converter
        descriptions (dict): dict of parameter_name: paramter_description. 
            If a parameter_name does not appear in the dict if will be used as it's own description
        options (dict): a dict of parameter_name: parameter_options if you wish to display a list of
            options for a given parameter. parameter options may be either a list or a zero argument
            callable. 
        """
        super().__init__()
        self.scope = scope
        self.callable = callable

        self.input_widgets = []
        self.inputs = inputs
        self._setup_input_widgets(descriptions, options)

        self.output = widgets.Text(placeholder='output name',
                                   value='',
                                   continuous_update=False)

        self.button = widgets.Button(description=name)
        self.button.on_click(self._on_button_clicked)

        self.children = [
            widgets.HBox(self.input_widgets + [self.output, self.button])
        ]

        self.subscribers = []

    def _setup_input_widgets(self, descriptions, options):
        for name in self.inputs.keys():
            placeholder = descriptions[name] if name in descriptions else name
            option = options[name] if name in options else []
            option = option() if callable(option) else option
            self.input_widgets.append(
                widgets.Combobox(placeholder=placeholder,
                                 continuous_update=False,
                                 options=option))

    def _retrive_kwargs(self):
        kwargs = {
            name: converter(item.value)
            for name, converter, item in zip(
                self.inputs.keys(), self.inputs.values(), self.input_widgets)
        }
        return kwargs

    def _on_button_clicked(self, button):
        if self.output.value:
            output_name = self.output.value
        else:
            print(f'Invalid inputs: No output name specified')
            return
        self.scope[output_name] = self.process()

    def process(self):
        """
        Calls the wrapped function using the 
        parameter values specified.

        Returns: Output of the wrapped callable.
        """
        try:
            kwargs = self._retrive_kwargs()
        except ValueError as e:
            print(f'Invalid inputs: {e}')
            return

        return self.callable(**kwargs)


class PlotWidget(widgets.Box):
    """
    Wraps scipp.plot.plot attempting to display the result of evaluating
    the input string as a scipp plot.
    """
    def __init__(self, scope):
        """
        Parameters:
        scope (dict): the scope dict to use when evaluating expressions.
        """
        super().__init__()
        self.scope = scope
        options = [
            key for key, item in globals().items()
            if isinstance(item, (sc.DataArray, sc.Dataset))
        ]
        self._data_selector = widgets.Combobox(placeholder='Data to plot',
                                               options=options)
        self._button = widgets.Button(description='Plot')
        self._button.on_click(self._on_plot_button_clicked)
        self.plot_options = widgets.Output()
        self.update_button = widgets.Button(description='Manual Update')
        self.update_button.on_click(self._on_update_button_clicked)
        self.output = widgets.Output(width='100%', height='100%')
        self.children = [
            widgets.VBox([
                widgets.HBox([self.plot_options, self.update_button]),
                widgets.HBox([self._data_selector, self._button]), self.output
            ])
        ]
        self.update()

    def _repr_html_(self, input_scope=None):
        import inspect
        # Is there a better way to get the scope? The `7` is hard-coded for the
        # current IPython stack when calling _repr_html_ so this is bound to break.
        scope = input_scope if input_scope else inspect.stack()[7][0].f_globals
        from IPython import get_ipython
        ipython = get_ipython()
        out = ''
        for category in ['Variable', 'DataArray', 'Dataset']:
            names = ipython.magic(f"who_ls {category}")
            out += f"<details open=\"open\"><summary>{category}s:"\
                   f"({len(names)})</summary>"
            for name in names:
                html = sc.table_html.make_html(eval(name, scope))
                out += f"<details style=\"padding-left:2em\"><summary>"\
                       f"{name}</summary>{html}</details>"
            out += "</details>"
        from IPython.core.display import display, HTML
        display(HTML(out))

    def _on_plot_button_clicked(self, b):
        self.output.clear_output()
        with self.output:
            disp.display(plot(eval(self._data_selector.value, self.scope)))

    def _on_update_button_clicked(self, button):
        self.update()

    def update(self):
        """
        Updates the display of available scipp objects
        """
        options = [
            key for key, item in self.scope.items()
            if isinstance(item, (sc.DataArray, sc.Dataset, sc.Variable))
        ]
        self._data_selector.options = options
        self.plot_options.clear_output()
        with self.plot_options:
            self._repr_html_(self.scope)


#Method to hide code blocks taken from
#https://stackoverflow.com/questions/27934885/how-to-hide-code-from-cells-in-ipython-notebook-visualized-with-nbviewer
javascript_functions = {False: "hide()", True: "show()"}
button_descriptions = {False: "Show code", True: "Hide code"}


def toggle_code(state):
    """
    Toggles the JavaScript show()/hide() function on the div.input element.
    """

    output_string = "<script>$(\"div.input\").{}</script>"
    output_args = (javascript_functions[state], )
    output = output_string.format(*output_args)

    disp.display(disp.HTML(output))


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
