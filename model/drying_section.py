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
    X0 = 7
    Xf = 0.1
    td = 6.5
    t0 = 9.75
    Td = 60
    P = [100.34373691424814, 114.3559869703552, 126.03400987585604, 135.36851465301027, 142.36130489254745,
     147.0181925255959, 149.34493444596555, 149.34493444596555, 147.0181925255959, 142.36130489254754,
     135.36851465301027, 126.03400987585604, 114.3559869703552, 100.34373691424793]
    T = [49.61305183372599, 52.822449116416635, 55.56785537435013, 57.80856028577267, 59.51415472970882, 60.662886998728254,
     61.24070377349716, 61.24070377349716, 60.662886998728254, 59.51415472970882, 57.80856028577267, 55.56785537435013,
     52.822449116416635, 49.61305183372605]
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


