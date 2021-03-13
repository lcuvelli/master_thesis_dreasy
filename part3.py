import heat_transfer_coefficient as libh

from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from math import exp, pi, sin
import timeit

DELTA = 0.2
st1 = timeit.default_timer()


def direct_diffuse_solar_radiation(Sm: float, t_set: float, t_rise: float, t: float) -> float:
    S = pi/2 * Sm * sin(pi * (t - t_rise)/(t_set-t_rise))
    return S

def equations(vars, *data):
    Tair, t = data
    #print(Tair)
    R = 1.4  # m (aspect ratio)
    h = 2  # W/m2/K (heat transfert coefficient)
    k = 0.85  # reduction factor
    Sm = 463  # W/m2
    Tamb = 30 + 273  # °K (mean diurnal temperature)
    t_rise = 7  # h
    t_set = 19  # h
    RHamb = 70  # %
    Iatm = 377  # W/m2
    e = 6 / 1000  # mm (epaisseur)
    Wd = 1.4  # m
    ep = 0.001  # m
    lp = 0.2  # W /m*K (plastic thermal conductivity)
    #z = 0
    dz = DELTA    # m
    Q = 0.03  # kg of humid air / s
    Ca = 1009 # Heat capacity, J/kg/K
    To, Ti, Tfl, P, Tair_next = vars # T in K, P is in W/m2


    eq1 = Iatm * R + direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) * (1 - k) - libh.infrared_energy_flux(To) - libh.conductive_heat_flux(lp, ep, To, Ti) * R - h * (To - Tamb) * R
    eq2 = libh.infrared_energy_flux(Tfl) - libh.infrared_energy_flux(Ti) + libh.conductive_heat_flux(lp, ep, To, Ti) * R - h * (Ti - Tair) * R
    eq3 = P - h * (Tfl - Tair) - h * (Ti - Tair) * R
    eq4 = direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) * k - (libh.infrared_energy_flux(Tfl) - libh.infrared_energy_flux(Ti)) - h * (Tfl - Tair)
    eq5 = Tair_next - Tair - P * Wd / (Q * Ca) * dz

    return [eq1, eq2, eq3, eq4, eq5]


def temperature_one_time(Tamb, t, LH):
    z = 0
    data = (Tamb, t)
    #s0 = [0, 0, 0, 320, 320]
    # To, Ti, Tfl, P, Tair_next = vars
    s0 = [310, 320, 350, 320, 320]
    x = fsolve(equations, s0, args=data)
    while z < LH:
        z = round(z + DELTA, 2)
        data = (x[4], t)  # Tair = Tair_next de l'itération précédente
        x = fsolve(equations, s0, args=data)
        y = list(x)
        for i in range(5):
            if (i != 3):
                y[i] = x[i] - 273
                # t = t + 0.5
        print("En z = ", z, " et t = ", t, " : ", y, "\n")
    #Tair_LH = y[4]
    #print(Tair_LH)
    return y

def main():


    LH = 5 # m; length heating part.

    s0 = [0.0, 0.0, 0.0, 0.0, 0.0]
    t0 = 9.5 #heures, début du séchage
    td = 6.5 #heures, durée du séchage
    tf = td + t0  #heures, fin du séchage
    print("\n Début de programme ")
    Tamb = 30 + 273 # °K (mean diurnal temperature)
    z = 0
    #t = 10  # h
    t = t0
    Tair_LH = []
    P_LH = []
    all_t = []


    # To, Ti, Tfl, P, Tair_next = vars
    while t < tf:
        x = temperature_one_time(Tamb, t, LH)
        P_t = x[3]
        Tair_LH_t = x[4]
        Tair_LH.append(Tair_LH_t)
        P_LH.append(P_t)
        all_t.append(t)
        t += 0.5
    print(len(all_t))
    print(len(Tair_LH))

    plt.figure(1)
    plt.xlabel('Time of the day (h)')
    plt.ylabel('Temperatures (°C)')
    plt.title('Temperature inside the dryer during the day')
    plt.plot(all_t, Tair_LH, 'go')
    #plt.show()

    plt.figure(2)
    plt.xlabel('Time of the day (h)')
    plt.ylabel('Energy flux (W/m2)')
    plt.title('Energy flux transferred to the air inside the dryer')
    plt.plot(all_t, P_LH, 'ro')
    plt.show()


    #a = isclose(equations(x, x[4], t), [0.0, 0.0, 0.0, 0.0, 0.0])
    #print(a)

    # Graphe de la température de l'air à la fin de la zone de chauffe au long de la journée


    #print(x)

if __name__ == '__main__':
    main()


