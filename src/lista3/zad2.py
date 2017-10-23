from math import ceil


def is_perfect(x):
    suma = 0
    for i in range(1, ceil(x / 2) + 1):
        if x % i == 0:
            suma += i
    return suma == x


def doskonale_funkcyjna(n):
    return list(filter(is_perfect, range(n + 1)))


def doskonale_skladana(n):
    return [x for x in range(n + 1) if is_perfect(x)]


print(doskonale_funkcyjna(10000))
print(doskonale_skladana(10000))
