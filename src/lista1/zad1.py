from random import randrange
import sys


def roll_dice():
    return randrange(1, 6, 1)


def roll_for_player(n):
    res = 0
    for i in range(n):
        res += roll_dice()
    return res


def game(n):
    i = 0
    res_a = 0
    res_b = 0
    draw = 0
    while i < n or (i >= n and res_a == res_b):
        a = roll_for_player(2)
        b = roll_for_player(2)

        print('Wynik A:{} , Wynik B:{} '.format(a, b))

        res = a - b
        if res == 0:
            print('Remis')
            draw += 1
        elif res > 0:
            print('Gracz A wygrywa')
            res_a += 1
        else:
            print('Gracz B wygrywa')
            res_b += 1
        i += 1
        print('Wygrane gracza A: {}. Wygrane gracza B: {}. Remisy: {}'.format(res_a, res_b, draw))


x = int(sys.argv[1])
game(x)
