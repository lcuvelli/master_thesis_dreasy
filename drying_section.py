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
    Ea = 10 * 1000 # J/mol #TODO: diminuer à 10,000 (données Nada)
    Rg = 8.314     # J/mol*K

    return alpha * exp(-4 * (t - t0) / td) * exp(-Ea/Rg * (1/T - 1/Td))


def mass_per_surface_unit(M0, LD, Wd):
    Ms = M0/(LD * Wd)
    return Ms


def main():
    X0 = 7
    Xf = 0.1
    td = 6.5
    t0 = 9.75
    Td = 60
    P = [103.41795242855638, 118.20109639903882, 130.5727354591062, 140.49568166041038, 147.94938753590725, 152.9228829562677, 155.41072879588936, 155.41072879588936, 152.9228829562677, 147.94938753590733, 140.49568166041038, 130.5727354591062, 118.20109639903882, 103.41795242855643]
    T = [49.04896603568676, 52.15320421477281, 54.80630083601244, 56.970206685130734, 58.616526550720494, 59.72496007067514, 60.28239569511095, 60.28239569511095, 59.72496007067514, 58.616526550720494, 56.970206685130734, 54.80630083601244, 52.15320421477281, 49.04896603568676]
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

    mean = round(darboux_sum(M,DELTA_T)/td,3)
    print("Moyenne pour la zone de séchage:", mean, "m^2")
    LD = round(mean/Wd,3)
    print("Longueur de la zone de séchage:", LD)
    solution = {"LD": LD, "omega_mean": mean}

    return solution



    #
    #
    #
    # f = plt.figure(1)
    # ax = f.add_subplot(111)
    #
    # plt.title("Surface au sol de la zone de séchage (m2)")
    # plt.plot(intervals_t, M, 'yo')
    # plt.xlabel('Time of the day (h)')
    # plt.ylabel("Omega (m2)")
    # plt.text(0.5, 0.5, "Mean: %1.3f m2" % mean, horizontalalignment='center',
    #          verticalalignment='center', transform=ax.transAxes)
    #
    # plt.text(0.5, 0.4, "LD: %1.3f m" % LD, horizontalalignment='center',
    #          verticalalignment='center', transform=ax.transAxes)
    #
    #
    # """Drawing"""
    # plt.figure(2)
    # plt.title("Energy flux transferred to the air inside the dryer, W/m2 (LH = 5m)")
    # plt.plot(intervals_t,P)
    # plt.xlabel('Time of the day (h)')
    # plt.ylabel("P (W/m2)")
    #
    # plt.figure(3)
    # plt.title("J(t) with alpha = %1.5f" % alpha)
    # plt.plot(intervals_t, y, 'og')
    # plt.xlabel('Time of the day (h)')
    # plt.ylabel("J (kg of water/kg dry product per second)")

    #for i, txt in enumerate(T):
        #txt = str(round(txt,1))+"°C"
        #plt.annotate(txt, (intervals_t[i]+0.1, y[i]), fontsize=9)

    #plt.show()

    # line, = plt.plot(intervals_t, y, label='for evaporation')
    # plt.legend()
    #
    # plt.ylabel('Energy flux (W/m2)')
    # #line.set_label('Label via method')
    # #tikzplotlib.save("mytikz.tex")
    # plt.show()


if __name__ == '__main__':
    main()


