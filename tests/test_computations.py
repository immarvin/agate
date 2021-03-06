#!/usr/bin/env Python

try:
    from cdecimal import Decimal
except ImportError: #pragma: no cover
    from decimal import Decimal

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from agate import Table
from agate.column_types import NumberType, TextType
from agate.computations import Change, PercentChange, Rank, ZScores, PercentileRank
from agate.exceptions import UnsupportedComputationError

class TestTableComputation(unittest.TestCase):
    def setUp(self):
        self.rows = (
            ('a', 2, 3, 4),
            (None, 3, 5, None),
            ('a', 2, 4, None),
            ('b', 3, 4, None)
        )

        self.number_type = NumberType()
        self.text_type = TextType()

        self.columns = (
            ('one', self.text_type),
            ('two', self.number_type),
            ('three', self.number_type),
            ('four', self.number_type),
        )

        self.table = Table(self.rows, self.columns)

    def test_change(self):
        new_table = self.table.compute([
            ('test', Change('two', 'three'))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        to_one_place = lambda d: d.quantize(Decimal('0.1'))

        self.assertSequenceEqual(new_table.rows[0], ('a', Decimal('2'), Decimal('3'), Decimal('4'), Decimal('1')))
        self.assertEqual(new_table.columns['test'][0], Decimal('1'))
        self.assertEqual(new_table.columns['test'][1], Decimal('2'))
        self.assertEqual(new_table.columns['test'][2], Decimal('2'))
        self.assertEqual(new_table.columns['test'][3], Decimal('1'))

    def test_percent_change(self):
        new_table = self.table.compute([
            ('test', PercentChange('two', 'three'))
        ])

        self.assertIsNot(new_table, self.table)
        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        to_one_place = lambda d: d.quantize(Decimal('0.1'))

        self.assertSequenceEqual(new_table.rows[0], ('a', Decimal('2'), Decimal('3'), Decimal('4'), Decimal('50.0')))
        self.assertEqual(to_one_place(new_table.columns['test'][0]), Decimal('50.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][1]), Decimal('66.7'))
        self.assertEqual(to_one_place(new_table.columns['test'][2]), Decimal('100.0'))
        self.assertEqual(to_one_place(new_table.columns['test'][3]), Decimal('33.3'))

    def test_percent_change_invalid_columns(self):
        with self.assertRaises(UnsupportedComputationError):
            new_table = self.table.compute([
                ('test', PercentChange('one', 'three'))
            ])

    def test_z_scores(self):
        new_table = self.table.compute([
            ('z-scores', ZScores('two'))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, -1))
        self.assertSequenceEqual(new_table.rows[1], (None, 3, 5, None, 1))
        self.assertSequenceEqual(new_table.rows[2], ('a', 2, 4, None, -1))
        self.assertSequenceEqual(new_table.rows[3], ('b', 3, 4, None, 1))

        self.assertSequenceEqual(new_table.columns['z-scores'],(-1,1,-1,1))

    def test_zscores_invalid_column(self):
        with self.assertRaises(UnsupportedComputationError):
            new_table = self.table.compute([
                ('test', ZScores('one'))
            ])

    def test_rank_number(self):
        new_table = self.table.compute([
            ('rank', Rank('two'))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 1))
        self.assertSequenceEqual(new_table.rows[1], (None, 3, 5, None, 3))
        self.assertSequenceEqual(new_table.rows[2], ('a', 2, 4, None, 1))
        self.assertSequenceEqual(new_table.rows[3], ('b', 3, 4, None, 3))

        self.assertSequenceEqual(new_table.columns['rank'], (1, 3, 1, 3))

    def test_rank_text(self):
        new_table = self.table.compute([
            ('rank', Rank('one'))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 1))
        self.assertSequenceEqual(new_table.rows[1], (None, 3, 5, None, 4))
        self.assertSequenceEqual(new_table.rows[2], ('a', 2, 4, None, 1))
        self.assertSequenceEqual(new_table.rows[3], ('b', 3, 4, None, 3))

        self.assertSequenceEqual(new_table.columns['rank'], (1, 4, 1, 3))

    def test_rank_column_name(self):
        new_table = self.table.compute([
            ('rank', Rank('two'))
        ])

        self.assertEqual(len(new_table.rows), 4)
        self.assertEqual(len(new_table.columns), 5)

        self.assertSequenceEqual(new_table.rows[0], ('a', 2, 3, 4, 1))
        self.assertSequenceEqual(new_table.rows[1], (None, 3, 5, None, 3))
        self.assertSequenceEqual(new_table.rows[2], ('a', 2, 4, None, 1))
        self.assertSequenceEqual(new_table.rows[3], ('b', 3, 4, None, 3))

        self.assertSequenceEqual(new_table.columns['rank'], (1, 3, 1, 3))

    def test_percentile_rank(self):
        rows = [(n,) for n in range(1, 1001)]

        table = Table(rows, (('ints', self.number_type),))
        new_table = table.compute([
            ('percentiles', PercentileRank('ints'))
        ])

        self.assertEqual(len(new_table.rows), 1000)
        self.assertEqual(len(new_table.columns), 2)

        self.assertSequenceEqual(new_table.rows[0], (1, 0))
        self.assertSequenceEqual(new_table.rows[50], (51, 5))
        self.assertSequenceEqual(new_table.rows[499], (500, 49))
        self.assertSequenceEqual(new_table.rows[500], (501, 50))
        self.assertSequenceEqual(new_table.rows[998], (999, 99))
        self.assertSequenceEqual(new_table.rows[999], (1000, 100))
