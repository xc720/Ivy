# global
import numpy as np
from hypothesis import strategies as st

# local
import ivy
import ivy_tests.test_ivy.helpers as helpers
import ivy.functional.frontends.numpy as np_frontend


@st.composite
def where(draw):
    _, values = draw(helpers.dtype_and_values(dtype=["bool"]))
    return draw(st.just(values) | st.just(True))


@st.composite
def get_casting(draw):
    return draw(st.sampled_from(["no", "equiv", "safe", "same_kind", "unsafe"]))


@st.composite
def dtype_x_bounded_axis(draw, **kwargs):
    dtype, x, shape = draw(helpers.dtype_and_values(**kwargs, ret_shape=True))
    axis = draw(helpers.ints(min_value=0, max_value=max(len(shape) - 1, 0)))
    return dtype, x, axis


@st.composite
def _array_and_axes_permute_helper(
    draw,
    *,
    min_num_dims,
    max_num_dims,
    min_dim_size,
    max_dim_size,
    allow_none=False,
):
    """Returns array, its dtype and either the random permutation of its axes or None.

    Parameters
    ----------
    draw
        special function that draws data randomly (but is reproducible) from a given
        data-set (ex. list).
    min_num_dims
        minimum number of array dimensions
    max_num_dims
        maximum number of array dimensions
    min_dim_size
        minimum size of the dimension
    max_dim_size
        maximum size of the dimension

    Returns
    -------
    A strategy that draws an array, its dtype and axes (or None).
    """
    shape = draw(
        helpers.get_shape(
            allow_none=allow_none,
            min_num_dims=min_num_dims,
            max_num_dims=max_num_dims,
            min_dim_size=min_dim_size,
            max_dim_size=max_dim_size,
        )
    )
    dtype = draw(helpers.array_dtypes(num_arrays=1))
    array = draw(helpers.array_values(dtype=dtype[0], shape=shape))
    axes = draw(
        st.one_of(
            st.none(),
            helpers.get_axis(
                shape=shape,
                allow_neg=False,
                allow_none=False,
                sorted=False,
                unique=True,
                min_size=len(shape),
                max_size=len(shape),
                force_tuple=True,
                force_int=False,
            ),
        ).filter(lambda x: x != tuple(range(len(shape))))
    )
    return (array, dtype, axes)


# noinspection PyShadowingNames
def _test_frontend_function_ignoring_unitialized(*args, **kwargs):
    # TODO: this is a hack to get around, but not sure if it is efficient way to do it.
    where = kwargs["where"]
    if kwargs["frontend"] == "numpy":
        kwargs["where"] = True
    else:
        kwargs["where"] = None
    kwargs["test_values"] = False
    values = helpers.test_frontend_function(*args, **kwargs)
    if values is None:
        return
    ret, frontend_ret = values
    # set backend to frontend to flatten the frontend array
    ivy.set_backend(kwargs["frontend"])
    try:
        # get flattened arrays from returned value
        if ivy.isscalar(frontend_ret):
            frontend_ret_np_flat = [np.asarray(frontend_ret)]
        else:
            if not isinstance(frontend_ret, tuple):
                frontend_ret = (frontend_ret,)
            frontend_ret_idxs = ivy.nested_argwhere(frontend_ret, ivy.is_native_array)
            frontend_ret_flat = ivy.multi_index_nest(frontend_ret, frontend_ret_idxs)
            frontend_ret_np_flat = [ivy.to_numpy(x) for x in frontend_ret_flat]
    except Exception as e:
        ivy.unset_backend()
        raise e
    # set backend back to original
    ivy.unset_backend()

    # get flattened arrays from returned value
    ret_np_flat = helpers.flatten_fw_and_to_np(ret=ret, fw=kwargs["frontend"])

    # handling where size
    where = np.asarray(where)
    if where.ndim == 0:
        where = np.array([where])
    elif where.ndim > 1:
        where = where.flatten()
    # handling ret size

    first_el = ret_np_flat[0]
    # change where to match the shape of the first element of ret_np_flat
    if first_el.size == 1:
        where = where[:1]
    else:
        where = np.repeat(where, first_el.size)
        where = where[: first_el.size]
        where = where.reshape(first_el.shape)

    ret_flat = [np.where(where, x, np.zeros_like(x)) for x in ret_np_flat]
    frontend_ret_flat = [
        np.where(where, x, np.zeros_like(x)) for x in frontend_ret_np_flat
    ]
    if "rtol" in kwargs.keys():
        rtol = kwargs["rtol"]
    else:
        rtol = 1e-4
    if "atol" in kwargs.keys():
        atol = kwargs["atol"]
    else:
        atol = 1e-6
    helpers.value_test(
        ret_np_flat=ret_flat,
        ret_np_from_gt_flat=frontend_ret_flat,
        rtol=rtol,
        atol=atol,
    )


# noinspection PyShadowingNames
def test_frontend_function(*args, where=None, **kwargs):
    if not ivy.exists(where):
        helpers.test_frontend_function(*args, **kwargs)
    else:
        kwargs["where"] = where
        if "out" in kwargs and kwargs["out"] is None:
            _test_frontend_function_ignoring_unitialized(*args, **kwargs)
            return
        else:
            helpers.test_frontend_function(*args, **kwargs)


