# local
import ivy
from ivy.functional.frontends.jax.func_wrapper import (
    to_ivy_arrays_and_back,
    handle_jax_dtype,
)
from ivy.functional.frontends.jax.numpy import promote_types_of_jax_inputs


@to_ivy_arrays_and_back
def einsum(
    subscripts,
    *operands,
    out=None,
    optimize="optimal",
    precision=None,
    _use_xeinsum=False,
):
    return ivy.einsum(subscripts, *operands, out=out)


@handle_jax_dtype
@to_ivy_arrays_and_back
def mean(a, axis=None, dtype=None, out=None, keepdims=False, *, where=None):
    axis = tuple(axis) if isinstance(axis, list) else axis
    if dtype is None:
        dtype = "float32" if ivy.is_int_dtype(a) else a.dtype
    ret = ivy.mean(a, axis=axis, keepdims=keepdims, out=out)
    if ivy.is_array(where):
        where = ivy.array(where, dtype=ivy.bool)
        ret = ivy.where(where, ret, ivy.default(out, ivy.zeros_like(ret)), out=out)
    return ivy.astype(ret, ivy.as_ivy_dtype(dtype), copy=False)


@handle_jax_dtype
@to_ivy_arrays_and_back
def var(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False, *, where=None):
    axis = tuple(axis) if isinstance(axis, list) else axis
    if dtype is None:
        dtype = "float32" if ivy.is_int_dtype(a) else a.dtype
    ret = ivy.var(a, axis=axis, correction=ddof, keepdims=keepdims, out=out)
    if ivy.is_array(where):
        where = ivy.array(where, dtype=ivy.bool)
        ret = ivy.where(where, ret, ivy.default(out, ivy.zeros_like(ret)), out=out)
    return ivy.astype(ret, ivy.as_ivy_dtype(dtype), copy=False)


@to_ivy_arrays_and_back
def argmin(a, axis=None, out=None, keepdims=None):
    return ivy.argmin(a, axis=axis, out=out, keepdims=keepdims)


@to_ivy_arrays_and_back
def bincount(x, weights=None, minlength=0, *, length=None):
    x_list = []
    for i in range(x.shape[0]):
        x_list.append(int(x[i]))
    max_val = int(ivy.max(ivy.array(x_list)))
    ret = [x_list.count(i) for i in range(0, max_val + 1)]
    ret = ivy.array(ret)
    ret = ivy.astype(ret, ivy.as_ivy_dtype(ivy.int64))
    return ret


@handle_jax_dtype
@to_ivy_arrays_and_back
def cumprod(a, axis=None, dtype=None, out=None):
    if dtype is None:
        dtype = ivy.as_ivy_dtype(a.dtype)
    return ivy.cumprod(a, axis=axis, dtype=dtype, out=out)


@handle_jax_dtype
@to_ivy_arrays_and_back
def cumsum(a, axis=0, dtype=None, out=None):
    if dtype is None:
        dtype = ivy.uint8
    return ivy.cumsum(a, axis, dtype=dtype, out=out)


cumproduct = cumprod


@handle_jax_dtype
@to_ivy_arrays_and_back
def sum(
    a,
    axis=None,
    dtype=None,
    out=None,
    keepdims=False,
    initial=None,
    where=None,
    promote_integers=True,
):
    if dtype is None:
        dtype = "float32" if ivy.is_int_dtype(a.dtype) else ivy.as_ivy_dtype(a.dtype)

    # TODO: promote_integers is only supported from JAX v0.3.14
    if dtype is None and promote_integers:
        if ivy.is_bool_dtype(dtype):
            dtype = ivy.default_int_dtype()
        elif ivy.is_uint_dtype(dtype):
            if ivy.dtype_bits(dtype) < ivy.dtype_bits(ivy.default_uint_dtype()):
                dtype = ivy.default_uint_dtype()
        elif ivy.is_int_dtype(dtype):
            if ivy.dtype_bits(dtype) < ivy.dtype_bits(ivy.default_int_dtype()):
                dtype = ivy.default_int_dtype()

    if initial:
        if axis is None:
            a = ivy.reshape(a, (1, -1))
            axis = 0
        s = list(ivy.shape(a))
        s[axis] = 1
        header = ivy.full(s, initial)
        a = ivy.concat([a, header], axis=axis)

    ret = ivy.sum(a, axis=axis, keepdims=keepdims, out=out)

    if ivy.is_array(where):
        where = ivy.array(where, dtype=ivy.bool)
        ret = ivy.where(where, ret, ivy.default(out, ivy.zeros_like(ret)), out=out)
    return ivy.astype(ret, ivy.as_ivy_dtype(dtype))


