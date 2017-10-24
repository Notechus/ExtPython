from math import ceil
from time import time


def doskonale_funkcyjna(n):
    return list(filter(lambda x: sum(i for i in range(1, ceil(x / 2) + 1) if x % i == 0) == x, range(6, n + 1)))


def doskonale_skladana(n):
    return [x for x in range(6, n + 1) if sum(i for i in range(1, ceil(x / 2) + 1) if x % i == 0) == x]


start1 = time()
print(doskonale_funkcyjna(10000))
end1 = time()
start2 = time()
print(doskonale_skladana(10000))
end2 = time()

print(end1 - start1)
print(end2 - start2)
