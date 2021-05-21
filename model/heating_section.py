from math import pi, sin
from math import sqrt, pow
from time import process_time
import os

import matplotlib.pyplot as plt
from scipy.optimize import fsolve

from model import heat_transfer_coefficient as libh, tools as tools

#ep = 0.001 # m - Plastic thickness
#lp = 0.2  # W/m*K - Plastic thermal conductivity
#e = 6 / 1000  # m - Thickness of the slices of product

Tmax = 90   # °C - maximal Tair allowed at the end of the heating section along the day #TODO: discuss function product
tol = 2    # °C (or K) - tolerance on the mean temperature in the dryer

DELTA_Z = 0.1
DELTA_T = 0.5
ADD_STORAGE = True
STORAGE = {}

def lenght_sup_dryer(H, h, Wd):
    """Calculates superior length of the dryer when cross section is trapezoidal"""
    Lsup = sqrt(pow((H - h), 2) + pow(Wd, 2))
    return Lsup

def hydaulic_diameter(H, h, Wd):
    """Calculates hydraulic parameter defined as the ratio of 4 times the surface by the perimeter"""
    Lsup = lenght_sup_dryer(H,h,Wd)
    S = h * Wd + Wd * h / 2
    P = H + h + Wd + Lsup

    Lc = 4 * S / P
    return Lc


def direct_diffuse_solar_radiation(Sm: float, t_set: float, t_rise: float, t: float) -> float:
    S = pi/2 * Sm * sin(pi * (t - t_rise)/(t_set-t_rise))
    return S


def temperature_time_t(Tamb, t, Iatm, Sm, tset, trise, Lc, R, k, LH, Q, Ca, Wd)->list:
    """Gives the temperature profile in the heating section at one time t of the day.
    The first execution (assuming LH >>), all the values will be stored in the dict STORAGE with keys (z,t)
    and values [Tp, Tfl, P, Tair]

    Args:
        Tamb: ambient temperature (in K)
        t: time of the day
        LH: length of the heating section

    Returns:
        x: values of Tp, Tfl, P and Tair when z = LH at time t"""

    z = 0
    data = (Tamb, t, Iatm, Sm, tset, trise, Tamb, Lc, R, k)
    Tair = Tamb

    s0 = [310, 320, 350] # Initial vector
    x = fsolve(balance_equations_heating, s0, args=data)

    i = 0
    while z < LH:
        z = round(z + DELTA_Z, 2)
        P = x[2]
        Tair = Tair_z_plus_dz(P, Tair, Q, Ca, Wd)
        data = (Tair, t, Iatm, Sm, tset, trise, Tamb, Lc, R, k)  # Tair = Tair_next from previous iteration
        s0 = x            # Old solution is the new initial solution
        x = fsolve(balance_equations_heating, s0, args=data)


    # TODO: remettre print
        print(i,": En (z,t) = (", z, ",", t, "): ", "(Tp, Tfl, P) = (",x[0]-273, "°C,", x[1]-273, "°C,", P, "W/m2) \n")
        #print(isclose(balance_equations_Tp(x, Tair, t), [0.0, 0.0, 0.0]))  # Check if numerical solution makes sense
        i += 1
        # Dictionnary filled only once
        if ADD_STORAGE :
            y = x.tolist()
            y.append(Tair)
            STORAGE[(z,t)] = y


    x = x.tolist()  # Converts numpy.ndarray to list

    x.append(Tair)
    return x

def balance_equations_heating(vars, *data):
    """System 3x3 of balance equations of the heating section.
    The unknown are the temperature of the plastic (Tp), the temperature of the floor (Tfl) and the
    energy flux transferred to the air inside the dryer (P).
    Assumption that the inner and outer surface of the plastic cover have the same temperature (Ti = To = Tp).

    Args:
        data: (Tair, t) with
        Tair: air temperature at one slice of the heating section (cross section in z) (in K)
        t: time of the day """

    Tair, t, Iatm, Sm, tset, trise, Tamb, Lc, R, k = data

    Tp, Tfl, P = vars # T in K, P is in W/m2

    # Heat transfer coefficients depend on the temperatures
    h_fl_air = libh.convective_heat_transfer_coefficient(Tfl, Tair, Lc)
    h_p_air = libh.convective_heat_transfer_coefficient(Tp, Tair, Lc)
    h_star = 10 # libh.convective_heat_transfer_coefficient(Tp, Tamb, 2.3)
    #print(h_star, h_fl_air, h_p_air)

    eq1 = Iatm + direct_diffuse_solar_radiation(Sm, tset, trise, t) - h_star * (Tp - Tamb) - libh.infrared_energy_flux(Tp)
    eq2 = P - h_fl_air * (Tfl - Tair) - h_p_air * (Tp - Tair) * R
    eq3 = direct_diffuse_solar_radiation(Sm, tset, trise, t) * k - (libh.infrared_energy_flux(Tfl) - libh.infrared_energy_flux(Tp)) - h_fl_air * (Tfl - Tair)

    return [eq1, eq2, eq3]



