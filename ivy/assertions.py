import ivy


# General with Custom Message #
# --------------------------- #


def check_less(x1, x2, allow_equal=False, message=""):
    # less_equal
    if allow_equal and ivy.any(x1 > x2):
        raise ivy.exceptions.IvyException(
            "{} must be lesser than or equal to {}".format(x1, x2)
            if message == ""
            else message
        )
    # less
    elif not allow_equal and ivy.any(x1 >= x2):
        raise ivy.exceptions.IvyException(
            "{} must be lesser than {}".format(x1, x2) if message == "" else message
        )


def check_greater(x1, x2, allow_equal=False, message=""):
    # greater_equal
    if allow_equal and ivy.any(x1 < x2):
        raise ivy.exceptions.IvyException(
            "{} must be greater than or equal to {}".format(x1, x2)
            if message == ""
            else message
        )
    # greater
    elif not allow_equal and ivy.any(x1 <= x2):
        raise ivy.exceptions.IvyException(
            "{} must be greater than {}".format(x1, x2) if message == "" else message
        )


def check_equal(x1, x2, inverse=False, message=""):
    # not_equal
    if inverse and ivy.any(x1 == x2):
        raise ivy.exceptions.IvyException(
            "{} must not be equal to {}".format(x1, x2) if message == "" else message
        )
    # equal
    elif not inverse and ivy.any(x1 != x2):
        raise ivy.exceptions.IvyException(
            "{} must be equal to {}".format(x1, x2) if message == "" else message
        )


def check_isinstance(x, allowed_types, message=""):
    if not isinstance(x, allowed_types):
        raise ivy.exceptions.IvyException(
            "type of x: {} must be one of the allowed types: {}".format(
                type(x), allowed_types
            )
            if message == ""
            else message
        )


def check_exists(x, inverse=False, message=""):
    # not_exists
    if inverse and ivy.exists(x):
        raise ivy.exceptions.IvyException(
            "arg must be None" if message == "" else message
        )
    # exists
    elif not inverse and not ivy.exists(x):
        raise ivy.exceptions.IvyException(
            "arg must not be None" if message == "" else message
        )


def check_elem_in_list(elem, list, message=""):
    message = message if message != "" else "{} must be one of {}".format(elem, list)
    if elem not in list:
        raise ivy.exceptions.IvyException(message)


def check_true(expression, message="expression must be True"):
    if not expression:
        raise ivy.exceptions.IvyException(message)


def check_false(expression, message="expression must be False"):
    if expression:
        raise ivy.exceptions.IvyException(message)


def check_all(results, message="one of the args is False"):
    if not ivy.all(results):
        raise ivy.exceptions.IvyException(message)


def check_any(results, message="all of the args are False"):
    if not ivy.any(results):
        raise ivy.exceptions.IvyException(message)


def check_all_or_any_fn(
    *args,
    fn,
    type="all",
    limit=[0],
    message="args must exist according to type and limit given"
):
    if type == "all":
        check_all([fn(arg) for arg in args], message)
    elif type == "any":
        count = 0
        for arg in args:
            count = count + 1 if fn(arg) else count
        if count not in limit:
            raise ivy.exceptions.IvyException(message)
    else:
        raise ivy.exceptions.IvyException("type must be all or any")


def check_shape(x1, x2, message=""):
    message = (
        message
        if message != ""
        else "{} and {} must have the same shape ({} vs {})".format(
            x1, x2, ivy.shape(x1), ivy.shape(x2)
        )
    )
    if ivy.shape(x1) != ivy.shape(x2):
        raise ivy.exceptions.IvyException(message)


def check_same_dtype(x1, x2, message=""):
    message = (
        message
        if message != ""
        else "{} and {} must have the same dtype ({} vs {})".format(
            x1, x2, ivy.dtype(x1), ivy.dtype(x2)
        )
    )
    if ivy.dtype(x1) != ivy.dtype(x2):
        raise ivy.exceptions.IvyException(message)


# Creation #
# -------- #


def check_fill_value_and_dtype_are_compatible(fill_value, dtype):
    if (
        not (
            (ivy.is_int_dtype(dtype) or ivy.is_uint_dtype(dtype))
            and isinstance(fill_value, int)
        )
        and not (
            ivy.is_complex_dtype(dtype) and isinstance(fill_value, (float, complex))
        )
        and not (
            ivy.is_float_dtype(dtype)
            and isinstance(fill_value, float)
            or isinstance(fill_value, bool)
        )
    ):
        raise ivy.exceptions.IvyException(
            "the fill_value: {} and data type: {} are not compatible".format(
                fill_value, dtype
            )
        )


# General #
# ------- #


def check_gather_input_valid(params, indices, axis, batch_dims):
    if batch_dims > axis:
        raise ivy.exceptions.IvyException(
            "batch_dims ({}) must be less than or equal to axis ({}).".format(
                batch_dims, axis
            )
        )
    if params.shape[0:batch_dims] != indices.shape[0:batch_dims]:
        raise ivy.exceptions.IvyException(
            "batch dimensions must match in `params` and `indices`;"
            + " saw {} vs. {}".format(
                params.shape[0:batch_dims], indices.shape[0:batch_dims]
            )
        )


def check_gather_nd_input_valid(params, indices, batch_dims):
    if batch_dims >= len(params.shape):
        raise ivy.exceptions.IvyException(
            "batch_dims = {} must be less than rank(`params`) = {}.".format(
                batch_dims, len(params.shape)
            )
        )
    if batch_dims >= len(indices.shape):
        raise ivy.exceptions.IvyException(
            "batch_dims = {}  must be less than rank(`indices`) = {}.".format(
                batch_dims, len(indices.shape)
            )
        )
    if params.shape[0:batch_dims] != indices.shape[0:batch_dims]:
        raise ivy.exceptions.IvyException(
            "batch dimensions must match in `params` and `indices`;"
            + " saw {} vs. {}".format(
                params.shape[0:batch_dims], indices.shape[0:batch_dims]
            )
        )
    if indices.shape[-1] > (len(params.shape[batch_dims:])):
        raise ivy.exceptions.IvyException(
            "index innermost dimension length must be <= "
            + "rank(`params[batch_dims:]`); saw: {} vs. {} .".format(
                indices.shape[-1], len(params.shape[batch_dims:])
            )
        )


def check_one_way_broadcastable(x1, x2):
    for a, b in zip(x1[::-1], x2[::-1]):
        if b == 1 or a == b:
            pass
        else:
            return False
    return True


def check_inplace_sizes_valid(var, data):
    if not check_one_way_broadcastable(var.shape, data.shape):
        raise ivy.exceptions.IvyException(
            "Could not output values of shape {} into array with shape {}.".format(
                data.shape, var.shape
            )
        )


def check_shapes_broadcastable(var, data):
    if not check_one_way_broadcastable(var, data):
        raise ivy.exceptions.IvyException(
            "Could not broadcast shape {} to shape {}.".format(data, var)
        )


def check_dimensions(x):
    if len(x.shape) <= 1:
        raise ivy.exceptions.IvyException(
            "input must have greater than one dimension; "
            + " {} has {} dimensions".format(x, len(x.shape))
        )
