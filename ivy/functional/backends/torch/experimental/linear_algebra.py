# global
import math

import torch
from typing import Optional, Tuple

import ivy
from ivy.func_wrapper import with_unsupported_dtypes
from .. import backend_version

from ivy.functional.ivy.experimental.linear_algebra import _check_valid_dimension_size


@with_unsupported_dtypes({"1.13.0 and below": ("float16",)}, backend_version)
def diagflat(
    x: torch.Tensor,
    /,
    *,
    offset: Optional[int] = 0,
    padding_value: Optional[float] = 0,
    align: Optional[str] = "RIGHT_LEFT",
    num_rows: Optional[int] = -1,
    num_cols: Optional[int] = -1,
    out: Optional[torch.Tensor] = None,
):
    if len(x.shape) > 1:
        x = torch.flatten(x)
    # if len(x.shape) == 1 and offset == 0 and num_rows <= 1 and num_cols <= 1:
    if math.prod(x.shape) == 1 and offset == 0 and num_rows <= 1 and num_cols <= 1:
        return x

    # This is used as part of Tensorflow's shape calculation
    # See their source code to see what they're doing with it
    lower_diag_index = offset
    upper_diag_index = lower_diag_index

    x_shape = x.shape
    x_rank = len(x_shape)

    num_diags = upper_diag_index - lower_diag_index + 1
    max_diag_len = x_shape[x_rank - 1]

    min_num_rows = max_diag_len - min(upper_diag_index, 0)
    min_num_cols = max_diag_len + max(lower_diag_index, 0)

    if num_rows == -1 and num_cols == -1:
        num_rows = max(min_num_rows, min_num_cols)
        num_cols = num_rows
    elif num_rows == -1:
        num_rows = min_num_rows
    elif num_cols == -1:
        num_cols = min_num_cols

    output_shape = list(x_shape)
    if num_diags == 1:
        output_shape[x_rank - 1] = num_rows
        output_shape.append(num_cols)
    else:
        output_shape[x_rank - 2] = num_rows
        output_shape[x_rank - 1] = num_cols

    output_array = torch.full(tuple(output_shape), padding_value, dtype=x.dtype)
    output_array = output_array.to(x.dtype)

    diag_len = max(min(num_rows, num_cols) - abs(offset) + 1, 1)

    if len(x) < diag_len:
        x = torch.tensor(
            list(x) + [padding_value] * max((diag_len - len(x), 0)), dtype=x.dtype
        )

    temp = x - torch.full(x.shape, padding_value).type(x.dtype)
    diagonal_to_add = torch.diag(temp, diagonal=offset).type(
        x.dtype
    )  # diag does not support float16

    diagonal_to_add = diagonal_to_add[tuple(slice(0, n) for n in output_array.shape)]
    diagonal_to_add = diagonal_to_add.to(x.dtype)

    output_array += torch.nn.functional.pad(
        diagonal_to_add,
        (
            0,
            max([output_array.shape[1] - diagonal_to_add.shape[1], 0]),
            0,
            max([output_array.shape[0] - diagonal_to_add.shape[0], 0]),
        ),
        "constant",
        0,
    ).type(x.dtype)
    ret = output_array.type(x.dtype)

    if ivy.exists(out):
        ivy.inplace_update(out, ret)

    return ret


diagflat.support_native_out = False


def kron(
    a: torch.Tensor,
    b: torch.Tensor,
    /,
    *,
    out: Optional[torch.Tensor] = None,
) -> torch.tensor:
    return torch.kron(a, b, out=out)


kron.support_native_out = True


def matrix_exp(
    x: torch.Tensor,
    /,
    *,
    out: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    return torch.exp(x, out=out)


matrix_exp.support_native_out = True


def eig(
    x: torch.Tensor, /, *, out: Optional[torch.Tensor] = None
) -> Tuple[torch.Tensor]:
    if not torch.is_complex(x):
        x = x.to(torch.complex128)
    return torch.linalg.eig(x)


eig.support_native_out = False


def eigvals(x: torch.Tensor, /) -> torch.Tensor:
    if not torch.is_complex(x):
        x = x.to(torch.complex128)
    return torch.linalg.eigvals(x)


eigvals.support_native_out = False


def adjoint(
    x: torch.Tensor,
    /,
    *,
    out: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    _check_valid_dimension_size(x)
    return torch.adjoint(x).resolve_conj()
