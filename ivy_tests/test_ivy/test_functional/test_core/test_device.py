"""Collection of tests for unified device functions."""

# global
import io
import multiprocessing
import os
import re
import shutil
import sys

import numpy as np
import pynvml
import psutil
from hypothesis import strategies as st, assume

# local
import ivy
from ivy.functional.ivy.gradients import _variable
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import handle_test


# Helpers #
# ------- #


def _ram_array_and_clear_test(metric_fn, size=10000000):
    # This function checks if the memory usage changes before, during and after

    # Measure usage before creating array
    before = metric_fn()
    # Create an array of floats, by default with 10 million elements (40 MB)
    arr = ivy.ones((size,), dtype="float32", device="cpu")
    during = metric_fn()
    # Check that the memory usage has increased
    assert before < during

    # Delete the array
    del arr
    # Measure the memory usage after the array is deleted
    after = metric_fn()
    # Check that the memory usage has decreased
    assert during > after


def _get_possible_devices():
    # Return all the possible usable devices
    devices = ["cpu"]
    if ivy.gpu_is_available():
        for i in range(ivy.num_gpus()):
            devices.append("gpu:" + str(i))

    # Return a list of ivy devices
    return list(map(ivy.Device, devices))


def _empty_dir(path, recreate=False):
    # Delete the directory if it exists and create it again if recreate is True
    if os.path.exists(path):
        shutil.rmtree(path)
    if recreate:
        os.makedirs(path)


# Tests #
# ------#

# Device Queries #

# dev
@handle_test(
    fn_tree="functional.ivy.dev",
    array_shape=helpers.lists(
        arg=helpers.ints(min_value=2, max_value=3),
        min_size="num_dims",
        max_size="num_dims",
        size_bounds=[1, 3],
    ),
    dtype=helpers.get_dtypes("numeric", full=False),
    as_variable_flags=st.booleans(),
)
def test_dev(
    *,
    array_shape,
    dtype,
    test_flags,
    backend_fw,
):
    assume(not (backend_fw == "torch" and "int" in dtype))
    x = np.random.uniform(size=tuple(array_shape)).astype(dtype[0])

    for device in _get_possible_devices():
        x = ivy.array(x, device=device)
        if test_flags.as_variable and ivy.is_float_dtype(dtype[0]):
            x = _variable(x)

        ret = ivy.dev(x)
        # type test
        assert isinstance(ret, str)
        # value test
        assert ret == device
        # array instance test
        assert x.dev() == device
        # container instance test
        container_x = ivy.Container({"a": x})
        assert container_x.dev() == device
        # container static test
        assert ivy.Container.static_dev(container_x) == device


# as_ivy_dev
@handle_test(
    fn_tree="functional.ivy.as_ivy_dev",
    array_shape=helpers.lists(
        arg=helpers.ints(min_value=2, max_value=3),
        min_size="num_dims",
        max_size="num_dims",
        size_bounds=[1, 3],
    ),
    dtype=helpers.get_dtypes("numeric", full=False),
)
def test_as_ivy_dev(
    *,
    array_shape,
    dtype,
    test_flags,
    backend_fw,
):
    assume(not (backend_fw == "torch" and "int" in dtype))

    x = np.random.uniform(size=tuple(array_shape)).astype(dtype[0])

    for device in _get_possible_devices():
        x = ivy.array(x, device=device)
        if test_flags.as_variable and ivy.is_float_dtype(dtype[0]):
            x = _variable(x)

        native_device = ivy.dev(x, as_native=True)
        ret = ivy.as_ivy_dev(native_device)

        # Type test
        assert isinstance(ret, str)
        # Value test
        assert ret == device


# as_native_dev
# TODO: possible refactor to use the helpers.test_function method
@handle_test(
    fn_tree="functional.ivy.as_native_dev",
    array_shape=helpers.lists(
        arg=helpers.ints(min_value=1, max_value=3),
        min_size="num_dims",
        max_size="num_dims",
        size_bounds=[1, 3],
    ),
    dtype=helpers.get_dtypes("float", index=1, full=False),
)
def test_as_native_dev(
    *,
    array_shape,
    dtype,
    test_flags,
    on_device,
):
    # TODO: should be replaced with the helpers.dtype_values function
    x = np.random.uniform(size=tuple(array_shape)).astype(dtype[0])

    for device in _get_possible_devices():
        x = ivy.asarray(x, device=on_device)
        if test_flags.as_variable:
            x = _variable(x)

        device = ivy.as_native_dev(on_device)
        ret = ivy.as_native_dev(ivy.dev(x))
        # value test
        if ivy.current_backend_str() == "tensorflow":
            assert "/" + ":".join(ret[1:].split(":")[-2:]) == "/" + ":".join(
                device[1:].split(":")[-2:]
            )
        elif ivy.current_backend_str() == "torch":
            assert ret.type == device.type
        else:
            assert ret == device