@to_ivy_arrays_and_back
def min(a, axis=None, out=None, keepdims=False, where=None):
    ret = ivy.min(a, axis=axis, out=out, keepdims=keepdims)
    if ivy.is_array(where):
        where = ivy.array(where, dtype=ivy.bool)
        ret = ivy.where(where, ret, ivy.default(out, ivy.zeros_like(ret)), out=out)
    return ret


amin = min


@to_ivy_arrays_and_back
def max(a, axis=None, out=None, keepdims=False, where=None):
    ret = ivy.max(a, axis=axis, out=out, keepdims=keepdims)
    if ivy.is_array(where):
        where = ivy.array(where, dtype=ivy.bool)
        ret = ivy.where(where, ret, ivy.default(out, ivy.zeros_like(ret)), out=out)
    return ret


amax = max


@to_ivy_arrays_and_back
def average(a, axis=None, weights=None, returned=False, keepdims=False):

    # canonicalize_axis to ensure axis or the values in axis > 0
    if isinstance(axis, tuple) or isinstance(axis, list):
        a_ndim = len(ivy.shape(a))
        new_axis = [0] * len(axis)
        for i, v in enumerate(axis):
            if not -a_ndim <= v < a_ndim:
                raise ValueError(
                    f"axis {v} is out of bounds for array of \
                    dimension {a_ndim}"
                )
            if v < 0:
                new_axis[i] = v + a_ndim
            else:
                new_axis[i] = v
        axis = tuple(new_axis)

    if weights is None:
        ret = ivy.mean(a, axis=axis, keepdims=keepdims)
        if axis is None:
            fill_value = int(a.size) if ivy.is_int_dtype(ret) else float(a.size)
            weights_sum = ivy.full(shape=(), fill_value=fill_value, dtype=ret.dtype)
        else:
            if isinstance(axis, tuple):
                # prod with axis has dtype Sequence[int]
                fill_value = 1
                for d in axis:
                    fill_value *= a.shape[d]
            else:
                fill_value = a.shape[axis]
            fill_value = int(fill_value) if ivy.is_int_dtype(ret) else float(fill_value)
            weights_sum = ivy.full_like(ret, fill_value=fill_value)
    else:
        a = ivy.asarray(a, copy=False)
        weights = ivy.asarray(weights, copy=False)
        a, weights = promote_types_of_jax_inputs(a, weights)

        a_shape = ivy.shape(a)
        a_ndim = len(a_shape)
        weights_shape = ivy.shape(weights)

        # Make sure the dimensions work out
        if a_shape != weights_shape:
            if len(weights_shape) != 1:
                raise ValueError(
                    "1D weights expected when shapes of a and \
                    weights differ."
                )
            if axis is None:
                raise ValueError(
                    "Axis must be specified when shapes of a and \
                    weights differ."
                )
            elif isinstance(axis, tuple):
                raise ValueError(
                    "Single axis expected when shapes of a and \
                    weights differ"
                )
            elif not weights.shape[0] == a.shape[axis]:
                raise ValueError(
                    "Length of weights not compatible with \
                    specified axis."
                )

            weights = ivy.broadcast_to(
                weights, shape=(a_ndim - 1) * (1,) + weights_shape
            )
            weights = ivy.moveaxis(weights, -1, axis)

        weights_sum = ivy.sum(weights, axis=axis)
        ret = ivy.sum(a * weights, axis=axis, keepdims=keepdims) / weights_sum

    if returned:
        if ret.shape != weights_sum.shape:
            weights_sum = ivy.broadcast_to(weights_sum, shape=ret.shape)
        return ret, weights_sum

    return ret


