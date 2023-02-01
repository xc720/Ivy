# global
import tensorflow as tf
from typing import Tuple, Union, Optional
from collections import namedtuple
from ivy.func_wrapper import with_unsupported_dtypes
from . import backend_version


@with_unsupported_dtypes({"2.9.1 and below": ("complex",)}, backend_version)
def unique_all(
    x: Union[tf.Tensor, tf.Variable],
    /,
) -> Tuple[
    Union[tf.Tensor, tf.Variable],
    Union[tf.Tensor, tf.Variable],
    Union[tf.Tensor, tf.Variable],
    Union[tf.Tensor, tf.Variable],
]:
    Results = namedtuple(
        "Results",
        ["values", "indices", "inverse_indices", "counts"],
    )
    flat_tensor = tf.reshape(x, [-1])
    values, inverse_indices, counts = tf.unique_with_counts(tf.sort(flat_tensor))
    tensor_list = flat_tensor.numpy().tolist()
    if (
        x.dtype.is_floating
        and tf.math.reduce_sum(tf.cast(tf.math.is_nan(values), "float32")).numpy()
    ):
        unique_nan = tf.math.is_nan(values).numpy()

        nan_index = tf.where(tf.math.is_nan(flat_tensor)).numpy().reshape([-1])
        non_nan_index = tf.experimental.numpy.array(
            [tensor_list.index(val) for val in values if not tf.math.is_nan(val)]
        )

        indices = tf.experimental.numpy.full(
            fill_value=float("NaN"), shape=values.shape
        ).numpy()

        indices[unique_nan] = nan_index
        indices[~unique_nan] = non_nan_index
        indices = tf.convert_to_tensor(indices)
    else:
        values_list = values.numpy().tolist()
        indices = [tensor_list.index(val) for val in values_list]
        indices = tf.convert_to_tensor(indices)
        inverse_indices = [values_list.index(val) for val in tensor_list]
        inverse_indices = tf.convert_to_tensor(inverse_indices)

    return Results(
        tf.cast(values, x.dtype),
        tf.cast(indices, dtype=tf.int64),
        tf.cast(tf.reshape(inverse_indices, x.shape), dtype=tf.int64),
        tf.cast(counts, dtype=tf.int64),
    )


@with_unsupported_dtypes({"2.9.1 and below": ("complex",)}, backend_version)
def unique_counts(
    x: Union[tf.Tensor, tf.Variable],
    /,
) -> Tuple[Union[tf.Tensor, tf.Variable], Union[tf.Tensor, tf.Variable]]:
    Results = namedtuple("Results", ["values", "counts"])
    v, _, c = tf.unique_with_counts(tf.sort(tf.reshape(x, [-1])))
    v = tf.cast(v, dtype=x.dtype)
    c = tf.cast(c, dtype=tf.int64)
    return Results(v, c)


@with_unsupported_dtypes({"2.9.1 and below": ("complex",)}, backend_version)
def unique_inverse(
    x: Union[tf.Tensor, tf.Variable],
    /,
) -> Tuple[Union[tf.Tensor, tf.Variable], Union[tf.Tensor, tf.Variable]]:
    Results = namedtuple("Results", ["values", "inverse_indices"])
    flat_tensor = tf.reshape(x, -1)
    values = tf.unique(tf.sort(flat_tensor))[0]
    values = tf.cast(values, dtype=x.dtype)

    values_list = values.numpy().tolist()
    inverse_indices = [values_list.index(val) for val in flat_tensor.numpy().tolist()]
    inverse_indices = tf.reshape(tf.convert_to_tensor(inverse_indices), x.shape)
    inverse_indices = tf.cast(inverse_indices, dtype=tf.int64)
    return Results(values, inverse_indices)


@with_unsupported_dtypes({"2.9.1 and below": ("complex",)}, backend_version)
def unique_values(
    x: Union[tf.Tensor, tf.Variable],
    /,
    *,
    out: Optional[Union[tf.Tensor, tf.Variable]] = None,
) -> Union[tf.Tensor, tf.Variable]:
    ret = tf.unique(tf.reshape(x, [-1]))[0]
    return tf.sort(ret)
