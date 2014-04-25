#!/usr/bin/env python

from collections import Iterator, Mapping, Sequence

class ColumnIterator(Iterator):
    """
    Iterator over column proxies.
    """
    def __init__(self, table):
        self._table = table
        self._i = 0

    def next(self):
        try:
            v = self._table._column_names[self._i]
        except IndexError:
            raise StopIteration

        column_type = self._table._column_types[self._i]

        self._i += 1
        
        return column_type(self._table, v)

class ColumnMapping(Mapping):
    """
    Proxy access to columns by name.
    """
    def __init__(self, table):
        self._table = table

    def __getitem__(self, k):
        if k not in self._table._column_names:
            raise KeyError

        i = self._table._column_names.index(k)
        column_type = self._table._column_types[i]

        return column_type(self._table, k)

    def __iter__(self):
        return ColumnIterator(self._table)

    def __len__(self):
        return len(self._table._column_names)

class Column(Sequence):
    """
    Proxy access to column data.
    """
    def __init__(self, table, k):
        self._table = table
        self._k = k

    def _data(self):
        # TODO: memoize?
        i = self._table._column_names.index(self._k)

        return [r[i] for r in self._table._data]

    def _data_without_nulls(self):
        # TODO: memoize?
        return [d for d in self._data() if d is not None]

    def __getitem__(self, j):
        return self._data()[j]

    def __len__(self):
        return len(self._data()) 

    def __eq__(self, other):
        return list(self._data()) == other

class TextColumn(Column):
    pass

class NumberColumn(Column):
    def sum(self):
        return sum(self._data_without_nulls())

class IntColumn(NumberColumn):
    pass

class FloatColumn(NumberColumn):
    pass