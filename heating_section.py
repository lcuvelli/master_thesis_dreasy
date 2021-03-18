import heat_transfer_coefficient as libh

from scipy.optimize import fsolve
from numpy import isclose, polyfit
import matplotlib.pyplot as plt
import tikzplotlib

from math import exp, pi, sin
import timeit


# Constants
Ca = 1009 # Heat capacity air, J/kg/K

# Climatic data - Cambodia
Sm = 463  # W/m2
Tamb = 30 + 273  # °K (mean diurnal temperature)
t_rise = 7  # h
t_set = 19  # h

# Specifications - Drying 10kg of mangoes in Cambodia
DELTA = 0.5
R = 1.4   # m (aspect ratio)
Q = 0.03  # kg of humid air / s
Wd = 1.4  # m
k = 0.85  # reduction factor
M0 = 10   # kg


def direct_diffuse_solar_radiation(Sm: float, t_set: float, t_rise: float, t: float) -> float:
    S = pi/2 * Sm * sin(pi * (t - t_rise)/(t_set-t_rise))
    return S

# def equations(vars, *data):
#     Tair, t = data
#     #print(Tair)
#     R = 1.4  # m (aspect ratio)
#     h = 2  # W/m2/K (heat transfert coefficient)
#     k = 0.85  # reduction factor
#     Sm = 463  # W/m2
#     Tamb = 30 + 273  # °K (mean diurnal temperature)
#     t_rise = 7  # h
#     t_set = 19  # h
#     RHamb = 70  # %
#     Iatm = 377  # W/m2
#     e = 6 / 1000  # mm (epaisseur)
#     Wd = 1.4  # m
#     ep = 0.001  # m
#     lp = 0.2  # W /m*K (plastic thermal conductivity)
#     #z = 0
#     dz = DELTA    # m
#
#     To, Ti, Tfl, P, Tair_next = vars # T in K, P is in W/m2
#
#
#     eq1 = Iatm * R + direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) * (1 - k) - libh.infrared_energy_flux(To) - libh.conductive_heat_flux(lp, ep, To, Ti) * R - h * (To - Tamb) * R
#     eq2 = libh.infrared_energy_flux(Tfl) - libh.infrared_energy_flux(Ti) + libh.conductive_heat_flux(lp, ep, To, Ti) * R - h * (Ti - Tair) * R
#     eq3 = P - h * (Tfl - Tair) - h * (Ti - Tair) * R
#     eq4 = direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) * k - (libh.infrared_energy_flux(Tfl) - libh.infrared_energy_flux(Ti)) - h * (Tfl - Tair)
#     eq5 = Tair_next - Tair - P * Wd / (Q * Ca) * dz
#
#     return [eq1, eq2, eq3, eq4, eq5]


def temperature_time_t(Tamb, t, LH):
    z = 0
    data = (Tamb, t)
    Tair = Tamb
    # Tp, Tfl, P = vars
    s0 = [310, 320, 350]
    x = fsolve(balance_equations_heating, s0, args=data)
    while z < LH:
        z = round(z + DELTA, 2)
        P = x[2]
        #print("Tair avant: ", Tair-273, " °C")
        Tair = Tair_z_plus_dz(P,Tair)
        #print("Tair next: ", Tair-273)
        data = (Tair, t)  # Tair = Tair_next de l'itération précédente
        s0 = x            # old solution is the new initial solution
        x = fsolve(balance_equations_heating, s0, args=data)
        y = list(x)
        y[0] -= 273
        y[1] -= 273
        print("En z = ", z, " et t = ", t, " : ", y, "\n")
        #a = isclose(balance_equations_Tp(x, Tair, t), [0.0, 0.0, 0.0])  # check if numerical solution makes sense
        #print(a)
    y.append(Tair-273)
    print(t)
    return y

# Hypothese 13-03-21 : Ti = To = Tp
# Résoudre 3 équations à 3 inconnues

def balance_equations_heating(vars, *data): # Need to give Tair(z) and time t
    Tair, t = data

    h = 2  # W/m2/K (heat transfert coefficient)

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
    Lc = 0.5 # m, hydraulic diamater #TODO: how to fix this parameter ?
    Tp, Tfl, P = vars # T in K, P is in W/m2
    h_fl_air = libh.convective_heat_transfer_coefficient(Tfl, Tair, Lc)
    h_p_amb = libh.convective_heat_transfer_coefficient(Tp, Tamb, Lc)
    h_p_air = libh.convective_heat_transfer_coefficient(Tp, Tair, Lc)
    h_star = 10 #TODO: how to fix this parameter ?


    eq1 = Iatm + direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) - h_star * (Tp - Tamb) - libh.infrared_energy_flux(Tp)
    eq2 = P - h_fl_air * (Tfl - Tair) - h_p_air * (Tp - Tair) * R
    eq3 = direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) * k - (libh.infrared_energy_flux(Tfl) - libh.infrared_energy_flux(Tp)) - h_fl_air * (Tfl - Tair)

    return [eq1, eq2, eq3]



