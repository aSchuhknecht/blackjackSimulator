import random
import config as cf
import strat as st
import matplotlib.pyplot as plt
import numpy as np
import math


def main():

    win = 2000
    initial = 2000
    rph = 100
    wh = []
    bet = 100

    n_sim = 1000000
    list1 = np.linspace(0, 1000, 1001)
    for i in range(0, n_sim):

        c = random.choice(list1)
        if c <= 504:
            win += bet
        else:
            win -= bet
        wh.append(win)

    x = np.linspace(0, len(wh), len(wh))
    baseline = np.full((len(wh),), initial)
    y = np.array(wh)
    m = np.polyfit(x, y, 1)
    best_fit = m[0] * x + m[1]

    total_win = wh[len(wh) - 1] - initial
    wpr = total_win / n_sim
    print(wpr)
    wph = wpr * rph
    print(wph)

    plt.plot(x, y, 'r--', x, baseline, 'k--', x, best_fit, 'b--')
    plt.show()


if __name__ == "__main__":
    main()