@to_ivy_arrays_and_back
def nanmax(
    a,
    axis=None,
    out=None,
    keepdims=False,
    initial=None,
    where=True,
):
    nan_mask = ivy.isnan(a)
    a = ivy.where(ivy.logical_not(nan_mask), a, a.full_like(-ivy.inf))
    where_mask = None
    if initial is not None:
        if ivy.is_array(where):
            a = ivy.where(where, a, a.full_like(initial))
            where_mask = ivy.all(ivy.logical_not(where), axis=axis, keepdims=keepdims)
        s = ivy.shape(a, as_array=True)
        if axis is not None:
            if isinstance(axis, (tuple, list)) or ivy.is_array(axis):
                # introducing the initial in one dimension is enough
                ax = axis[0] % len(s)
                s[ax] = 1
            else:
                ax = axis % len(s)
                s[ax] = 1
        header = ivy.full(ivy.Shape(s.to_list()), initial, dtype=ivy.dtype(a))
        if axis:
            if isinstance(axis, (tuple, list)) or ivy.is_array(axis):
                a = ivy.concat([a, header], axis=axis[0])
            else:
                a = ivy.concat([a, header], axis=axis)
        else:
            a = ivy.concat([a, header], axis=0)
    res = ivy.max(a, axis=axis, keepdims=keepdims, out=out)
    if nan_mask is not None:
        nan_mask = ivy.all(nan_mask, axis=axis, keepdims=keepdims, out=out)
        if ivy.any(nan_mask):
            res = ivy.where(
                ivy.logical_not(nan_mask),
                res,
                initial if initial is not None else ivy.nan,
                out=out,
            )
    if where_mask is not None and ivy.any(where_mask):
        res = ivy.where(ivy.logical_not(where_mask), res, ivy.nan, out=out)
    return res


@to_ivy_arrays_and_back
def nanmin(
    a,
    axis=None,
    out=None,
    keepdims=False,
    initial=None,
    where=True,
):
    nan_mask = ivy.isnan(a)
    a = ivy.where(ivy.logical_not(nan_mask), a, a.full_like(+ivy.inf))
    where_mask = None
    if initial is not None:
        if ivy.is_array(where):
            a = ivy.where(where, a, a.full_like(initial))
            where_mask = ivy.all(ivy.logical_not(where), axis=axis, keepdims=keepdims)
        s = ivy.shape(a, as_array=True)
        if axis is not None:
            if isinstance(axis, (tuple, list)) or ivy.is_array(axis):
                # introducing the initial in one dimension is enough
                ax = axis[0] % len(s)
                s[ax] = 1
            else:
                ax = axis % len(s)
                s[ax] = 1
        header = ivy.full(ivy.Shape(s.to_list()), initial, dtype=ivy.dtype(a))
        if axis:
            if isinstance(axis, (tuple, list)) or ivy.is_array(axis):
                a = ivy.concat([a, header], axis=axis[0])
            else:
                a = ivy.concat([a, header], axis=axis)
        else:
            a = ivy.concat([a, header], axis=0)
    res = ivy.min(a, axis=axis, keepdims=keepdims, out=out)
    if nan_mask is not None:
        nan_mask = ivy.all(nan_mask, axis=axis, keepdims=keepdims, out=out)
        if ivy.any(nan_mask):
            res = ivy.where(
                ivy.logical_not(nan_mask),
                res,
                initial if initial is not None else ivy.nan,
                out=out,
            )
    if where_mask is not None and ivy.any(where_mask):
        res = ivy.where(ivy.logical_not(where_mask), res, ivy.nan, out=out)
    return res
