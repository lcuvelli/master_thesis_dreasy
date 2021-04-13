import heat_transfer_coefficient as libh

from scipy.optimize import fsolve
from numpy import isclose, polyfit
import matplotlib.pyplot as plt
import tikzplotlib
import numpy as np
from tools import darboux_sum
import matplotlib as mpl
import pylab as pl



from math import exp
import timeit

Lw = 2358 * 1000 # J/kg - Mass latent heat of vaporization #TODO: change in function of T
DELTA_T = 0.5




def evaporation_coefficient(X0, Xf, td):
    """Coefficient in the function of the energy flux consumed by the evaporation"""

    alpha = - 4 * (X0 - Xf) / (td * 3600 * (exp(-4) - 1))

    return alpha

def J(t, alpha, t0, td):
    """Kg of water per kg dry product per second as a function of time

    Args:
        t: time of the day, in range [t0, t0 + td] in seconds
        alpha: coefficient of the exponentiel """

    return alpha * exp(-4 * (t - t0)/td)

def J2(t, T, alpha, Td, t0, td):
    """Kg of water per kg dry product per second as a function of time

        Args:
            t: time of the day, in range [t0, t0 + td] in seconds
            alpha: coefficient of the exponentiel """
    Ea = 30 * 1000 # J/mol
    Rg = 8.314     # J/mol*K

    return alpha * exp(-4 * (t - t0) / td) * exp(-Ea/Rg * (1/T - 1/Td))


def mass_per_surface_unit(M0, LD, Wd):
    Ms = M0/(LD * Wd)
    return Ms


def main():
    X0 = 10
    Xf = 0.9
    td = 6.5
    t0 = 9.75
    tf = td + t0
    Td = 60
    P = [53.755463930536635, 61.07720999613991, 67.01758728494032, 71.7111138804958, 75.26067224112127, 77.74304067972115, 79.21153410558242, 79.69757147809871, 79.21153410558242, 77.74304067972115, 75.2606722411213, 71.71111388049594, 67.01758728494003, 61.07720999613991]
    T = [57.05070711384582, 61.89683694590565, 66.07278090156086, 69.53688856317234, 72.25906951723152, 74.21781731805669,
     75.39864113287763, 75.79316322713913, 75.39864113287763, 74.21781731805669, 72.25906951723152, 69.53688856317234,
     66.07278090156092, 61.89683694590565]
    Wd = 1.5 #m
    M0 = 10 #kg

    compute_drying_length(X0, Xf, M0, td, t0, Td, Wd, P, T)

def compute_drying_length(X0, Xf, M0, td, t0, Td, Wd, P:list, T:list):
    """

    :param X0:
    :param Xf:
    :param M0:
    :param td:
    :param t0:
    :param Td:
    :param P:
    :param T: list of temperatures (in °C) at z = LH
    :return:
    """

    tf = t0 + td
    intervals_t = np.arange(t0, t0 + td + DELTA_T, DELTA_T).tolist()
    alpha = evaporation_coefficient(X0, Xf, td)
    print(alpha)

    y = []
    for i in range(len(T)):
        y.append(J2(intervals_t[i],T[i]+273, alpha, Td+273, t0, td))
        #y.append(J(intervals_t[i], alpha))

    t = t0
    M = []
    i = 0
    while t <= tf:
        M.append(M0 / (1+X0) * Lw * y[i]/P[i])
        M[i] = M[i]/Wd
        t+= DELTA_T
        i+=1
    print(len(M), len(y))
    print(M0 /(1+X0))
    mean = darboux_sum(M,DELTA_T)/td
    print(mean)
    print(mean/Wd)




    plt.figure(1)
    plt.title("Surface au sol de la zone de séchage (m2)")
    plt.plot(intervals_t, M, 'yo')
    plt.xlabel('Time of the day (h)')
    plt.ylabel("Omega (m2)")
    plt.text(13,20,"Mean: 8.4 m2")


    """Drawing"""
    plt.figure(2)
    plt.title("Energy flux transferred to the air inside the dryer, W/m2 (LH = 5m)")
    plt.plot(intervals_t,P)
    plt.xlabel('Time of the day (h)')
    plt.ylabel("P (W/m2)")

    plt.figure(3)
    plt.title("J(t) with alpha = 0.0012 ")
    plt.plot(intervals_t, y, 'og')
    plt.xlabel('Time of the day (h)')
    plt.ylabel("J (kg of water/kg dry product per second)")

    #for i, txt in enumerate(T):
        #txt = str(round(txt,1))+"°C"
        #plt.annotate(txt, (intervals_t[i]+0.1, y[i]), fontsize=9)

    plt.show()

    # line, = plt.plot(intervals_t, y, label='for evaporation')
    # plt.legend()
    #
    # plt.ylabel('Energy flux (W/m2)')
    # #line.set_label('Label via method')
    # #tikzplotlib.save("mytikz.tex")
    # plt.show()


if __name__ == '__main__':
    main()


