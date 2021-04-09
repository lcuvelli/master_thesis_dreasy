import numpy as np
import thermopy.iapws as th
from sympy import symbols, solve
import typing
# -*-coding:Latin-1 -*


# Definition des constantes (systeme international)
MOLAR_MASS_WATER = 18.01528/1000  # molar mass of water [ kg/mol ]
MOLAR_MASS_AIR = 28.965/1000      # molar mass of air   [ kg/mol ]
P_ATM = 101325                    # atm pressure        [ Pa ]


######### PART 1 - gemoetry #############

"""
Input: - Wd width of the dryer (in m) 
       - Wp length of the cross-section of the plastic cover transverse to the flow (in m)
Output: aspect ratio of the flow cross-section of the dryer (no unit)
"""
def aspect_ratio(Wd: float, Wp: float) -> float:
    R = Wp/Wd
    return R

######### PART 1 - climatic data #############



######### PART 2 #############
"""
Input: temperature T (in Kelvin) 
Output: the saturation pressure of water at the temperature T (in Pa)"""
def pressure_saturation_water(T: float) -> float:
    w = th.Water(101.3, T)  # pressure arbitrary value
    return w.pressure_saturation(T)

"""
Input: temperature T (in kelvin)
Outuput: (absolute) Humidity of air saturated with water at the air temperature T (in kg of water/kg of dry air)
"""
def absolute_humidity_air_saturated(T: float) -> float:
    Y_sat = (MOLAR_MASS_WATER * (pressure_saturation_water(T)/P_ATM) / (MOLAR_MASS_AIR*(1 - pressure_saturation_water(T)/P_ATM) ))
    return Y_sat

"""
Input: - mean diurnal ambient air relative RHamb (no unit)
       - mean diurnal ambient air temperature Tamb (in Kelvin)
Output: mean diurnal ambient air humidity (in kg of water/kg of dry air)
"""
def mean_ambient_air_humidity(RHamb: float, Tamb: float) -> float:
    Yamb = RHamb * absolute_humidity_air_saturated(Tamb)  # RHamb * Ysat (Tamb)  # QUESTION: non lineaire normalement ?
    return Yamb

def minimal_air_flow_rate(Yamb: float, M0: float, X0: float, Xf: float, td: float, Td: float) -> float:
    """Returns the minimal air flow rate defined as the air flow rate that would lead to an air
    saturated with water at the exit of the dryer.

    Args:
        Yamb: air humidity - kg water/kg dry air
        M0: initial mass of product - kg
        X0: initial moisture of products - kg water/kg dry product
        Xf: final moisture of products - kg water/kg dry product
        td: drying time - hours
        Td : drying temperature - K

    Returns:
        Qmin: minimal air flow rate"""

    x = symbols('x')
    td = td * 3600
    Ysat_Td = absolute_humidity_air_saturated(Td)
    expr = x * (Ysat_Td-Yamb)/(1+Yamb) - M0/(1+X0)*(X0-Xf)*1/td

    Qmin = solve(expr)

    return float(Qmin[0])

def air_flow_rate(Qmin: float, F:float) -> float:
    """Return air flow rate

    Args:
        Qmin: minimal air flow rate
        F: design coefficient """

    Q = F * Qmin
    return Q


def compute_air_flow_rate(RHamb: float, Tamb: float, M0: float, X0: float, Xf: float, td: float, Td: float)->float:

    F = 12
    RHamb = RHamb / 100
    Yamb = mean_ambient_air_humidity(RHamb, Tamb)
    print("Données : \n",
          "M0 : ", M0, " kg \n",
          "X0 : ", X0, " kg water / kg dry product \n",
          "Xf : ", Xf, " kg water / kg dry product \n",
          "td : ", td * 3600, " s or ", td, "h \n",
          "Td : ", Td, " K or", Td - 273.15, "°C \n",
          "Tamb : ", Tamb, " K or", Tamb - 273.15, "°C \n",
          "RHamb : ", RHamb, " / \n"
                             "-----------------")
    print("Yamb is: ", round(Yamb, 5), " kg of water/kg of dry air")
    print("Masse d'eau initiale : ", M0 / (1 + X0) * (X0), " kg d'eau")
    print("Masse d'eau à évaporer : ", M0 / (1 + X0) * (X0 - Xf), " kg d'eau \n -----------------")

    Qmin = minimal_air_flow_rate(Yamb, M0, X0, Xf, td, Td)
    print("Qmin is : ", round(Qmin, 5), " kg humid air / s")


    Q = air_flow_rate(Qmin, F)
    print("Q is : ", round(Q, 5), " kg humid air / s, using factor F = ", F)

    return Q


######### TESTS #############

def main():
    print("\n --- Let's try out for Cambodia (Q = 0.030 with F = 12 so Qmin should be 0.0025) --- ")
    Tamb = 30+273.15 # K
    RHamb = 70/100      # %
    Yamb = mean_ambient_air_humidity(RHamb, Tamb)

    X0 = 7      # kg water / kg dry product
    Xf = 0.1    # kg water / kg dry product
    M0 = 10     # kg
    td = 6.5 # seconds
    Td = 62.5+273.15 # K
    print("Données : \n",
          "M0 : ", M0, " kg \n",
          "X0 : ", X0, " kg water / kg dry product \n",
          "Xf : ", Xf, " kg water / kg dry product \n",
          "td : ", td, " s or ", td/3600, "h \n",
          "Td : ", Td, " K or", Td-273.15, "°C \n",
          "Tamb : ", Tamb, " K or", Tamb-273.15, "°C \n",
          "RHamb : ", RHamb, " / \n"
                             "-----------------")
    print("Yamb is: ", round(Yamb, 5), " kg of water/kg of dry air")
    print("Masse d'eau initiale : ", M0 / (1 + X0) * (X0), " kg d'eau")
    print("Masse d'eau à évaporer : ", M0 / (1 + X0) * (X0 - Xf), " kg d'eau \n -----------------")

    Qmin = minimal_air_flow_rate(Yamb, M0, X0, Xf, td, Td)
    print("Qmin is : ", round(Qmin,5), " kg humid air / s")

    F = 12
    Q = air_flow_rate(Qmin, F)
    print("Q is : ", round(Q, 5), " kg humid air / s, using factor F = ", F)

if __name__ == '__main__':
    main()