from ipyfilechooser import FileChooser
from ipywidgets import Layout, Text, Dropdown, Select, Box
import os
import fnmatch
from pathlib import Path
from typing import Iterable


class FilePicker(object):
    def __init__(self, directory=os.getcwd()):
        self._file_display = Select()
        self._filter_pattern = ''
        self._selected = Path(directory)
        self.update_diectory(directory)
        self._file_display.observe(self._on_dircontent_select, names='value')

    def _on_dircontent_select(self, change):
        new_path = self._directory / self.display_to_actual_map[change['new']]
        if new_path.is_dir():
            self._file_display.unobserve(self._on_dircontent_select,
                                         names='value')
            self.update_diectory(new_path)
            self._file_display.observe(self._on_dircontent_select,
                                       names='value')

        self._selected = new_path.resolve()

    def update_diectory(self, new_dir):
        self._directory = Path(new_dir)
        dir_contents_display = get_dir_contents(
            self._directory,
            prepend_icons=True,
            filter_pattern=self._filter_pattern)
        dir_contents = get_dir_contents(self._directory,
                                        prepend_icons=False,
                                        filter_pattern=self._filter_pattern)
        self.display_to_actual_map = {
            disp: real
            for disp, real in zip(dir_contents_display, dir_contents)
        }
        self._file_display.options = dir_contents_display
        self._file_display.value = None

    @property
    def widget(self):
        return self._file_display

    @property
    def selected(self):
        return str(self._selected)


def has_parent(path):
    """Check if a path has a parent folder."""
    return os.path.basename(path) != ''


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
            full_item = path / item
            if append and full_item.is_dir():
                dirs.append(item_str)
            elif append and not show_only_dirs:
                if filter_pattern:
                    if filter_pattern in item_str:
                        files.append(item_str)
                else:
                    files.append(item_str)
        if path.parent != path:
            dirs.insert(0, '..')
    dirs = sorted(dirs, key=sort_key, reverse=reversed_sort)
    files = sorted(files, key=sort_key, reverse=reversed_sort)
    if prepend_icons:
        return prepend_dir_icons(dirs) + files
    else:
        return dirs + files
