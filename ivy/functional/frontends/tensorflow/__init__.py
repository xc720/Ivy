# flake8: noqa
# local
from ivy.exceptions import handle_exceptions
import ivy
from numbers import Number
from typing import Union, Tuple, Iterable
from .dtypes import DType

tensorflow_enum_to_type = {
    1: ivy.float32,
    2: ivy.float64,
    3: ivy.int32,
    4: ivy.uint8,
    5: ivy.int16,
    6: ivy.int8,
    8: ivy.complex64,
    9: ivy.int64,
    10: ivy.bool,
    14: ivy.bfloat16,
    17: ivy.uint16,
    18: ivy.complex128,
    19: ivy.float16,
    22: ivy.uint32,
    23: ivy.uint64,
}

tensorflow_type_to_enum = {v: k for k, v in tensorflow_enum_to_type.items()}


float32 = DType(1)
float64 = DType(2)
int32 = DType(3)
uint8 = DType(4)
int16 = DType(5)
int8 = DType(6)
int64 = DType(9)
bool = DType(10)
bfloat16 = DType(14)
uint16 = DType(17)
float16 = DType(19)
uint32 = DType(22)
uint64 = DType(23)

# type aliases
double = float64
half = float16


@handle_exceptions
def check_tensorflow_casting(x1, x2):
    """
    Checks whether the two arguments provided in the function have the same dtype,
    unless one of them is an array_like or scalar,
    where it gets casted to the other input's dtype

    Parameters
    ----------
    x1
        First argument which can be tensor, array_like or scalar
    x2
        Second argument which can be tensor, array_like or scalar

    Returns
    -------
    x1
        First tensor promoted accordingly.
    x2
        Second tensor promoted accordingly.

    """
    if hasattr(x1, "dtype") and not hasattr(x2, "dtype"):
        x1 = ivy.asarray(x1)
        x2 = ivy.asarray(x2, dtype=x1.dtype)
    else:
        x1 = ivy.asarray(x1)
        if not hasattr(x2, "dtype"):
            x2 = ivy.asarray(x2, dtype=x1.dtype)
        ivy.assertions.check_same_dtype(x1, x2)
    return x1, x2


from . import dtypes
from .dtypes import DType, as_dtype, cast
from . import ragged
from .ragged import *
from . import tensor
from .tensor import EagerTensor, Tensor
from . import keras
from . import compat
from . import linalg
from . import math
from .math import *
from . import nest
from . import nn
from . import quantization
from . import random
from . import general_functions
from .general_functions import *
from . import raw_ops
from . import sets
from . import signal
from . import sparse
