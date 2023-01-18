from __future__ import annotations
from typing import Union
import os.path
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
from shutil import copytree, copy2, rmtree
from tqdm import tqdm
import pathlib
import string


def select_directory(**kwargs) -> Union[str, None]:
    """
    Interactive tool for directory selection. All keyword arguments are
    passed to `tkinter.filedialog.askdirectory <https://docs.python.org/3/library/tk.html>`_

    :param kwargs: keyword arguments
    :return: absolute path to directory
    :rtype: str
    """
    # Make Root
    root = tk.Tk()

    # collect path & format
    # noinspection PyArgumentList
    path = askdirectory(**kwargs)
    path = str(pathlib.Path(path))
    if path == ".":
        path = None

    # destroy root
    root.destroy()
    return path


def select_file(**kwargs) -> Union[str, None]:
    """
    Interactive tool for directory selection. All keyword arguments are
    passed to `tkinter.filedialog.askopenfilename <https://docs.python.org/3/library/tk.html>`_

    :param kwargs: keyword arguments
    :return: absolute path to file or None
    :rtype: str
    """
    # Make Root
    root = tk.Tk()

    # select path
    # noinspection PyArgumentList
    path = askopenfilename(**kwargs)
    path = str(pathlib.Path(path))
    if path == ".":
        path = None

    # destroy root
    root.destroy()
    return path


def select_file(**kwargs) -> Union[str, None]:
    """
    Interactive tool for directory selection. All keyword arguments are
    passed to `tkinter.filedialog.askopenfilename <https://docs.python.org/3/library/tk.html>`_

    :param kwargs: keyword arguments
    :return: absolute path to file or None
    :rtype: str
    """
    # Make Root
    root = tk.Tk()

    # select path
    # noinspection PyArgumentList
    path = askopenfilename(**kwargs)
    path = str(pathlib.Path(path))
    if path == ".":
        path = None

    # destroy root
    root.destroy()
    return path


def verbose_copying(SourceFolder: Union[str, pathlib.Path], DestinationFolder: Union[str, pathlib.Path]) -> None:
    """
    Verbose copying of one folder's contents to another
    
    :param SourceFolder: Source folder
    :type SourceFolder: Union[str, pathlib.Path]
    :param DestinationFolder: Destination folder
    :type DestinationFolder: Union[str, pathlib.Path]
    :rtype: None
    """
    
    # Make sure SourceFolder is a pathlib.Path object for rglob and DestinationFolder is a str for copy2
    if isinstance(SourceFolder, str):
        SourceFolder = pathlib.Path(SourceFolder)
    if isinstance(DestinationFolder, pathlib.Path):
        DestinationFolder = str(DestinationFolder)

    # Make sure destination is not the source
    if SourceFolder == DestinationFolder:
        raise ValueError("Destination and source files are identical")

    _num_files = sum([1 for _file in SourceFolder.rglob("*") if _file.is_file()])
    _pbar = tqdm(total=_num_files)
    _pbar.set_description("Copying files...")

    if os.path.exists(DestinationFolder):
        rmtree(DestinationFolder)

    def verbose_copy(_SourceFolder, _DestinationFolder):
        copy2(_SourceFolder, _DestinationFolder)
        _pbar.update(1)

    copytree(SourceFolder, DestinationFolder, copy_function=verbose_copy)


def validate_string(String: str) -> bool:
    return set(String) <= set(string.ascii_letters + string.digits)


def validate_path_string(Path: str) -> bool:
    if [_char for _char in list(Path) if _char is ":"].__len__() != 1:
        return False
    else:
        return set(Path) <= set(string.ascii_letters + string.digits + "." + "\\" + ":")


def validate_config_format(String: str) -> bool:
    return ".json" in String