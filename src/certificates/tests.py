import pytest
from django.test import TestCase

from src.certificates.utils import numeral_noun_declension


args = ('час', 'часа', 'часов')


@pytest.mark.parametrize(
    "n,expected",
    [
        ((74, ) + args, "часа"),
        ((71, ) + args, "час"),
        ((1, ) + args, "час"),
        ((2, ) + args, "часа"),
        ((5, ) + args, "часов"),
        ((11, ) + args, "часов"),
        ((21, ) + args, "час"),
     ]
)
def test_numeral_noun_declension(n, expected):
    assert numeral_noun_declension(*n) == expected
