import pytest
from django.test import TestCase

from src.certificates.utils import numeral_noun_declension


args = ('академический час', 'академических часа', 'академических часов')


@pytest.mark.parametrize(
    "n,expected",
    [
        ((74, ) + args, "академических часа"),
        ((71, ) + args, "академический час"),
        ((1, ) + args, "академический час"),
        ((2, ) + args, "академических часа"),
        ((5, ) + args, "академических часов"),
        ((11, ) + args, "академических часов"),
        ((21, ) + args, "академический час"),
     ]
)
def test_numeral_noun_declension(n, expected):
    assert numeral_noun_declension(*n) == expected