def Tair_z_plus_dz(P, Tair, Q, Ca, Wd):
    """Gives the temperature of the air in the heating section in (z + dz) when Tair and P are known in z.

        Args:
            P: energy flux transferred to the air inside the dryer at one time t and one length z
            Tair: air temperature at one slice of the heating section (cross section in z) (in K) """

    dz = DELTA_Z
    Tair_next =  Tair + P * Wd / (Q * Ca) * dz

    return Tair_next

def estimate_length_heating(Tair_LH: list, LH, td, Td):
    """Estimates the optimal length of the drying part with two criteria (not used simultaneously)
    Criteria 1: Temperature at the end of the heating section (z = LH)  never exceeds a certain threshold Tmax.
    Criteria 2: Mean temperature at the end of the heating section (z = LH) from t0 to tf is Td.

    Args:
        Tair_LH: list of temperatures in °C
        LH: the last length tried

    Returns:
         -1 if LH has to be decreased
         1 if LH has to be increased
         0 otherwise """

    # Criteria 1
    max_temperature = max(Tair_LH)
    if abs(max_temperature-Tmax) < tol:
        result = 0

    elif max_temperature < Tmax:
        result = 1
    elif max_temperature > Tmax:
        result = -1


    # Criteria 2
    mean_temperature = tools.darboux_sum(Tair_LH, DELTA_T) / td
    print("Note: with LH = ", LH, " mean Td is : ", mean_temperature, " °C")
    print(mean_temperature, Td, abs(mean_temperature-Td))
    if abs(mean_temperature - Td) < tol :
        result = 0

    elif mean_temperature < Td:
        result = 1
        print("Need to bigger LH")
    elif mean_temperature > Td:
        result = -1
        print("Need to lower LH")

    print(result)
    return result


def start_time_drying(td, tset, trise):
    t0 = (trise + tset)/2 - td/2
    return t0

def temperatures_heating_section(Tamb, td, Iatm, Sm, tset, trise, Lc, R, k, LH, Q, Ca, Wd)->list:
    """Gives the temperature profile at the end of the drying section is calculated for a certain length of the
    drying section. We only calculate half of time because it is symetric (S(t) is symetric)

    Args:
       LH: length of the drying section  """

    t = start_time_drying(td, tset, trise)
    t0 = start_time_drying(td, tset, trise)
    tf = t + td
    mid_drying = (t0 + tf)/2
    profile_end_heating = []

    while t <= tf:
        x = temperature_time_t(Tamb, t, Iatm, Sm, tset, trise, Lc, R, k, LH, Q, Ca, Wd)
        profile_end_heating.append(x)
        t += DELTA_T
    print(profile_end_heating)

    return profile_end_heating

def filter_dictionnary(zmax):
    "Filters the dictionnary for all values of z == zmax. Returns the filtered dictionnary"
    filtered_dic = {k: v for (k, v) in STORAGE.items() if tools.key_satifies_condition(k, zmax)}
    return filtered_dic

def find_next_value(test_length_heating, res, LH, intervals_z):
    """Gives the next value of LH that has to be tested based on dichotomic search.

    Args:
         test_length_heating: list values of LH already test
         res: -1 / +1 if LH has to decrease / increase
         LH: the last value of LH tested (not yet added to the list) """

    if res == -1 :
        lower = min([i for i in test_length_heating if i < LH], key=lambda x: abs(x - LH))
        next = lower + (LH - lower)/2

    if res == 1 :
        upper = min([i for i in test_length_heating if i >= LH], key=lambda x: abs(x - LH))
        next = upper + (LH - upper) / 2

    next_rounded = round(next,1)
    print("Next value of LH to try should be:", next, "but is rounded to:", next_rounded, "m")
    return next_rounded


def main():
    Tamb = 28 + 273.15  # °K (mean diurnal temperature)
    Iatm = 322  # W/m2
    Sm = 613  # W/m2
    tset = 18  # h - Time sunset
    trise = 6  # h - Time sunrise
    R = 1.5  # m - Aspect ratio
    Lc = 0.66  # m - Hydraulic diamater #fixed by cross section
    k = 0.85  # Reduction factor
    Q = 0.024 #(au lieu de 0.023)  # kg of humid air/s - Air flow rate
    Wd = 1.95  # m - Width of the dryer
    td = 8
    Td = 72+273.15


    solution = compute_heating_length(Tamb, Iatm, Sm, tset, trise, Lc, R, k, Q, Wd, td, Td)

    print(solution['Tair_LH'], "\n", solution['LH'], "\n", solution['P_LH'], "\n")
    os.system('say "over"')

