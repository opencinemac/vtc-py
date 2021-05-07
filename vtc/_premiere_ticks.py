from typing import Union, Tuple


class PremiereTicks(int):
    """
    PremiereTicks signals than an int value represents an Adobe Premier Pro ticks value
    and can be used to wrap ints for parsing tc and doing mathematical operations.
    """

    # We need to override all of the mathematical magic methods or math operations,
    # even on two PremiereTicks instances, will return a generic int.
    def __add__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__add__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __radd__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__radd__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __sub__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__sub__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __rsub__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__rsub__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __mul__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__mul__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __rmul__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__rmul__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __floordiv__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__floordiv__(other)
        return self.__class__(res)

    def __rfloordiv__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__rfloordiv__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __mod__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__mod__(other)
        return self.__class__(res)

    def __rmod__(self, other: Union["PremiereTicks", int]) -> "PremiereTicks":
        res = super().__rmod__(other)
        if isinstance(res, int):
            res = self.__class__(res)
        return res

    def __divmod__(
        self,
        other: Union["PremiereTicks", int],
    ) -> Tuple["PremiereTicks", "PremiereTicks"]:
        res = super().__divmod__(other)
        return self.__class__(res[0]), self.__class__(res[1])

    def __rdivmod__(
        self,
        other: Union["PremiereTicks", int],
    ) -> Tuple["PremiereTicks", "PremiereTicks"]:
        res = super().__rdivmod__(other)
        return self.__class__(res[0]), self.__class__(res[1])

    def __floor__(self) -> "PremiereTicks":
        res = super().__floor__()
        return self.__class__(res)

    def __ceil__(self) -> "PremiereTicks":
        res = super().__ceil__()
        return self.__class__(res)

    def __neg__(self) -> "PremiereTicks":
        res = super().__neg__()
        return self.__class__(res)

    def __abs__(self) -> "PremiereTicks":
        res = super().__abs__()
        return self.__class__(res)
