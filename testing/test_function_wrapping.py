from mose_framework.wrapping import FunctionWrapper, write_wrapper, read_wrapper, wrapped_process
import pytest
import numpy as np
import os
from shutil import rmtree


FIXTURE_DIR = "".join([os.path.abspath(os.path.join(os.getcwd(), os.pardir)), "\\TestingData"])

DATASET = pytest.mark.datafiles(
    "".join([FIXTURE_DIR, "\\TestWrapping\\test_wrapper.json"]),
    keep_top_dir=False,
    on_duplicate="ignore",
)


def generate_test_array():
    test_array = np.ones((2, 5), dtype=np.uint8)
    test_array[0, :] = [1, 2, 3, 4, 5]
    return test_array


def generate_test_array_results():
    test_array = generate_test_array()
    test_array = np.sum(test_array, axis=1)
    test_array = np.cumsum(test_array)
    test_array = np.mean(test_array, axis=0)
    return test_array


def test_function_wrapping_keys():
    test_wrapper = FunctionWrapper()
    test_wrapper.wrap_function(np.sum, axis=1)
    test_wrapper.wrap_function(np.cumsum)
    test_wrapper.wrap_function(np.sum, axis=0)

    # check proper naming of keys
    assert("sum" in test_wrapper.config.keys())
    assert("cumsum" in test_wrapper.config.keys())


def test_function_wrapping_modules():
    test_wrapper = FunctionWrapper()
    test_wrapper.wrap_function(np.sum, axis=1)
    test_wrapper.wrap_function(np.cumsum)
    test_wrapper.wrap_function(np.sum, axis=0)

    # check proper inclusion of modules
    assert("numpy" in test_wrapper.config.get("sum"))


def test_function_wrapping_parameters():
    test_wrapper = FunctionWrapper()
    test_wrapper.wrap_function(np.sum, axis=1)
    test_wrapper.wrap_function(np.cumsum)
    test_wrapper.wrap_function(np.mean, axis=0)

    # check proper inclusion of parameters
    assert(test_wrapper.config.get("sum")[2].get("axis") == 1)


def test_function_wrapping_runtime():
    test_wrapper = FunctionWrapper()
    test_wrapper.wrap_function(np.sum, axis=1)
    test_wrapper.wrap_function(np.cumsum)
    test_wrapper.wrap_function(np.mean, axis=0)

    # check runtime
    test_array = generate_test_array()
    results = wrapped_process(test_array, *test_wrapper.interface())
    assert(results == generate_test_array_results())


def test_write_wrapper_runtime(tmp_path):
    test_wrapper = FunctionWrapper()
    test_wrapper.wrap_function(np.sum, axis=1)
    test_wrapper.wrap_function(np.cumsum)
    test_wrapper.wrap_function(np.mean, axis=0)

    # check write
    write_wrapper(test_wrapper, "test_wrapper.json", str(tmp_path))


@DATASET
def test_read_wrapper_runtime(datafiles):
    test_wrapper = read_wrapper("".join([str(datafiles), "\\test_wrapper.json"]))
    rmtree(datafiles)


@DATASET
def test_read_wrapper_results(datafiles):
    test_wrapper = read_wrapper("".join([str(datafiles), "\\test_wrapper.json"]))

    # check runtime
    test_array = generate_test_array()
    results = wrapped_process(test_array, *test_wrapper.interface())
    assert(results == generate_test_array_results())
    rmtree(datafiles)


def test_read_write_wrapper(tmp_path):
    # Instance
    test_wrapper = FunctionWrapper()
    test_wrapper.wrap_function(np.sum, axis=1)
    test_wrapper.wrap_function(np.cumsum)
    test_wrapper.wrap_function(np.mean, axis=0)

    # Write
    write_wrapper(test_wrapper, "test_wrapper.json", str(tmp_path))

    # Read
    test_wrapper = read_wrapper("".join([str(tmp_path), "\\test_wrapper.json"]))

    # Check Results
    test_array = generate_test_array()
    results = wrapped_process(test_array, *test_wrapper.interface())
    assert(results == generate_test_array_results())