def compute_heating_length(Tamb, Iatm, Sm, tset, trise, Lc, R, k, Q, Wd, td, Td):

    print("Tamb:", Tamb)
    print("Iatm:", Iatm)
    print("Sm:", Sm)
    print("tset:", tset)
    print("trise:", trise)
    print("Lc", Lc)
    print("R:", R)
    print('k:', k)
    print('Q:', Q)
    print("Wd:", Wd)
    print("td:", td)
    print("Td:", Td)
    Td = Td - 273.15
    t0 = start_time_drying(td, tset, trise)
    tf = td + t0  # h - End of drying
    Ca = 1009  # Heat capacity air, J/kg/K (assumed constant)


    LH = 4.4
    air = 3  # Tair is the 4th element of vector x
    energy = 2  # P is the 3rd element of vector x
    Tair_LH, P_LH, intervals_z, intervals = [], [], [], []
    z = 0
    while z <= LH:
        intervals_z.append(z)
        z += DELTA_Z

    global ADD_STORAGE
    ADD_STORAGE = True

    t1_start = process_time()
    profile_end_heating = temperatures_heating_section(Tamb, td, Iatm, Sm, tset, trise, Lc, R, k, LH, Q, Ca, Wd)
    t1_stop = process_time()
    print("Elapsed time during the whole program in seconds:",
          t1_stop - t1_start)
    ADD_STORAGE = False

    # Get Tair and P profile in z = LH and
    for i in range(len(profile_end_heating)):
        Tair_LH.append(profile_end_heating[i][air] - 273.15)  # Converting temperature from K to °C
        P_LH.append(profile_end_heating[i][energy])

    t = t0
    while t <= tf:
        intervals.append(t)
        t += DELTA_T

    res = estimate_length_heating(Tair_LH, LH, td, Td)
    if res == 1 :
        mean_temperature = tools.darboux_sum(Tair_LH, DELTA_T) / td
        print("Note: with LH,max = ", LH, " mean Td is : ", mean_temperature, " °C")
        return 0 #TODO: gérer le cas dans le site web

    test_length_heating = [0]  # Keeps track of the LH values tested
    filtered_storage = filter_dictionnary(LH)

    while res != 0 and (len(test_length_heating) == len(set(test_length_heating))):
        new_LH = find_next_value(test_length_heating, res, LH, intervals_z)

        test_length_heating.append(LH)
        LH = new_LH

        print("List of trials ", test_length_heating, " now we try ", LH)
        filtered_storage = filter_dictionnary(LH)
        Tair_LH = tools.toCelsius(tools.extract_temperature_air(filtered_storage))
        res = estimate_length_heating(Tair_LH, LH, td, Td)
    Tair_LH = tools.toCelsius(tools.extract_temperature_air(filtered_storage))
    P_LH = tools.extract_energy_flux(filtered_storage)
    mean_temperature = tools.darboux_sum(Tair_LH, DELTA_T) / td

    print("---> Heating length is: ", LH, "m")


    solution = {"LH": LH, "Tair_LH": Tair_LH, "P_LH": P_LH, "Td_mean": mean_temperature}

    return solution

    #draw_profiles(Tair_LH, P_LH, intervals, LH)



def draw_profiles(Tair_LH: list, P_LH: list, intervals: list, LH):
    """Plot the temperature and energy flux profiles at the end of the drying section

        Args:
           Tair_LH: list of air temperature in function of time t
           P_LH: list of energy flux in function of time t
           intervals: time intervals from t0 to tf with step DELTA_T """


    plt.figure(1)
    plt.xlabel('Time of the day (h)')
    plt.ylabel('Temperatures (°C)')
    plt.title('Temperature inside the dryer during the day, heating section is %1.2f' %LH)
    plt.plot(intervals, Tair_LH, 'go')
    # plt.show()

    plt.figure(2)
    plt.xlabel('Time of the day (h)')
    plt.ylabel('Energy flux (W/m2)')
    plt.title('Energy flux transferred to the air inside the dryer, heating section is %1.2f' %LH)
    plt.plot(intervals, P_LH, 'ro')
    plt.show()

    # Save graph in Latex format (before plt.show())
    # tikzplotlib.save("mytikz.tex")

if __name__ == '__main__':
    main()