# noinspection PyShadowingNames
def handle_where_and_array_bools(where, input_dtype, test_flags):
    if isinstance(where, list) or isinstance(where, tuple):
        where = where[0]
        test_flags.as_variable += [False]
        test_flags.native_arrays += [False]
        input_dtype += ["bool"]
        return where, input_dtype, test_flags
    return where, input_dtype, test_flags


def handle_dtype_and_casting(
    *,
    dtypes,
    get_dtypes_kind="valid",
    get_dtypes_index=0,
    get_dtypes_none=True,
    get_dtypes_key=None,
):
    casting = get_casting()
    if casting in ["no", "equiv"]:
        dtype = dtypes[0]
        dtypes = [dtype for x in dtypes]
        return dtype, dtypes, casting
    dtype = helpers.get_dtypes(
        get_dtypes_kind,
        index=get_dtypes_index,
        full=False,
        none=get_dtypes_none,
        key=get_dtypes_key,
    )
    if casting in ["safe", "same_kind"]:
        while not ivy.all([ivy.can_cast(x, dtype) for x in dtypes]):
            dtype = helpers.get_dtypes(
                get_dtypes_kind,
                index=get_dtypes_index,
                full=False,
                none=get_dtypes_none,
                key=get_dtypes_key,
            )
    return dtype, dtypes, casting


@st.composite
def _get_safe_casting_dtype(draw, *, dtypes):
    target_dtype = dtypes[0]
    for dtype in dtypes[1:]:
        if ivy.can_cast(target_dtype, dtype):
            target_dtype = dtype
    if ivy.is_float_dtype(target_dtype):
        dtype = draw(st.sampled_from(["float64", None]))
    elif ivy.is_uint_dtype(target_dtype):
        dtype = draw(st.sampled_from(["uint64", None]))
    elif ivy.is_int_dtype(target_dtype):
        dtype = draw(st.sampled_from(["int64", None]))
    else:
        dtype = draw(st.sampled_from(["bool", None]))
    # filter uint64 as not supported by torch backend
    if dtype == "uint64":
        dtype = None
    return dtype


@st.composite
def dtypes_values_casting_dtype(
    draw,
    *,
    arr_func,
    get_dtypes_kind="valid",
    get_dtypes_index=0,
    get_dtypes_none=True,
    get_dtypes_key=None,
    special=False,
):
    dtypes, values = [], []
    casting = draw(st.sampled_from(["no", "equiv", "safe", "same_kind", "unsafe"]))
    for func in arr_func:
        typ, val = draw(func())
        dtypes += typ if isinstance(typ, list) else [typ]
        values += val if isinstance(val, list) else [val]

    if casting in ["no", "equiv"] and len(dtypes) > 0:
        dtypes = [dtypes[0]] * len(dtypes)

    if special:
        dtype = draw(st.sampled_from(["bool", None]))
    elif casting in ["no", "equiv"]:
        dtype = draw(st.just(None))
    elif casting in ["safe", "same_kind"]:
        dtype = draw(_get_safe_casting_dtype(dtypes=dtypes))

    else:
        dtype = draw(
            helpers.get_dtypes(
                kind=get_dtypes_kind,
                index=get_dtypes_index,
                full=False,
                none=get_dtypes_none,
                key=get_dtypes_key,
            )
        )[0]
        # filter uint64 as not supported by torch backend
        if dtype == "uint64":
            dtype = None
    return dtypes, values, casting, dtype


@st.composite
def get_dtype_and_values_and_casting(
    draw,
    *,
    get_dtypes_kind="valid",
    get_dtypes_index=0,
    get_dtypes_none=True,
    get_dtypes_key=None,
    **kwargs,
):
    input_dtype, x = draw(helpers.dtype_and_values(**kwargs))
    casting = draw(st.sampled_from(["no", "equiv", "safe", "same_kind", "unsafe"]))
    if casting in ["no", "equiv"]:
        dtype = input_dtype[0]
        input_dtype = [dtype for x in input_dtype]
        return dtype, input_dtype, x, casting
    dtype = draw(
        helpers.get_dtypes(
            get_dtypes_kind,
            index=get_dtypes_index,
            full=False,
            none=get_dtypes_none,
            key=get_dtypes_key,
        )
    )
    if casting in ["safe", "same_kind"]:
        while not ivy.all([ivy.can_cast(x, dtype[0]) for x in input_dtype]):
            dtype = draw(
                helpers.get_dtypes(
                    get_dtypes_kind,
                    index=get_dtypes_index,
                    full=False,
                    none=get_dtypes_none,
                    key=get_dtypes_key,
                )
            )

    return dtype[0], input_dtype, x, casting


# ufunc num_positional_args helper
@st.composite
def get_num_positional_args_ufunc(draw, *, fn_name=None):
    """
    Draws data randomly from numbers between nin and nargs
    where nin and nargs are properties of the given ufunc.

    Parameters
    ----------
    draw
        special function that draws data randomly (but is reproducible)
        from a given data-set (ex. list).
    fn_name
        name of the ufunc.

    Returns
    -------
    A strategy that can be used in the @given hypothesis decorator.
    """
    func = getattr(np_frontend, fn_name)
    nin = func.nin
    nargs = func.nargs
    return draw(st.integers(min_value=nin, max_value=nargs))
