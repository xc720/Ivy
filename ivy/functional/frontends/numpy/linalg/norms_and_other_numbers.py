# local
import ivy
from ivy.functional.frontends.numpy.func_wrapper import (
    to_ivy_arrays_and_back,
    from_zero_dim_arrays_to_scalar,
    inputs_to_ivy_arrays,
)

from ivy.func_wrapper import with_unsupported_dtypes


# solve
@with_unsupported_dtypes({"1.23.0 and below": ("float16",)}, "numpy")
@to_ivy_arrays_and_back
@from_zero_dim_arrays_to_scalar
def norm(x, ord=None, axis=None, keepdims=False):
    ret = ivy.vector_norm(x, axis=axis, keepdims=keepdims, ord=ord)
    if axis is None:
        return ret[0]
    return ret


# matrix_rank
# TODO: add support for hermitian
@to_ivy_arrays_and_back
@from_zero_dim_arrays_to_scalar
def matrix_rank(A, tol=None, hermitian=False):
    if A.ndim < 2:
        return int(not all(A == 0))
    S = ivy.svd(A, compute_uv=False)[0]
    if tol is None:
        tol = S.max() * max(A.shape) * ivy.finfo(S.dtype).eps
    return ivy.count_nonzero(S > tol, axis=-1).astype(ivy.int64)


# det
@to_ivy_arrays_and_back
@from_zero_dim_arrays_to_scalar
def det(a):
    return ivy.det(a)


# slogdet
@inputs_to_ivy_arrays
@from_zero_dim_arrays_to_scalar
def slogdet(a):
    sign, logabsdet = ivy.slogdet(a)
    return sign, logabsdet


# trace
@to_ivy_arrays_and_back
@from_zero_dim_arrays_to_scalar
def trace(a, offset=0, axis1=0, axis2=1, out=None):
    ret = ivy.trace(a, offset=offset, axis1=axis1, axis2=axis2, out=out)
    return ret
