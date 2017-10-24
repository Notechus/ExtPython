from math import sqrt, ceil
from time import time


def pierwsze_funkcyjna(n):
    return list(filter(lambda x: all(not x % i == 0 for i in range(2, ceil(sqrt(x)))), range(2, n + 1)))


def pierwsze_skladana(n):
    return [x for x in range(2, n + 1) if all(x % i != 0 for i in range(2, ceil(sqrt(x))))]


start1 = time()
print(pierwsze_funkcyjna(2000))
end1 = time()
start2 = time()
print(pierwsze_skladana(2000))
end2 = time()

print(end1 - start1)
print(end2 - start2)
