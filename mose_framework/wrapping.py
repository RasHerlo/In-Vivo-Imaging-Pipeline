from __future__ import annotations
import os
from collections import OrderedDict
import importlib
from typing import Optional, Callable, Tuple
from json_tricks import dumps, loads
import numpy as np
from mose_framework.user_interfaces import validate_path_string, validate_string


class FunctionWrapper:
    """
    This is a class for wrapping functions into a single step pipeline
    """
    def __init__(self):
        self.config = OrderedDict()

    def __str__(self):

        def make_single_step():
            nonlocal _key
            nonlocal _step
            # Add (Step, Function): Function(Input
            _return_string = "".join([str((_step, _key)), ": ", _key, "(Input"])
            # Add Parameters (Step, Function(Input, Parameter=Value
            for _sub_key in self.config.get(_key)[2]:
                _return_string = "".join([_return_string, ", ", _sub_key, "=",
                                          str(self.config.get(_key)[2].get(_sub_key))])
            # Enclose and add import information (Step, Function(Input, Parameter=Value) from Module
            _return_string = "".join([_return_string, ") from ", self.config.get(_key)[0]])

            return _return_string

        _config_step = enumerate(self.config.keys())
        _print_string = "\nWrapped Pipeline: "

        # noinspection PyTypeChecker
        for _step, _key in enumerate(self.config.keys()):
            _print_string = "".join([_print_string, "\n", make_single_step()])

        return _print_string

    def wrap_function(self, Function: Callable, **kwargs) -> Self:
        """
        Stores functions into a dictionary where key is the function name and the value is a tuple:
        (Module/Package, Function, Parameters)

        :param Function: Function to add
        :type Function: Callable
        :param kwargs: Parameters to pass
        :rtype: Any
        """
        # noinspection PyArgumentList
        self.config[Function.__name__] = (Function.__module__, Function, dict(**kwargs))

    def interface(self) -> Tuple:
        # noinspection PyTypeChecker
        Functions = [self.config.get(_key)[1] for _key in self.config.keys()]
        # noinspection PyTypeChecker
        Parameters = [self.config.get(_key)[2] for _key in self.config.keys()]
        return tuple([Functions, Parameters])

    def __json_encode__(self) -> Self:
        """
        Json encoder for wrapped functions

        :rtype: Any
        """
        # Here we save each functions as a nested dictionary containing keys module, function (name), parameters
        # noinspection PyTypeChecker
        for _key in self.config.keys():
            self.config[_key] = {
                "Module": self.config[_key][0],
                "Function": _key,
                "Parameters": self.config[_key][2],
            }
        return {"config": self.config}

    def __json_decode__(self, **attrs) -> Self:
        """
        Json decoder for wrapped functions

        :param attrs: attributes from json
        :rtype: Any
        """
        # Here we extract the appropriate functions dynamically imported the module and grabbing the function from
        # its namespace using __dict__.get() to access the functions using the name as a key
        self.config = attrs["config"]
        for _key in self.config.keys():
            self.config[_key] = (self.config[_key].get("Module"),
                                 importlib.import_module(self.config[_key].get("Module")).__dict__.get(_key),
                                 self.config[_key].get("Parameters"))


def write_wrapper(Wrapper: FunctionWrapper, Filename: Optional[str] = None, Path: Optional[str] = None) -> None:
    """
    This function writes an instance of :class:`Management.Wrapping.FunctionWrapper` to .json for future access

    :param Wrapper: An instance of a function wrapper containing wrapper functions
    :type Wrapper: Any
    :param Filename: Filename for saved .json
    :type Filename: str
    :param Path: Path to save file in
    :type Path: str
    :rtype: None
    """

    if Filename is None:
        Filename = "wrapped_functions.json"

    # Validate user input
    if not validate_string(Filename):
        ValueError("Please use only standard ascii letters and digits")
    if not validate_path_string(Filename):
        ValueError("Please use only standard ascii letters and digits")
    if ".json" not in Filename:
        Filename = "".join([Filename, ".json"])
    if Path is not None:
        Filename = "".join([Path, "\\", Filename])
    else:
        Filename = "".join([os.getcwd(), "\\", Filename])

    # Serialize to .json
    _wrapped_functions = dumps(Wrapper, indent=0)

    # Actually write
    with open(Filename, "w") as _file:
        _file.write(_wrapped_functions)
    _file.close()
    print("\nSaved Function Wrapper to File.")


def read_wrapper(Filepath: str) -> FunctionWrapper:
    """
    This function reads a wrapped function file .json and instantiates its :class:`Management.Wrapping.FunctionWrapper`

    :param Filepath: Absolute filepath to file
    :type Filepath: str
    :return: wrapped function object
    :rtype: object
    """
    # Validate User Input
    if not validate_path_string(Filepath):
        ValueError("Please use only standard ascii letters and digits.")
    if ".json" not in Filepath:
        Filepath = "".join([Filepath, ".json"])
    if not os.path.exists(Filepath):
        FileNotFoundError("Unable to locate file.")

    # Open
    with open(Filepath, "r") as _file:
        wrapper = loads(_file.read())
    _file.close()

    return wrapper


def wrapped_process(Input: np.ndarray, Functions: Tuple[Union[Callable, str]],
               Parameters: Tuple[dict]) -> np.ndarray:
    """
    This is a wrapper for preprocessing. A tuple of functions and a tuple of associated parameters are fed alongside
    the images to be processed. For example, a single element in a Functions tuple might be *np.max*. It's associated
     element in the Parameters tuple might be a dictionary containing the keys-value pairs "axis"=1,
     and keepsdims=False)

    :param Input: Input to be processed
    :type Input: Any
    :param Functions: A tuple of callable functions to perform on the input
    :type Functions: tuple[callable]
    :param Parameters: A tuple of dictionaries containing the associated parameters for each function
    :type Parameters: tuple[dict]
    :return: The processed input
    :rtype: Any
    """

    # quick return if simply passing
    if Functions is None:
        return Input

    # actually run if callables passed
    for _fun, _params in zip(Functions, Parameters):
        try:
            Input = _fun(Input, **_params)
        except TypeError:
            print("Please pass a tuple of callables and a tuples of dictionaries")
        except ModuleNotFoundError:
            print("Please make sure all requisite modules have been imported")
        except AssertionError or RuntimeError or ValueError or ZeroDivisionError:
            print("Please make sure you have followed the appropriate documentation for passed callables")

    return Input
