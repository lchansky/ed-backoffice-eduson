def numeral_noun_declension(
    number,
    nominative_singular,
    genetive_singular,
    nominative_plural,
):
    """
    Возвращает склонение под нужное число объектов.
    Например:
    >>> numeral_noun_declension(22, 'собака', 'собаки', 'собак')
    >>> "собаки"
"""
    last_digit = number % 10
    if nominative_plural and (number in range(5, 20)):
        return nominative_plural
    elif nominative_singular and (1 in (number, last_digit)):
        return nominative_singular
    elif genetive_singular and ({number, last_digit} & {2, 3, 4}):
        return genetive_singular
    else:
        return nominative_plural
