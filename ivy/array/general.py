# global
import abc
import numpy as np
from numbers import Number
from typing import Any, Iterable, Union, Optional, Dict, Callable, List, Tuple

# ToDo: implement all methods here as public instance methods

# local
import ivy


class ArrayWithGeneral(abc.ABC):
    def is_native_array(
        self: ivy.Array,
        /,
        *,
        exclusive: bool = False,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.is_native_array. This method simply
        wraps the function, and so the docstring for ivy.is_native_array
        also applies to this method with minimal changes.

        Parameters
        ----------
        self
            The input to check
        exclusive
            Whether to check if the data type is exclusively an array, rather than a
            variable or traced array.

        Returns
        -------
        ret
            Boolean, whether or not x is a native array.

        Examples
        --------
        >>> x = ivy.array([0, 1, 2])
        >>> ret = x.is_native_array()
        >>> print(ret)
        False

        >>> x = ivy.native_array([9.1, -8.3])
        >>> ret = x.is_native_array(exclusive=True)
        >>> print(ret)
        True
        """
        return ivy.is_native_array(self, exclusive=exclusive)

    def is_ivy_array(self: ivy.Array, /, *, exclusive: Optional[bool] = False) -> bool:
        """
        ivy.Array instance method variant of ivy.is_ivy_array. This method simply
        wraps the function, and so the docstring for ivy.is_ivy_array also
        applies to this method with minimal changes.

        Parameters
        ----------
        self
            input array
        exclusive
            Whether to check if the data type is exclusively an array, rather than a
            variable or traced array.

        Returns
        -------
        ret
            Boolean, whether or not x is an ivy array.

        Examples
        --------
        >>> x = ivy.array([0, 1, 2])
        >>> ret = x.is_ivy_array()
        >>> print(ret)
        True

        >>> x = ivy.native_array([9.1, -8.3])
        >>> ret = x.is_ivy_array(exclusive=True)
        >>> print(ret)
        False

        """
        return ivy.is_ivy_array(self, exclusive=exclusive)

    def is_array(self: ivy.Array, /, *, exclusive: bool = False) -> bool:
        """
        ivy.Array instance method variant of ivy.is_array. This method simply wraps the
        function, and so the docstring for ivy.is_array also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            The input to check
        exclusive
            Whether to check if the data type is exclusively an array, rather than a
            variable or traced array.

        Returns
        -------
        ret
            Boolean, whether or not x is an array.

        Examples
        --------
        >>> x = ivy.array([0, 1, 2])
        >>> print(x.is_array())
        True

        >>> x = ivy.native_array([9.1, -8.3, 2.8, 3.0])
        >>> print(x.is_array(exclusive=True))
        True

        """
        return ivy.is_array(self, exclusive=exclusive)

    def is_ivy_container(self: ivy.Array) -> bool:
        """
        ivy.Array instance method variant of ivy.is_ivy_container. This method simply
        wraps the function, and so the docstring for ivy.is_ivy_container also applies
        to this method with minimal changes.

        Parameters
        ----------
        self
            The input to check

        Returns
        -------
        ret
            Boolean, whether or not x is an ivy container.

        Examples
        --------
        >>> x = ivy.array([0, 1, 2])
        >>> print(x.is_ivy_container())
        False
        """
        return ivy.is_ivy_container(self)

    def all_equal(
        self: ivy.Array, *x2: Iterable[Any], equality_matrix: bool = False
    ) -> Union[bool, ivy.Array, ivy.NativeArray]:
        """
        ivy.Array instance method variant of ivy.all_equal. This method simply wraps the
        function, and so the docstring for ivy.all_equal also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array
        x2
            input iterable to compare to ``self``
        equality_matrix
            Whether to return a matrix of equalities comparing each input with every
            other. Default is ``False``.

        Returns
        -------
        ret
            Boolean, whether or not the inputs are equal, or matrix array of booleans if
            equality_matrix=True is set.

        Examples
        --------
        >>> x1 = ivy.array([1, 1, 0, 0, 1, -1])
        >>> x2 = ivy.array([1, 1, 0, 0, 1, -1])
        >>> y = x1.all_equal(x2)
        >>> print(y)
        True

        >>> x1 = ivy.array([0, 0])
        >>> x2 = ivy.array([0, 0])
        >>> x3 = ivy.array([1, 0])
        >>> y = x1.all_equal(x2, x3, equality_matrix=True)
        >>> print(y)
        ivy.array([[ True,  True, False],
           [ True,  True, False],
           [False, False,  True]])
        """
        arrays = [self] + [x for x in x2]
        return ivy.all_equal(*arrays, equality_matrix=equality_matrix)

    def has_nans(self: ivy.Array, /, *, include_infs: bool = True):
        """
        ivy.Array instance method variant of ivy.has_nans. This method simply wraps the
        function, and so the docstring for ivy.has_nans also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array
        include_infs
            Whether to include ``+infinity`` and ``-infinity`` in the check.
            Default is ``True``.

        Returns
        -------
        ret
            Boolean as to whether the array contains nans.

        Examples
        --------
        >>> x = ivy.array([1, 2, 3])
        >>> y = x.has_nans()
        >>> print(y)
        False
        """
        return ivy.has_nans(self, include_infs=include_infs)

    def gather(
        self: ivy.Array,
        indices: Union[ivy.Array, ivy.NativeArray],
        /,
        *,
        axis: Optional[int] = -1,
        batch_dims: Optional[int] = 0,
        out: Optional[ivy.Array] = None,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.gather. This method simply
        wraps the function, and so the docstring for ivy.gather also applies to
        this method with minimal changes.

        Parameters
        ----------
        self
            The array from which to gather values.
        indices
            The array which indicates the indices that will be gathered along
            the specified axis.
        axis
            The axis from which the indices will be gathered. Default is ``-1``.
        batch_dims
            optional int, lets you gather different items from each element of a batch.
        out
            optional array, for writing the result to. It must have a shape
            that the inputs broadcast to.

        Returns
        -------
        ret
            New array with the values gathered at the specified indices along
            the specified axis.

        Examples
        --------
        >>> x = ivy.array([0., 1., 2.])
        >>> y = ivy.array([0, 1])
        >>> x.gather(y)
        ivy.array([0., 1.])

        """
        return ivy.gather(
            self._data, indices, axis=axis, batch_dims=batch_dims, out=out
        )

    def scatter_nd(
        self: ivy.Array,
        updates: Union[ivy.Array, ivy.NativeArray],
        /,
        shape: Optional[ivy.Array] = None,
        *,
        reduction: str = "sum",
        out: Optional[ivy.Array] = None,
    ) -> ivy.Array:
        """
        Scatter updates into an array according to indices.

        Parameters
        ----------
        self
            array of indices
        updates
            values to update input tensor with
        shape
            The shape of the result. Default is ``None``, in which case tensor
            argument must be provided.
        reduction
            The reduction method for the scatter, one of 'sum', 'min', 'max'
            or 'replace'
        out
            optional output array, for writing the result to.

        Returns
        -------
        ret
            New array of given shape, with the values scattered at the indices.

        Examples
        --------
        With scatter values into an array

        >>> arr = ivy.array([1,2,3,4,5,6,7,8, 9, 10])
        >>> indices = ivy.array([[4], [3], [1], [7]])
        >>> updates = ivy.array([9, 10, 11, 12])
        >>> scatter = indices.scatter_nd(updates, reduction='replace', out=arr)
        >>> print(scatter)
        ivy.array([ 1, 11,  3, 10,  9,  6,  7, 12,  9, 10])

        With scatter values into an empty array

        >>> shape = ivy.array([2, 5])
        >>> indices = ivy.array([[1,4], [0,3], [1,1], [0,2]])
        >>> updates = ivy.array([25, 40, 21, 22])
        >>> scatter = indices.scatter_nd(updates, shape=shape)
        >>> print(scatter)
        ivy.array([[ 0,  0, 22, 40,  0],
                    [ 0, 21,  0,  0, 25]])
        """
        return ivy.scatter_nd(self, updates, shape, reduction=reduction, out=out)

    def gather_nd(
        self: ivy.Array,
        indices: Union[ivy.Array, ivy.NativeArray],
        /,
        *,
        batch_dims: Optional[int] = 0,
        out: Optional[ivy.Array] = None,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.gather_nd. This method simply wraps the
        function, and so the docstring for ivy.gather_nd also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            The array from which to gather values.
        indices
            Index array.
        out
            optional output array, for writing the result to. It must have a shape that
            the inputs broadcast to.

        Returns
        -------
        ret
            New array of given shape, with the values gathered at the indices.

        Examples
        --------
        >>> x = ivy.array([1, 2, 3])
        >>> y = ivy.array([1])
        >>> z = x.gather_nd(y)
        >>> print(z)
        ivy.array(2)
        """
        return ivy.gather_nd(self, indices, batch_dims=batch_dims, out=out)

    def einops_rearrange(
        self: ivy.Array,
        pattern: str,
        /,
        *,
        out: Optional[ivy.Array] = None,
        **axes_lengths: Dict[str, int],
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.einops_rearrange.
        This method simply wraps the function, and so the docstring
        for ivy.einops_rearrange also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            Input array to be re-arranged.
        pattern
            Rearrangement pattern.
        axes_lengths
            Any additional specifications for dimensions.
        out
            optional output array, for writing the result to. It must have a shape
            that the inputs broadcast to.

        Returns
        -------
        ret
            New array with einops.rearrange having been applied.

        Examples
        --------
        With :class:`ivy.Array` instance method:

        >>> x = ivy.array([[1, 2, 3],
        ...               [-4, -5, -6]])
        >>> y = x.einops_rearrange("height width -> width height")
        >>> print(y)
        ivy.array([[ 1, -4],
            [ 2, -5],
            [ 3, -6]])

        >>> x = ivy.array([[[ 1,  2,  3],
        ...                  [ 4,  5,  6]],
        ...               [[ 7,  8,  9],
        ...                  [10, 11, 12]]])
        >>> y = x.einops_rearrange("c h w -> c (h w)")
        >>> print(y)
        ivy.array([[ 1,  2,  3,  4,  5,  6],
            [ 7,  8,  9, 10, 11, 12]])

        >>> x = ivy.array([[1, 2, 3, 4, 5, 6]
        ...               [7, 8, 9, 10, 11, 12]])
        >>> y = x.einops_rearrange("c (h w) -> (c h) w", h=2, w=3)
        ivy.array([[ 1,  2,  3],
            [ 4,  5,  6],
            [ 7,  8,  9],
            [10, 11, 12]])

        """
        return ivy.einops_rearrange(self._data, pattern, out=out, **axes_lengths)

    def einops_reduce(
        self: ivy.Array,
        pattern: str,
        reduction: Union[str, Callable],
        /,
        *,
        out: Optional[ivy.Array] = None,
        **axes_lengths: Dict[str, int],
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.einops_reduce. This method simply
        wraps the function, and so the docstring for ivy.einops_reduce also applies
        to this method with minimal changes.

        Parameters
        ----------
        self
            Input array to be reduced.
        pattern
            Reduction pattern.
        reduction
            One of available reductions ('min', 'max', 'sum', 'mean', 'prod'), or
            callable.
        axes_lengths
            Any additional specifications for dimensions.
        out
            optional output array, for writing the result to. It must have a shape
            that the inputs broadcast to.

        Returns
        -------
        ret
            New array with einops.reduce having been applied.

        Examples
        --------
        >>> x = ivy.array([[[5, 4],
        ...                 [11, 2]],
        ...                [[3, 5],
        ...                 [9, 7]]])

        >>> y = x.einops_reduce('a b c -> b c', 'max')
        >>> print(y)
        ivy.array([[ 5,  5],
                   [11,  7]])

        >>> x = ivy.array([[[5, 4, 3],
        ...                 [11, 2, 9]],
        ...                [[3, 5, 7],
        ...                 [9, 7, 1]]])
        >>> y = x.einops_reduce('a b c -> a () c', 'min')
        >>> print(y)
        ivy.array([[[5, 2, 3]],
                   [[3, 5, 1]]])
        """
        return ivy.einops_reduce(
            self._data, pattern, reduction, out=out, **axes_lengths
        )

    def einops_repeat(
        self: ivy.Array,
        pattern: str,
        /,
        *,
        out: Optional[ivy.Array] = None,
        **axes_lengths: Dict[str, int],
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.einops_repeat. This method simply
        wraps the function, and so the docstring for ivy.einops_repeat also applies
        to this method with minimal changes.

        Parameters
        ----------
        self
            Input array to be repeated.
        pattern
            Rearrangement pattern.
        axes_lengths
            Any additional specifications for dimensions.
        out
            optional output array, for writing the result to. It must have a shape
            that the inputs broadcast to.

        Returns
        -------
        ret
            New array with einops.repeat having been applied.

        Examples
        --------
        >>> x = ivy.array([5,4])
        >>> y = x.einops_repeat('a -> a c', c=3)
        >>> print(y)
        ivy.array([[5,5,5],[4,4,4]])

        >>> x = ivy.array([[5,4],
        ...                [2, 3]])
        >>> y = x.einops_repeat('a b ->  a b c', c=3)
        >>> print(y)
        ivy.array([[5,5,5],[4,4,4]])

        """
        return ivy.einops_repeat(self._data, pattern, out=out, **axes_lengths)

    def to_numpy(self: ivy.Array, /, *, copy: bool = True) -> np.ndarray:
        """
        ivy.Array instance method variant of ivy.to_numpy. This method simply wraps
        the function, and so the docstring for ivy.to_numpy also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array.

        Returns
        -------
        ret
            a numpy array copying all the element of the array ``self``.

        Examples
        --------
        With :class:`ivy.Array` inputs:

        >>> x = ivy.array([-1, 0, 1])
        >>> y = x.to_numpy()
        >>> print(y)
        [-1  0  1]

        >>> x = ivy.array([[-1, 0, 1],[-1, 0, 1], [1,0,-1]])
        >>> y = x.to_numpy()
        >>> print(y)
        [[-1  0  1]
        [-1  0  1]
        [ 1  0 -1]]

        """
        return ivy.to_numpy(self, copy=copy)

    def to_list(self: ivy.Array, /) -> List:
        """
        ivy.Array instance method variant of ivy.to_list. This method simply wraps
        the function, and so the docstring for ivy.to_list also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array.

        Returns
        -------
        ret
            A list representation of the input array ``x``.

        Examples
        --------
        With :class:`ivy.Array` instance method:

        >>> x = ivy.array([0, 1, 2])
        >>> y = x.to_list()
        >>> print(y)
        [0, 1, 2]
        """
        return ivy.to_list(self)

    def supports_inplace_updates(self: ivy.Array) -> bool:
        """
        ivy.Array instance method variant of ivy.supports_inplace_updates. This method
        simply wraps the function, and so the docstring for ivy.supports_inplace also
        applies to this method with minimal changes.

        Parameters
        ----------
        self
            The input array whose elements' data type is to be checked.

        Returns
        -------
        ret
            Bool value depends on whether the currently active backend
            framework supports in-place operations with argument's data type.

        Examples
        --------
        With `ivy.Array` input and backend set as "tensorflow":

        >>> x = ivy.array([1., 4.2, 2.2])
        >>> ret = x.supports_inplace_updates()
        >>> print(ret)
        False
        """
        return ivy.supports_inplace_updates(self)

    def inplace_decrement(
        self: Union[ivy.Array, ivy.NativeArray], val: Union[ivy.Array, ivy.NativeArray]
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.inplace_decrement. This method simply
        wraps the function, and so the docstring for ivy.inplace_decrement also
        applies to this method with minimal changes.

        Parameters
        ----------
        self
            The input array to be decremented by the defined value.
        val
            The value of decrement.

        Returns
        -------
        ret
            The array following an in-place decrement.

        Examples
        --------
        With :class:`ivy.Array` instance methods:

        >>> x = ivy.array([5.7, 4.3, 2.5, 1.9])
        >>> y = x.inplace_decrement(1)
        >>> print(y)
        ivy.array([4.7, 3.3, 1.5, 0.9])

        >>> x = ivy.asarray([4., 5., 6.])
        >>> y = x.inplace_decrement(2.5)
        >>> print(y)
        ivy.array([1.5, 2.5, 3.5])

        """
        return ivy.inplace_decrement(self, val)

    def stable_divide(
        self,
        denominator: Union[Number, ivy.Array, ivy.NativeArray, ivy.Container],
        min_denominator: Union[
            Number, ivy.Array, ivy.NativeArray, ivy.Container
        ] = None,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.stable_divide. This method simply wraps
        the function, and so the docstring for ivy.stable_divide also applies to this
        method with minimal changes.

        Parameters
        ----------
        self
            input array, used as the numerator for division.
        denominator
            denominator for division.
        min_denominator
            the minimum denominator to use, use global ivy._MIN_DENOMINATOR by default.

        Returns
        -------
        ret
            a numpy array containing the elements of numerator divided by
            the corresponding element of denominator

        Examples
        --------
        With :class:`ivy.Array` instance method:

        >>> x = ivy.asarray([4., 5., 6.])
        >>> y = x.stable_divide(2)
        >>> print(y)
        ivy.array([2., 2.5, 3.])

        >>> x = ivy.asarray([4, 5, 6])
        >>> y = x.stable_divide(4, min_denominator=1)
        >>> print(y)
        ivy.array([0.8, 1. , 1.2])

        >>> x = ivy.asarray([[4., 5., 6.], [7., 8., 9.]])
        >>> y = ivy.asarray([[1., 2., 3.], [2., 3., 4.]])
        >>> z = x.stable_divide(y)
        >>> print(z)
        ivy.array([[4.  , 2.5 , 2.  ],
                [3.5 , 2.67, 2.25]])

        """
        return ivy.stable_divide(self, denominator, min_denominator=min_denominator)

    def clip_vector_norm(
        self: ivy.Array,
        max_norm: float,
        /,
        *,
        p: float = 2.0,
        out: Optional[ivy.Array] = None,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.clip_vector_norm. This method simply
        wraps the function, and so the docstring for ivy.clip_vector_norm also applies
        to this method with minimal changes.

        Parameters
        ----------
        self
            input array
        max_norm
            float, the maximum value of the array norm.
        p
            optional float, the p-value for computing the p-norm. Default is 2.
        out
            optional output array, for writing the result to. It must have a shape
            that the inputs broadcast to.

        Returns
        -------
        ret
            An array with the vector norm downscaled to the max norm if needed.

        Examples
        --------
        With :class:`ivy.Array` instance method:

        >>> x = ivy.array([0., 1., 2.])
        >>> y = x.clip_vector_norm(2.0)
        >>> print(y)
        ivy.array([0., 0.894, 1.79])

        """
        return ivy.clip_vector_norm(self, max_norm, p=p, out=out)

    def array_equal(self: ivy.Array, x: Union[ivy.Array, ivy.NativeArray], /) -> bool:
        """
        ivy.Array instance method variant of ivy.array_equal. This method simply wraps
        the function, and so the docstring for ivy.array_equal also applies to this
        method with minimal changes.

        Parameters
        ----------
        self
            input array
        x
            input array to compare to ``self``

        Returns
        -------
        ret
            Boolean, whether or not the input arrays are equal

        Examples
        --------
        >>> x = ivy.array([-1,0])
        >>> y = ivy.array([1,0])
        >>> z = x.array_equal(y)
        >>> print(z)
        False

        >>> a = ivy.array([1, 2])
        >>> b = ivy.array([1, 2])
        >>> c = a.array_equal(b)
        >>> print(c)
        True

        """
        return ivy.array_equal(self, x)

    def assert_supports_inplace(self: ivy.Array) -> bool:
        """
        ivy.Array instance method variant of ivy.assert_supports_inplace. This method
        simply wraps the function, and so the docstring for ivy.assert_supports_inplace
        also applies to this method with minimal changes.

        Parameters
        ----------
        self
            input array

        Returns
        -------
        ret
            True if support, raises exception otherwise

        """
        return ivy.assert_supports_inplace(self)

    def to_scalar(self: ivy.Array) -> Number:
        """
        ivy.Array instance method variant of ivy.to_scalar. This method simply wraps
        the function, and so the docstring for ivy.to_scalar also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array.

        Returns
        -------
        ret
            a scalar copying the element of the array ``x``.

        Examples
        --------
        With :class:`ivy.Array` instance method:

        >>> x = ivy.array([3])
        >>> y = x.to_scalar()
        >>> print(y)
        3

        """
        return ivy.to_scalar(self)

    def fourier_encode(
        self: ivy.Array,
        max_freq: Union[float, ivy.Array, ivy.NativeArray],
        /,
        *,
        num_bands: int = 4,
        linear: bool = False,
        concat: bool = True,
        flatten: bool = False,
    ) -> Union[ivy.Array, ivy.NativeArray, Tuple]:
        """
        ivy.Array instance method variant of ivy.fourier_encode. This method simply
        wraps the function, and so the docstring for ivy.fourier_encode also applies to
        this method with minimal changes.

        Parameters
        ----------
        self
            input array to encode
        max_freq
            The maximum frequency of the encoding.
        num_bands
            The number of frequency bands for the encoding. Default is 4.
        linear
            Whether to space the frequency bands linearly as opposed to geometrically.
            Default is ``False``.
        concat
            Whether to concatenate the position, sin and cos values, or return
            seperately. Default is ``True``.
        flatten
            Whether to flatten the position dimension into the batch dimension.
            Default is ``False``.

        Returns
        -------
        ret
            New array with the final dimension expanded, and the encodings stored in
            this channel.

        Examples
        --------
        >>> x = ivy.array([1, 2, 3])
        >>> y = 1.5
        >>> z = x.fourier_encode(y)
        >>> print(z)
        ivy.array([[ 1.0000000e+00, 1.2246468e-16, 0.0000000e+00, 0.0000000e+00,
                     0.0000000e+00, -1.0000000e+00, 1.0000000e+00, 1.0000000e+00,
                     1.0000000e+00],
                   [ 2.0000000e+00, -2.4492936e-16, 0.0000000e+00, 0.0000000e+00,
                     0.0000000e+00, 1.0000000e+00, 1.0000000e+00, 1.0000000e+00,
                     1.0000000e+00],
                   [ 3.0000000e+00, 3.6739404e-16, 0.0000000e+00, 0.0000000e+00,
                     0.0000000e+00, -1.0000000e+00, 1.0000000e+00, 1.0000000e+00,
                     1.0000000e+00]])

        >>> x = ivy.array([3, 10])
        >>> y = 2.5
        >>> z = x.fourier_encode(y, num_bands=3)
        >>> print(z)
        ivy.array([[ 3.0000000e+00,  3.6739404e-16,  3.6739404e-16,  3.6739404e-16,
                    -1.0000000e+00, -1.0000000e+00, -1.0000000e+00],
                   [ 1.0000000e+01, -1.2246468e-15, -1.2246468e-15, -1.2246468e-15,
                     1.0000000e+00,  1.0000000e+00,  1.0000000e+00]])
        """
        return ivy.fourier_encode(
            self,
            max_freq,
            num_bands=num_bands,
            linear=linear,
            concat=concat,
            flatten=flatten,
        )

    def value_is_nan(self: ivy.Array, /, *, include_infs: bool = True) -> bool:
        """
        ivy.Array instance method variant of ivy.value_is_nan. This method simply wraps
        the function, and so the docstring for ivy.value_is_nan also applies to this
        method with minimal changes.

        Parameters
        ----------
        self
            input array
        include_infs
            Whether to include infs and -infs in the check. Default is ``True``.

        Returns
        -------
        ret
            Boolean as to whether the input value is a nan or not.

        Examples
        --------
        With one :class:`ivy.Array` instance method:

        >>> x = ivy.array([92])
        >>> y = x.value_is_nan()
        >>> print(y)
        False

        >>> x = ivy.array([float('inf')])
        >>> y = x.value_is_nan()
        >>> print(y)
        True

        >>> x = ivy.array([float('nan')])
        >>> y = x.value_is_nan()
        >>> print(y)
        True

        >>> x = ivy.array([float('inf')])
        >>> y = x.value_is_nan(include_infs=False)
        >>> print(y)
        False
        """
        return ivy.value_is_nan(self, include_infs=include_infs)

    def exists(self: ivy.Array) -> bool:
        """
        ivy.Array instance method variant of ivy.exists. This method simply wraps
        the function, and so the docstring for ivy.exists also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array.

        Returns
        -------
        ret
            True if x is not None, else False.

        Examples
        --------
        >>> x = ivy.array([1, 2, 3, 1.2])
        >>> y = x.exists()
        >>> print(y)
        True

        >>> x = ivy.array(None)
        >>> y = x.exists()
        >>> print(y)
        True
        """
        return ivy.exists(self)

    def default(
        self: ivy.Array,
        /,
        default_val: Any,
        *,
        catch_exceptions: bool = False,
        rev: bool = False,
        with_callable: bool = False,
    ) -> Any:
        """
        ivy.Array instance method variant of ivy.default. This method simply wraps the
        function, and so the docstring for ivy.default also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array
        default_val
            The default value.
        catch_exceptions
            Whether to catch exceptions from callable x. Default is ``False``.
        rev
            Whether to reverse the input x and default_val. Default is ``False``.
        with_callable
            Whether either of the arguments might be callable functions.
            Default is ``False``.

        Returns
        -------
        ret
            x if x exists (is not None), else default.

        Examples
        --------
        >>> x = ivy.array([1, 2, 3, 1.2])
        >>> y = x.default(0)
        >>> print(y)
        ivy.array([1. , 2. , 3. , 1.2])

        """
        return ivy.default(
            self,
            default_val,
            catch_exceptions=catch_exceptions,
            rev=rev,
            with_callable=with_callable,
        )

    def stable_pow(
        self: ivy.Array,
        exponent: Union[Number, ivy.Array, ivy.NativeArray],
        /,
        *,
        min_base: float = None,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.stable_pow. This method simply wraps
        the function, and so the docstring for ivy.stable_pow also applies to this
        method with minimal changes.

        Parameters
        ----------
        self
            input array, used as the base.
        exponent
            The exponent number.
        min_base
            The minimum base to use, use global ivy._MIN_BASE by default.

        Returns
        -------
        ret
            The new item following the numerically stable power.

        """
        return ivy.stable_pow(self, exponent, min_base=min_base)

    def inplace_update(
        self: ivy.Array,
        val: Union[ivy.Array, ivy.NativeArray],
        ensure_in_backend: bool = False,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.inplace_update. This method simply
        wraps the function, and so the docstring for ivy.inplace_update also applies to
        this method with minimal changes.

        Parameters
        ----------
        self
            input array to update
        val
            The array to update the variable with.
        ensure_in_backend
            Whether or not to ensure that the `ivy.NativeArray` is also inplace updated.
            In cases where it should be, backends which do not natively support inplace
            updates will raise an exception.

        Returns
        -------
        ret
            The array following the in-place update.

        """
        return ivy.inplace_update(self, val, ensure_in_backend=ensure_in_backend)

    def inplace_increment(
        self: ivy.Array, val: Union[ivy.Array, ivy.NativeArray]
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.inplace_increment. This
        method wraps the function, and so the docstring for
        ivy.inplace_increment also applies to this method with minimal changes.

        Parameters
        ----------
        self
            The input array to be incremented by the defined value.
        val
            The value of increment.

        Returns
        -------
        ret
            The array following an in-place increment.

        Examples
        --------
        With :class:`ivy.Array` instance methods:

        >>> x = ivy.array([5.7, 4.3, 2.5, 1.9])
        >>> y = x.inplace_increment(1)
        >>> print(y)
        ivy.array([6.7, 5.3, 3.5, 2.9])

        >>> x = ivy.asarray([4., 5., 6.])
        >>> y = x.inplace_increment(2.5)
        >>> print(y)
        ivy.array([6.5, 7.5, 8.5])

        """
        return ivy.inplace_increment(self, val)

    def clip_matrix_norm(
        self: ivy.Array,
        max_norm: float,
        /,
        *,
        p: float = 2.0,
        out: Optional[ivy.Array] = None,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.clip_matrix_norm. This method simply
        wraps the function, and so the docstring for ivy.clip_matrix_norm also applies
        to this method with minimal changes.

        Parameters
        ----------
        self
            input array
        max_norm
            The maximum value of the array norm.
        p
            The p-value for computing the p-norm. Default is 2.
        out
            optional output array, for writing the result to. It must have a shape that
            the inputs broadcast to.

        Returns
        -------
        ret
            An array with the matrix norm downscaled to the max norm if needed.

        Examples
        --------
        With :class:`ivy.Array` instance method:

        >>> x = ivy.array([[0., 1., 2.]])
        >>> y = x.clip_matrix_norm(2.0)
        >>> print(y)
        ivy.array([[0.   , 0.894, 1.79 ]])

        """
        return ivy.clip_matrix_norm(self, max_norm, p=p, out=out)

    def scatter_flat(
        self: ivy.Array,
        updates: Union[ivy.Array, ivy.NativeArray],
        /,
        *,
        size: Optional[int] = None,
        reduction: str = "sum",
        out: Optional[ivy.Array] = None,
    ) -> ivy.Array:
        """
        ivy.Array instance method variant of ivy.scatter_flat. This method simply wraps
        the function, and so the docstring for ivy.scatter_flat also applies to this
        method with minimal changes.

        Parameters
        ----------
        self
            input array containing the indices where the new values will occupy
        updates
            Values for the new array to hold.
        size
            The size of the result.
        reduction
            The reduction method for the scatter, one of 'sum', 'min', 'max' or
            'replace'
        out
            optional output array, for writing the result to. It must have a shape that
            the inputs broadcast to.

        Returns
        -------
        ret
            New array of given shape, with the values scattered at the indices.
        """
        return ivy.scatter_flat(self, updates, size=size, reduction=reduction, out=out)

    def get_num_dims(self: ivy.Array, /, *, as_array: bool = False) -> int:
        """
        ivy.Array instance method variant of ivy.shape. This method simply wraps the
        function, and so the docstring for ivy.shape also applies to this method
        with minimal changes.

        Parameters
        ----------
        self
            input array to infer the number of dimensions  for
        as_array
            Whether to return the shape as a array, default False.

        Returns
        -------
        ret
            Shape of the array

        Examples
        --------
        >>> x = ivy.array([[0.,1.,1.],[1.,0.,0.],[8.,2.,3.]])
        >>> b = x.get_num_dims()
        >>> print(b)
        2

        >>> x = ivy.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0]],\
                            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],\
                            [[0, 0, 0], [0, 0, 0], [0, 0, 0]]])
        >>> b = x.get_num_dims(as_array=False)
        >>> print(b)
        3
        
        >>> b = x.get_num_dims(as_array=True)
        >>> print(b)
        ivy.array(3)
        """
        return ivy.get_num_dims(self, as_array=as_array)