def Tair_z_plus_dz(P, Tair):
    dz = DELTA
    Tair_next =  Tair + P * Wd / (Q * Ca) * dz

    return Tair_next

def darboux_lower_sum(y: list, dt)->float:
    print("Lower sum darboux")
    lower_sum = 0
    for i in range(len(y)-1):
        lower_sum += y[i] * dt
        print(i)

    print("Lower sum darboux: ", lower_sum)
    return lower_sum



def darboux_sum(lower_sum, upper_sum):
    return (lower_sum + upper_sum)/2

def darboux_upper_sum(y: list, dz) -> float:
    print("Upper sum darboux")
    upper_sum = 0
    for i in range(len(y)-1):
        upper_sum += y[i+1] * dz
        print(i)

    print("Upper sum darboux: ", upper_sum)
    return upper_sum

# TODO: moyenne des sommes de Darboux
def balance_equations_drying(vars, *data):
    Tair, t = data
    M0 = 9.8 #kg
    Mf = 1.8 #kg
    LD = 3.0 #m
    Wd = 1.4  # m
    Ms = mass_per_surface_unit(M0, LD, Wd)
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
    # z = 0
    dz = DELTA  # m
    Q = 0.03  # kg of humid air / s
    Ca = 1009  # Heat capacity, J/kg/K
    Lc = 0.5  # m, hydraulic diamater
    Tp, Tfl, P = vars  # T in K, P is in W/m2
    h_fl_air = 2#libh.convective_heat_transfer_coefficient(Tfl, Tair, Lc)
    h_p_air = 1#libh.convective_heat_transfer_coefficient(Tp, Tair, Lc)
    h_star = 10
    Xf = 0.1 # kg d'eau par kilo
    X0 = 7.0
    Lw = 2358 * 1000    # J/kg
    td = 6.5
    EV = Ms / (1+X0) * (X0 - Xf) / td * Lw

    eq1 = P - h_fl_air * (Tfl - Tair) - R * h_p_air * (Tp - Tair)
    eq2 = direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) + Iatm - h_star * (Tp - Tair) - libh.infrared_energy_flux(Tp)
    eq3 = direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) * k - h_fl_air * (Tfl - Tair) - libh.infrared_energy_flux(Tfl) + libh.infrared_energy_flux(Tp) - EV

    return [eq1, eq2, eq3]

def temperature_time_t_drying(Tamb, t, LH):
    z = 0
    data = (Tamb, t)
    Tair = Tamb
    # Tp, Tfl, P = vars
    s0 = [310, 320, 350]
    x = fsolve(balance_equations_drying, s0, args=data)
    while z < LH:
        z = round(z + DELTA, 2)
        P = x[2]
        #print("Tair avant: ", Tair-273, " °C")
        Tair = Tair_z_plus_dz(P,Tair)
        #print("Tair next: ", Tair-273)
        data = (Tair, t)  # Tair = Tair_next de l'itération précédente
        s0 = x            # old solution is the new initial solution
        x = fsolve(balance_equations_drying, s0, args=data)
        y = list(x)
        y[0] -= 273
        y[1] -= 273
        print("En z = ", z, " et t = ", t, " : ", y, "\n")
        #a = isclose(balance_equations_Tp(x, Tair, t), [0.0, 0.0, 0.0])  # check if numerical solution makes sense
        #print(a)
    y.append(Tair-273)
    print(t)
    return y

def mass_per_surface_unit(M0, LD, Wd):
    Ms = M0/(LD * Wd)
    return Ms

def main():

    LD = 3 # m, length drying part
    z = 0
    Tair = 30 + 273
    LH = 5  # m; length heating part.

    t0 = 9.5 #heures, début du séchage
    td = 6.5 #heures, durée du séchage
    tf = td + t0  #heures, fin du séchage
    Tamb = 30 + 273 # °K (mean diurnal temperature)
    z = 0
    t = t0
    Tair_LH = []
    P_LH = []
    all_t = []


    #Tp, Tfl, P = vars
    while t < tf:
        x = temperature_time_t(Tamb, t, LH)
        P_t = x[2]
        Tair_LH_t = x[3]
        Tair_LH.append(Tair_LH_t)
        P_LH.append(P_t)
        all_t.append(t)
        t += 0.5
    y = list(Tair_LH)
    for i in range(len(y)):
        y[i] += 273



    upper_sum = darboux_upper_sum(y, 0.5)/td
    lower_sum = darboux_lower_sum(y, 0.5)/td
    print("Upper: ", upper_sum, " \n Lower: ", lower_sum)

    #fit = polyfit(all_t, Tair_LH, 2)
    #print(fit)
    #f
    #print(len(all_t))
    #print(len(Tair_LH))

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


    # Graphe de la température de l'air à la fin de la zone de chauffe au long de la journée


    #print(x)

    # plt.xlabel('Time of the day (h)')
    # plt.ylabel('Temperatures (°C)')
    # plt.title('Temperature inside the dryer during the day')
    # plt.plot([10,20,30], [2,6,5], 'go')
    # tikzplotlib.save("mytikz.tex")

if __name__ == '__main__':
    main()


