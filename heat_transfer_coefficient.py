import fluids.atmosphere as fl
from iapws.humidAir import Air
from thermopy.constants import standard_acceleration_of_gravity

import matplotlib.pyplot as plt


"""Calculate the convective heat transfer coefficient from two temperature and the hydraulic parameter given as input"""

# Definition des constantes

STEPHAN_BOLTZMANN = 5.6704 * 10 ** (-8) # W / (m^2 * K^4)
P_ATM = 101325                          # atm pressure  (Pa)
G = standard_acceleration_of_gravity    # m / s^2

thermal_expansion_coefficients = {-5: 3.76,
                                 0: 3.69,
                                 5: 3.62,
                                 10: 3.56,
                                 15: 3.50,
                                 20: 3.43,
                                 25: 3.38,
                                 30: 3.32,
                                 40: 3.21,
                                 50: 3.12,
                                 60: 3.02,
                                 80: 2.85,
                                 100: 2.70}  # 10-3 * K-1
# from : https://www.engineeringtoolbox.com/air-density-specific-weight-d_600.html
# TO DO: check source from literature


"""
Input: - temperature T (in K)
       - emissivity e (no units) should be [0,1]
Output: Infrared energy flux (in W / m^2) - emitting surfaces are considered as black bodies
"""
def infrared_energy_flux(T: float, e: float = 1.0) -> float: # Rayonnement
    return e * STEPHAN_BOLTZMANN * T ** 4

"""
Input: - plastic thickness ep (in m)
       - plastic thermal conductivity lp (in W / (m * K) )
       - temperature in T_in (in K)
       - temperature out T_out (in K)

Output: Conductive heat flux (in W / m^2) - Fourier's law
"""
def conductive_heat_flux(lp: float, ep: float, Tout: float, Tin: float) -> float: # Conduction
    Dp = lp / ep * abs(Tout-Tin)
    return Dp

"""
Input: - coefficient heat transfer h (in W / (m^2 * K) )
       - hot temperature T1 (in K)
       - cold temperature T2 (in K)

Output: Convective heat flux (in W / m^2) - Newton's law 
"""
def convective_heat_flux(h: float, T1: float, T2: float) -> float: # Convexion
    C = h * abs(T1-T2)
    return C


"""
Input: temperature T (in K)
Outuput Prandlt number of air at temp T
"""
def Prandtl_air(T: float) -> float:
    #thermal_conductivity = fl.ATMOSPHERE_1976.thermal_conductivity(T) # W/(m K)
    #kinematic_viscosity = fl.ATMOSPHERE_1976.viscosity(T) # m^2 / s
    #density = fl.ATMOSPHERE_1976.density(T, P_ATM)        # kg / m^3
    #dynamic_viscosity = density * kinematic_viscosity     # Pa * s
    #air = thb.Database().set_compound("AIR")              # get air element from database
    #heat_capacity_massic = air.heat_capacity(T) / air.mm  # specific heat capacity in J/(kg K)

    air = Air(T=T, P=1.01325) # arbitrary pressure (in MPa)
    Prandtl_number = air.Prandt

    return Prandtl_number

"""
Input: 
    - delta de temperature dT (in K)

Outuput Grashof : number of air at temp T [W/m/K]
"""
def Grashof_air(T1: float, T2: float, D)-> float:
    # - thermal expansion coefficient air (K-1)
    # - kinematic viscosity of the air (m^2/s)
    # - D is the hydraulic parameter
    # - gravity
    # - dT = delta de temperature
    dT = abs(T1-T2) # delta temperature
    T = (T1+T2)/2
    kinematic_viscosity = fl.ATMOSPHERE_1976.viscosity(T)  # m^2 / s
    # Find the closest value from the expansion coefficients dictionary
    thermal_expansion_coefficient = thermal_expansion_coefficients.get(T, thermal_expansion_coefficients[min(thermal_expansion_coefficients.keys(), key=lambda k: abs(k - T))])/1000

    return (thermal_expansion_coefficient * standard_acceleration_of_gravity[0] * (D**3) * dT) / (kinematic_viscosity ** 2)


def Rayleigh_air(T1: float, T2: float, D)-> float:
    Prandtl = Prandtl_air((T1+T2)/2)
    Grashof = Grashof_air(T1, T2, D)
    return Prandtl * Grashof


def convective_heat_transfer_coefficient(T1: float, T2: float, D)-> float: # Find h based on Rayleigh number
    thermal_conductivity = fl.ATMOSPHERE_1976.thermal_conductivity((T1+T2)/2)
    h = 0.4 * (Rayleigh_air(T1,T2,D)**0.25) * thermal_conductivity / D
    return h  # in W/m2/K

def main():
    T1 = 25+273
    x = []
    y = []
    for i in range (0, 80, 5):
        T2 = 25+273 + i
        h = convective_heat_transfer_coefficient(float(T1), float(T2), 0.2)
        print("h is ", h, " W/m2/K when T2 is ", T2)
        if (i!=0):
            x.append(T2-273)
            y.append(h)

    print(x)
    plt.plot(x, y, 'bs')
    plt.ylabel('h')
    plt.xlabel('T2 (°C)')
    plt.title('Convective heat transfer coefficient when T1 = 25°C and L = 1m')
    plt.show()
    h = convective_heat_transfer_coefficient(float(70+273), float(100+273), 0.2)
    print(h)

    # print("This file calculate the heat transfer coefficient")
    # T1 = input("Please enter temperature 1 (in K):\n")
    # T2 = input("Please enter temperature 2 (in K):\n")
    # D = input("Please enter hydraulic diameter: (in m):\n")
    # h = convective_heat_transfer_coefficient(float(T1), float(T2), float(D))
    # print("h is ", h , " W/m2/K")

if __name__ == '__main__':
    main()
