from ipyfilechooser import FileChooser
from ipywidgets import Layout, Text, Dropdown, Select, Box, GridBox, VBox, Button, HBox
import os, sys
import fnmatch
from pathlib import Path
from typing import Iterable

sort_descriptor_to_kwargs = {
    'alphabetical a->z': {
        'key': str,
        'reverse': False
    },
    'alphabetical z->a': {
        'key': str,
        'reverse': True
    },
    'date old->new': {
        'key': os.path.getmtime,
        'reverse': False
    },
    'date new->old': {
        'key': os.path.getmtime,
        'reverse': True
    },
}


class FileBrowser(object):
    def __init__(self, directory=os.getcwd()):
        self._widget = VBox()
        self._directory_picker = Dropdown(options=get_subpaths(directory))
        self._filter_text = Text(placeholder='filter')
        self._sort_by = Dropdown(options=sort_descriptor_to_kwargs.keys())
        self._select = Button(description='Select')
        self._cancel = Button(description='Cancel')
        self._file_select = FilePicker(directory=directory)

        top_row = HBox(
            [self._directory_picker, self._filter_text, self._sort_by])
        button_row = HBox([self._select, self._cancel])

        self._widget.children = [top_row, self._file_select.widget, button_row]

        self._directory_picker.observe(self._change_selected_dir,
                                       names='value')

        self._filter_text.observe(self._change_filter, names='value')

        self._sort_by.observe(self._change_sort, names='value')

    def _change_selected_dir(self, change):
        self._file_select.update_directory(change['new'])

    def _change_filter(self, change):
        self._file_select.update_filter(change['new'])

    def _change_sort(self, change):
        self._file_select.update_sort(sort_descriptor_to_kwargs[change['new']])

    @property
    def widget(self):
        return self._widget


class FilePicker(object):
    def __init__(self, directory=os.getcwd()):
        self._file_display = Select()
        self._filter_pattern = ''
        self._reversed_sort = False
        self._sort_key = str
        self._selected = Path(directory)
        self._file_display.observe(self._on_dircontent_select, names='value')
        self.update_directory(directory)
        self._file_display.observe(self._on_dircontent_select, names='value')

    def _on_dircontent_select(self, change):
        new_path = self._directory / self.display_to_actual_map[change['new']]
        if new_path.is_dir():
            self.update_directory(new_path)

        self._selected = new_path.resolve()

    def update_directory(self, new_dir):
        self._file_display.unobserve(self._on_dircontent_select, names='value')
        self._directory = Path(new_dir)
        dir_contents_display = get_dir_contents(
            self._directory,
            prepend_icons=True,
            filter_pattern=self._filter_pattern,
            sort_key=self._sort_key,
            reversed_sort=self._reversed_sort)
        dir_contents = get_dir_contents(self._directory,
                                        prepend_icons=False,
                                        filter_pattern=self._filter_pattern,
                                        sort_key=self._sort_key,
                                        reversed_sort=self._reversed_sort)
        self.display_to_actual_map = {
            disp: real
            for disp, real in zip(dir_contents_display, dir_contents)
        }
        self._file_display.options = dir_contents_display
        self._file_display.value = None
        self._file_display.observe(self._on_dircontent_select, names='value')

    @property
    def widget(self):
        return self._file_display

    @property
    def selected(self):
        return str(self._selected)

    def update_filter(self, filter):
        self._filter_pattern = filter
        self.update_directory(self._directory)

    def update_sort(self, sort_kwargs):
        self._sort_key = sort_kwargs['key']
        self._reversed_sort = sort_kwargs['reverse']
        self.update_directory(self._directory)


def prepend_dir_icons(dir_list):
    """Prepend unicode folder icon to directory names."""
    return ['\U0001F4C1 ' + dirname for dirname in dir_list]


def get_dir_contents(path,
                     show_hidden=False,
                     prepend_icons=False,
                     show_only_dirs=False,
                     filter_pattern=None,
                     sort_key=str,
                     reversed_sort=False) -> Iterable[str]:
    """Get directory contents."""
    files = list()
    dirs = list()

    if path.is_dir():
        for item in path.iterdir():
            append = True
            item_str = str(item.name)
            if item_str.startswith('.') and not show_hidden:
                append = False
            if filter_pattern not in item_str:
                append = False
            full_item = path / item
            if append and full_item.is_dir():
                dirs.append(item_str)
            elif append and not show_only_dirs:
                files.append(item_str)
        if path.parent != path and filter_pattern in '..':
            dirs.insert(0, '..')
    dirs = sorted(dirs, key=sort_key, reverse=reversed_sort)
    files = sorted(files, key=sort_key, reverse=reversed_sort)
    if prepend_icons:
        return prepend_dir_icons(dirs) + files
    else:
        return dirs + files


def get_subpaths(path):
    """Walk a path and return a list of subpaths."""
    if os.path.isfile(path):
        path = os.path.dirname(path)

    paths = [path]
    path, tail = os.path.split(path)

    while tail:
        paths.append(path)
        path, tail = os.path.split(path)

    try:
        # Add Windows drive letters, but remove the current drive
        drives = get_drive_letters()
        drives.remove(paths[-1])
        paths.extend(drives)
    except ValueError:
        pass
    return paths


def get_drive_letters():
    """Get drive letters."""
    if sys.platform == 'win32':
        # Windows has drive letters
        return [
            '%s:\\' % d for d in string.ascii_uppercase
            if os.path.exists('%s:' % d)
        ]
    else:
        # Unix does not have drive letters
        return []