# Device Allocation #
# default_device
@handle_test(fn_tree="functional.ivy.default_device")
def test_default_device():
    # setting and unsetting
    orig_len = len(ivy.default_device_stack)
    ivy.set_default_device("cpu")
    assert len(ivy.default_device_stack) == orig_len + 1
    ivy.set_default_device("cpu")
    assert len(ivy.default_device_stack) == orig_len + 2
    ivy.unset_default_device()
    assert len(ivy.default_device_stack) == orig_len + 1
    ivy.unset_default_device()
    assert len(ivy.default_device_stack) == orig_len

    # with
    assert len(ivy.default_device_stack) == orig_len
    with ivy.DefaultDevice("cpu"):
        assert len(ivy.default_device_stack) == orig_len + 1
        with ivy.DefaultDevice("cpu"):
            assert len(ivy.default_device_stack) == orig_len + 2
        assert len(ivy.default_device_stack) == orig_len + 1
    assert len(ivy.default_device_stack) == orig_len


# to_dev
@handle_test(
    fn_tree="functional.ivy.to_device",
    array_shape=helpers.lists(
        arg=helpers.ints(min_value=1, max_value=3),
        min_size="num_dims",
        max_size="num_dims",
        size_bounds=[1, 3],
    ),
    dtype=helpers.get_dtypes("numeric", full=False),
    stream=helpers.ints(min_value=0, max_value=50),
)
def test_to_device(
    *,
    array_shape,
    dtype,
    stream,
    test_flags,
    backend_fw,
    on_device,
):
    assume(not (backend_fw == "torch" and "int" in dtype))

    x = np.random.uniform(size=tuple(array_shape)).astype(dtype[0])
    x = ivy.asarray(x)
    if test_flags.as_variable and ivy.is_float_dtype(dtype[0]):
        x = _variable(x)

    # create a dummy array for out that is broadcastable to x
    out = (
        ivy.zeros(ivy.shape(x), device=on_device, dtype=dtype[0])
        if test_flags.with_out
        else None
    )

    device = ivy.dev(x)
    x_on_dev = ivy.to_device(x, on_device, stream=stream, out=out)
    dev_from_new_x = ivy.dev(x_on_dev)

    if test_flags.with_out:
        # should be the same array test
        assert x_on_dev is out

        # should be the same device
        assert ivy.dev(x_on_dev, as_native=True) == ivy.dev(out, as_native=True)

        # check if native arrays are the same
        # these backends do not support native inplace updates
        assume(not (backend_fw in ["tensorflow", "jax"]))

        assert x_on_dev.data is out.data

    # value test
    if ivy.current_backend_str() == "tensorflow":
        assert "/" + ":".join(dev_from_new_x[1:].split(":")[-2:]) == "/" + ":".join(
            device[1:].split(":")[-2:]
        )
    elif ivy.current_backend_str() == "torch":
        assert type(dev_from_new_x) == type(device)
    else:
        assert dev_from_new_x == device

    # array instance test
    assert x.to_device(device).dev() == device
    # container instance test
    container_x = ivy.Container({"x": x})
    assert container_x.to_device(device).dev() == device
    # container static test
    assert ivy.Container.to_device(container_x, device).dev() == device


# Function Splitting #


@st.composite
def _axis(draw):
    max_val = draw(st.shared(helpers.ints(), key="num_dims"))
    return draw(helpers.ints(min_value=0, max_value=max_val - 1))


@handle_test(
    fn_tree="functional.ivy.split_func_call",
    array_shape=helpers.lists(
        arg=helpers.ints(min_value=1, max_value=3),
        min_size="num_dims",
        max_size="num_dims",
        size_bounds=[1, 3],
    ),
    dtype=helpers.get_dtypes("numeric", full=False),
    chunk_size=helpers.ints(min_value=1, max_value=3),
    axis=_axis(),
)
def test_split_func_call(
    *,
    array_shape,
    dtype,
    chunk_size,
    axis,
    test_flags,
):
    # inputs
    shape = tuple(array_shape)
    x1 = np.random.uniform(size=shape).astype(dtype[0])
    x2 = np.random.uniform(size=shape).astype(dtype[0])
    x1 = ivy.asarray(x1)
    x2 = ivy.asarray(x2)
    if test_flags.as_variable and ivy.is_float_dtype(dtype[0]):
        x1 = _variable(x1)
        x2 = _variable(x2)

    # function
    def func(t0, t1):
        return t0 * t1, t0 - t1, t1 - t0

    # predictions
    a, b, c = ivy.split_func_call(
        func, [x1, x2], "concat", chunk_size=chunk_size, input_axes=axis
    )

    # true
    a_true, b_true, c_true = func(x1, x2)

    # value test
    helpers.assert_all_close(ivy.to_numpy(a), ivy.to_numpy(a_true))
    helpers.assert_all_close(ivy.to_numpy(b), ivy.to_numpy(b_true))
    helpers.assert_all_close(ivy.to_numpy(c), ivy.to_numpy(c_true))


