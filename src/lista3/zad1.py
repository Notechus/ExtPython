from math import sqrt, ceil


def is_prime(x):
    for i in range(2, ceil(sqrt(x))):
        if x % i == 0:
            return False
    return True


def pierwsze_funkcyjna(n):
    return list(filter(is_prime, range(n + 1)))


def pierwsze_skladana(n):
    return [x for x in range(n + 1) if is_prime(x)]


print(pierwsze_funkcyjna(20))
print(pierwsze_skladana(20))
