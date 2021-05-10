from typing import Union, Tuple


class PremiereTicks(int):

    """
    PremiereTicks signals than an int value represents an Adobe Premier Pro ticks value
    and can be used to wrap ints for parsing tc and doing mathematical operations.
    """

    # We need to override all of the mathematical magic methods or math operations,
    # even on two PremiereTicks instances, will return a generic int.
    def __add__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__add__ applies the int operation then casts to the correct type."""
        res = super().__add__(other)
        return self.__class__(res)

    def __radd__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__radd__ applies the int operation then casts to the correct type."""
        res = super().__radd__(other)
        return self.__class__(res)

    def __sub__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__sub__ applies the int operation then casts to the correct type."""
        res = super().__sub__(other)
        return self.__class__(res)

    def __rsub__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__rsub__ applies the int operation then casts to the correct type."""
        res = super().__rsub__(other)
        return self.__class__(res)

    def __mul__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__mul__ applies the int operation then casts to the correct type."""
        res = super().__mul__(other)
        return self.__class__(res)

    def __rmul__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__rmul__ applies the int operation then casts to the correct type."""
        res = super().__rmul__(other)
        return self.__class__(res)

    def __floordiv__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__floordiv__ applies the int operation then casts to the correct type."""
        res = super().__floordiv__(other)
        return self.__class__(res)

    def __rfloordiv__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__rfloordiv__ applies the int operation then casts to the correct type."""
        res = super().__rfloordiv__(other)
        return self.__class__(res)

    def __mod__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__mod__ applies the int operation then casts to the correct type."""
        res = super().__mod__(other)
        return self.__class__(res)

    def __rmod__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        """__rmod__ applies the int operation then casts to the correct type."""
        res = super().__rmod__(other)
        return self.__class__(res)

    def __divmod__(
        self,
        other: Union["PremiereTicks", int],
    ) -> Tuple["PremiereTicks", "PremiereTicks"]:
        """__divmod__ applies the int operation then casts to the correct type."""
        res = super().__divmod__(other)
        return self.__class__(res[0]), self.__class__(res[1])

    def __rdivmod__(
        self,
        other: Union["PremiereTicks", int],
    ) -> Tuple["PremiereTicks", "PremiereTicks"]:
        """__rdivmod__ applies the int operation then casts to the correct type."""
        res = super().__rdivmod__(other)
        return self.__class__(res[0]), self.__class__(res[1])

    def __floor__(self) -> "PremiereTicks":
        """__floor__ applies the int operation then casts to the correct type."""
        res = super().__floor__()
        return self.__class__(res)

    def __ceil__(self) -> "PremiereTicks":
        """__ceil__ applies the int operation then casts to the correct type."""
        res = super().__ceil__()
        return self.__class__(res)

    def __neg__(self) -> "PremiereTicks":
        """__neg__ applies the int operation then casts to the correct type."""
        res = super().__neg__()
        return self.__class__(res)

    def __abs__(self) -> "PremiereTicks":
        """__abs__ applies the int operation then casts to the correct type."""
        res = super().__abs__()
        return self.__class__(res)