@handle_test(
    fn_tree="functional.ivy.split_func_call",
    array_shape=helpers.lists(
        arg=helpers.ints(min_value=2, max_value=3),
        min_size="num_dims",
        max_size="num_dims",
        size_bounds=[2, 3],
    ),
    dtype=helpers.get_dtypes("numeric", full=False),
    chunk_size=helpers.ints(min_value=1, max_value=3),
    axis=helpers.ints(min_value=0, max_value=1),
)
def test_split_func_call_with_cont_input(
    *,
    array_shape,
    test_flags,
    dtype,
    chunk_size,
    axis,
    on_device,
):
    shape = tuple(array_shape)
    x1 = np.random.uniform(size=shape).astype(dtype[0])
    x2 = np.random.uniform(size=shape).astype(dtype[0])
    x1 = ivy.asarray(x1, device=on_device)
    x2 = ivy.asarray(x2, device=on_device)
    # inputs

    if test_flags.as_variable and ivy.is_float_dtype(dtype[0]):
        in0 = ivy.Container(cont_key=_variable(x1))
        in1 = ivy.Container(cont_key=_variable(x2))
    else:
        in0 = ivy.Container(cont_key=x1)
        in1 = ivy.Container(cont_key=x2)

    # function
    def func(t0, t1):
        return t0 * t1, t0 - t1, t1 - t0

    # predictions
    a, b, c = ivy.split_func_call(
        func, [in0, in1], "concat", chunk_size=chunk_size, input_axes=axis
    )

    # true
    a_true, b_true, c_true = func(in0, in1)

    # value test
    helpers.assert_all_close(ivy.to_numpy(a.cont_key), ivy.to_numpy(a_true.cont_key))
    helpers.assert_all_close(ivy.to_numpy(b.cont_key), ivy.to_numpy(b_true.cont_key))
    helpers.assert_all_close(ivy.to_numpy(c.cont_key), ivy.to_numpy(c_true.cont_key))


# profiler
@handle_test(
    fn_tree="functional.ivy.Profiler",
)
def test_profiler(
    *,
    backend_fw,
):
    # ToDo: find way to prevent this test from hanging when run
    #  alongside other tests in parallel

    # log dir, each framework uses their own folder,
    # so we can run this test in parallel
    this_dir = os.path.dirname(os.path.realpath(__file__))
    log_dir = os.path.join(this_dir, "../log")
    fw_log_dir = os.path.join(log_dir, backend_fw.__name__)

    # Remove old content and recreate log dir
    _empty_dir(fw_log_dir, True)

    # with statement
    with ivy.Profiler(fw_log_dir):
        a = ivy.ones([10])
        b = ivy.zeros([10])
        _ = a + b

    # Should have content in folder
    assert len(os.listdir(fw_log_dir)) != 0, "Profiler did not log anything"

    # Remove old content and recreate log dir
    _empty_dir(fw_log_dir, True)

    # Profiler should stop log
    assert len(os.listdir(fw_log_dir)) == 0, "Profiler logged something while stopped"

    # start and stop methods
    profiler = ivy.Profiler(fw_log_dir)
    profiler.start()
    a = ivy.ones([10])
    b = ivy.zeros([10])
    _ = a + b
    profiler.stop()

    # Should have content in folder
    assert len(os.listdir(fw_log_dir)) != 0, "Profiler did not log anything"

    # Remove old content including the logging folder
    _empty_dir(fw_log_dir, False)

    assert not os.path.exists(fw_log_dir), "Profiler recreated logging folder"


@handle_test(
    fn_tree="functional.ivy.num_ivy_arrays_on_dev",
    num=helpers.ints(min_value=0, max_value=5),
)
def test_num_ivy_arrays_on_dev(
    *,
    num,
    on_device,
):
    arrays = [
        ivy.array(np.random.uniform(size=2).tolist(), device=on_device)
        for _ in range(num)
    ]
    assert ivy.num_ivy_arrays_on_dev(on_device) == num
    for item in arrays:
        del item


@handle_test(
    fn_tree="functional.ivy.get_all_ivy_arrays_on_dev",
    num=helpers.ints(min_value=0, max_value=5),
)
def test_get_all_ivy_arrays_on_dev(
    *,
    num,
    on_device,
):
    arrays = [ivy.array(np.random.uniform(size=2)) for _ in range(num)]
    arr_ids_on_dev = [id(a) for a in ivy.get_all_ivy_arrays_on_dev(on_device).values()]
    for a in arrays:
        assert id(a) in arr_ids_on_dev


