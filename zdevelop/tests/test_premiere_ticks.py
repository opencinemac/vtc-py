import math
import unittest
import vtc


class TestPremiereTicks(unittest.TestCase):
    """
    TestPremiereTicks tests that using the magic methods of PremiereTicks class returns
    our new class and not a generic int.
    """

    A = vtc.PremiereTicks(1)
    B = vtc.PremiereTicks(5)

    def test_add(self) -> None:
        result = self.A + self.B
        self.assertEqual(6, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_add_int(self) -> None:
        result = self.A + 5
        self.assertEqual(6, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_radd(self) -> None:
        result = 1 + self.B
        self.assertEqual(6, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_sub(self) -> None:
        result = self.A - self.B
        self.assertEqual(-4, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_sub_int(self) -> None:
        result = self.A - 5
        self.assertEqual(-4, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_rsub(self) -> None:
        result = 1 - self.B
        self.assertEqual(-4, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_mul(self) -> None:
        result = self.A * self.B
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_mul_int(self) -> None:
        result = self.A * 5
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_rmul(self) -> None:
        result = 1 * self.B
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_floor_div(self) -> None:
        result = self.B // self.A
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_floor_div_int(self) -> None:
        result = self.B // 1
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_rfloor_div(self) -> None:
        result = 5 // self.A
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_mod(self) -> None:
        result = vtc.PremiereTicks(22) % vtc.PremiereTicks(5)
        self.assertEqual(2, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_mod_int(self) -> None:
        result = vtc.PremiereTicks(22) % 5
        self.assertEqual(2, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_rmod(self) -> None:
        result = 22 % vtc.PremiereTicks(5)
        self.assertEqual(2, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_divmod(self) -> None:
        result = divmod(vtc.PremiereTicks(22), vtc.PremiereTicks(5))
        self.assertEqual((4, 2), result, "result expected")
        self.assertIsInstance(result[0], vtc.PremiereTicks, "type correct")
        self.assertIsInstance(result[1], vtc.PremiereTicks, "type correct")

    def test_divmod_int(self) -> None:
        result = divmod(vtc.PremiereTicks(22), 5)
        self.assertEqual((4, 2), result, "result expected")
        self.assertIsInstance(result[0], vtc.PremiereTicks, "type correct")
        self.assertIsInstance(result[1], vtc.PremiereTicks, "type correct")

    def test_rdivmod(self) -> None:
        result = divmod(22, vtc.PremiereTicks(5))
        self.assertEqual((4, 2), result, "result expected")
        self.assertIsInstance(result[0], vtc.PremiereTicks, "type correct")
        self.assertIsInstance(result[1], vtc.PremiereTicks, "type correct")

    def test_floor(self) -> None:
        result = math.floor(self.B)
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_ceil(self) -> None:
        result = math.ceil(self.B)
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_abs(self) -> None:
        result = abs(vtc.PremiereTicks(-5))
        self.assertEqual(5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")

    def test_neg(self) -> None:
        result = -self.B
        self.assertEqual(-5, result, "result expected")
        self.assertIsInstance(result, vtc.PremiereTicks, "type correct")
