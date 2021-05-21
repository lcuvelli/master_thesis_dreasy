from math import exp

import numpy as np

from model.tools import darboux_sum

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
    X0 = 6
    Xf = 0.3
    td = 8
    t0 = 8
    Td = 72
    T = [52.433942822073334, 58.89285801525381, 64.60631177193056, 69.51086835636687, 73.56538722602579, 76.74227853597085, 79.02307199295967, 80.39593762017427, 80.85426799360641, 80.39593762017427, 79.02307199295967, 76.74227853597085, 73.56538722602579, 69.51086835636687, 64.60631177193056, 58.892858015253864, 52.433942822073334]

    P =  [96.26335423722986, 117.20765316697187, 134.93223888637624, 149.5998727215352, 161.37167260071897, 170.38463077113204, 176.74607043311025, 180.53247440243888, 181.78954460467682, 180.53247440243888, 176.74607043311025, 170.38463077113207, 161.3716726007191, 149.59987272153523, 134.93223888637627, 117.20765316697172, 96.26335423722986]


    Wd = 1.95 #m
    M0 = 25 #kg

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

    evaporation_rate_J = []
    for i in range(len(T)):
        evaporation_rate_J.append(J2(intervals_t[i],T[i]+273, alpha, Td+273, t0, td))


    mean_evaporation_rate = darboux_sum(evaporation_rate_J, DELTA_T)
    mean_P = darboux_sum(P, DELTA_T)

    MS = (1+X0)/Lw * mean_P/mean_evaporation_rate
    print("Mass of product per unit area:", round(MS,2), "kg/m2")
    print("Area needed:", round(M0/MS,2), "m2")
    LD = M0 / (MS * Wd)
    print("Length of the drying section:", round(LD,2), "m")



    solution = {"LD": LD}

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