@handle_test(
    fn_tree="functional.ivy.print_all_ivy_arrays_on_dev",
    num=helpers.ints(min_value=0, max_value=2),
    attr_only=st.booleans(),
)
def test_print_all_ivy_arrays_on_dev(
    *,
    num,
    attr_only,
    on_device,
):
    arr = [ivy.array(np.random.uniform(size=2)) for _ in range(num)]

    # Flush to avoid artifact
    sys.stdout.flush()
    # temporarily redirect output to a buffer
    captured_output = io.StringIO()
    sys.stdout = captured_output

    ivy.print_all_ivy_arrays_on_dev(device=on_device, attr_only=attr_only)
    # Flush again to make sure all data is printed
    sys.stdout.flush()
    written = captured_output.getvalue().splitlines()
    # restore stdout
    sys.stdout = sys.__stdout__

    # Should have written same number of lines as the number of array in device
    assert len(written) == num

    if attr_only:
        # Check that the attribute are printed are in the format of ((dim,...), type)
        regex = r"^\(\((\d+,(\d,\d*)*)\), \'\w*\'\)$"
    else:
        # Check that the arrays are printed are in the format of ivy.array(...)
        regex = r"^ivy\.array\(\[.*\]\)$"

    # Clear the array from device
    for item in arr:
        del item

    # Apply the regex search
    assert all([re.match(regex, line) for line in written])


@handle_test(fn_tree="total_mem_on_dev")
def test_total_mem_on_dev():
    devices = _get_possible_devices()
    for device in devices:
        if "cpu" in device:
            assert ivy.total_mem_on_dev(device) == psutil.virtual_memory().total / 1e9
        elif "gpu" in device:
            gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(device)
            assert ivy.total_mem_on_dev(device) == gpu_mem / 1e9


@handle_test(fn_tree="used_mem_on_dev")
def test_used_mem_on_dev():
    devices = _get_possible_devices()

    # Check that there not all memory is used
    for device in devices:
        assert ivy.used_mem_on_dev(device) > 0
        assert ivy.used_mem_on_dev(device) < ivy.total_mem_on_dev(device)

    # Testing if it's detects changes in RAM usage, cannot apply this to GPU, as we can
    # only get the total memory usage of a GPU, not the usage by the program.
    _ram_array_and_clear_test(
        lambda: ivy.used_mem_on_dev(ivy.Device("cpu"), process_specific=True)
    )


@handle_test(fn_tree="percent_used_mem_on_dev")
def test_percent_used_mem_on_dev():
    devices = _get_possible_devices()

    for device in devices:
        used = ivy.percent_used_mem_on_dev(ivy.Device(device))
        assert 0 <= used <= 100

    # Same as test_used_mem_on_dev, but using percent of total memory as metric function
    _ram_array_and_clear_test(
        lambda: ivy.percent_used_mem_on_dev(ivy.Device("cpu"), process_specific=True)
    )


@handle_test(fn_tree="gpu_is_available")
def test_gpu_is_available():
    # If gpu is available but cannot be initialised it will fail the test
    if ivy.gpu_is_available():
        try:
            pynvml.nvmlInit()
        except pynvml.NVMLError:
            assert False


@handle_test(fn_tree="num_cpu_cores")
def test_num_cpu_cores():
    # using multiprocessing module too because ivy uses psutil as basis.
    p_cpu_cores = psutil.cpu_count()
    m_cpu_cores = multiprocessing.cpu_count()
    assert type(ivy.num_cpu_cores()) == int
    assert ivy.num_cpu_cores() == p_cpu_cores
    assert ivy.num_cpu_cores() == m_cpu_cores


def _composition_1():
    return ivy.relu().argmax()


def _composition_2():
    a = ivy.floor
    return ivy.ceil() or a


# function_unsupported_devices
@handle_test(
    fn_tree="functional.ivy.function_supported_devices",
    func=st.sampled_from([_composition_1, _composition_2]),
    expected=st.just(["cpu"]),
)
def test_function_supported_devices(
    *,
    func,
    expected,
):
    res = ivy.function_supported_devices(func)
    exp = set(expected)

    assert sorted(tuple(exp)) == sorted(res)


# function_unsupported_devices
@handle_test(
    fn_tree="functional.ivy.function_supported_devices",
    func=st.sampled_from([_composition_1, _composition_2]),
    expected=st.just(["gpu", "tpu"]),
)
def test_function_unsupported_devices(
    *,
    func,
    expected,
):
    res = ivy.function_unsupported_devices(func)
    exp = set(expected)

    assert sorted(tuple(exp)) == sorted(res)


# Still to Add #
# ---------------#


# clear_mem_on_dev
# used_mem_on_dev # working fine for cpu
# percent_used_mem_on_dev # working fine for cpu
# dev_util # working fine for cpu
# tpu_is_available
# _assert_dev_correct_formatting
