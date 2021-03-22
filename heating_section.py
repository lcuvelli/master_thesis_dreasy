import heat_transfer_coefficient as libh

from scipy.optimize import fsolve
from numpy import isclose, polyfit
import matplotlib.pyplot as plt
import tikzplotlib

from math import exp, pi, sin


"""Constants"""
Ca = 1009 # Heat capacity air, J/kg/K

"""Climatic data - Cambodia"""
Sm = 463  # W/m2
Tamb = 30 + 273  # °K (mean diurnal temperature)
t_rise = 7  # h - Time sunrise
t_set = 19  # h - Time sunset
t0 = 9.5    # h - Start of drying
td = 6.5    # h - Drying time
tf = td + t0  #h - End of drying
RHamb = 70  # %
Iatm = 377  # W/m2



"""Specifications - Drying 10kg of mangoes in Cambodia"""
R = 1.4   # m - Aspect ratio
Q = 0.03  # kg of humid air/s - Air flow rate
Wd = 1.4  # m - Width of the dryer
k = 0.85  # Reduction factor
M0 = 10   # kg - Mass of product
ep = 0.001 # m - Plastic thickness
lp = 0.2  # W/m*K - Plastic thermal conductivity
e = 6 / 1000  # m - Thickness of the slices of product


Lc = 0.5  # m - Hydraulic diamater #TODO: how to fix this parameter ?
h_star = 10                        #TODO: how to fix this parameter ?
Td = 50     # °C - mean temperature at the end of the heating section along the day #TODO: discuss
Tmax = 90   # °C - maximal Tair allowed at the end of the heating section along the day #TODO: discuss function product
tol = 1     # °C (or K) - tolerance on the mean temperature in the dryer

DELTA_Z = 0.5
DELTA_T = 0.5
ADD_STORAGE = True
STORAGE = {}


def direct_diffuse_solar_radiation(Sm: float, t_set: float, t_rise: float, t: float) -> float:
    S = pi/2 * Sm * sin(pi * (t - t_rise)/(t_set-t_rise))
    return S

def toCelsius(T: list):
    """Converts a list of temperatures in Kelvin to Celsius"""
    res = []
    for elem in T:
        res.append(elem-273)
    return res


def temperature_time_t(Tamb, t, LH)->list:
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
    data = (Tamb, t)
    Tair = Tamb

    s0 = [310, 320, 350] # Initial vector
    x = fsolve(balance_equations_heating, s0, args=data)

    while z < LH:
        z = round(z + DELTA_Z, 2)
        P = x[2]
        Tair = Tair_z_plus_dz(P,Tair)
        data = (Tair, t)  # Tair = Tair_next from previous iteration
        s0 = x            # Old solution is the new initial solution
        x = fsolve(balance_equations_heating, s0, args=data)

        print("En (z,t) = (", z, ",", t, "): ", "(Tp, Tfl, P) = (",x[0]-273, "°C,", x[1]-273, "°C,", P, "W/m2) \n")
        #print(isclose(balance_equations_Tp(x, Tair, t), [0.0, 0.0, 0.0]))  # Check if numerical solution makes sense

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

    Tair, t = data

    Tp, Tfl, P = vars # T in K, P is in W/m2

    # Heat transfer coefficients depend on the temperatures
    h_fl_air = libh.convective_heat_transfer_coefficient(Tfl, Tair, Lc)
    h_p_air = libh.convective_heat_transfer_coefficient(Tp, Tair, Lc)

    eq1 = Iatm + direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) - h_star * (Tp - Tamb) - libh.infrared_energy_flux(Tp)
    eq2 = P - h_fl_air * (Tfl - Tair) - h_p_air * (Tp - Tair) * R
    eq3 = direct_diffuse_solar_radiation(Sm, t_set, t_rise, t) * k - (libh.infrared_energy_flux(Tfl) - libh.infrared_energy_flux(Tp)) - h_fl_air * (Tfl - Tair)

    return [eq1, eq2, eq3]



def Tair_z_plus_dz(P, Tair):
    """Gives the temperature of the air in the heating section in (z + dz) when Tair and P are known in z.

        Args:
            P: energy flux transferred to the air inside the dryer at one time t and one length z
            Tair: air temperature at one slice of the heating section (cross section in z) (in K) """

    dz = DELTA_Z
    Tair_next =  Tair + P * Wd / (Q * Ca) * dz

    return Tair_next


def darboux_sum(y: list, dt)->float:
    """Gives the Darboux sum, computed as the mean value between the lower and upper Darboux the mean.

    Args:
        y: List of the value of the function on the interval [0, len(y)]
        dt: length of the subinterval of the partition """

    lower_sum = 0
    upper_sum = 0

    for i in range(len(y) - 1):
        inf = min(y[i], y[i+1])
        sup = max(y[i], y[i+1])

        lower_sum += inf * dt
        upper_sum += sup * dt
    print("Lower Darboux sum:", lower_sum)
    print("Upper Darboux sum:", upper_sum)

    return (lower_sum + upper_sum)/2

def estimate_length_heating(Tair_LH: list, LH):
    """Estimates the optimal length of the drying part with two criteria (not used simultaneously)
    Criteria 1: Temperature at the end of the heating section (z = LH)  never exceeds a certain threshold Tmax.
    Criteria 2: Mean temperature at the end of the heating section (z = LH) from t0 to tf is Td.

    Args:
        Tair_LH: list of temperatures in °C
        LH: the last length tried

    Returns:
         -1 if LH has to be decreased
         1 if LH has to e increased
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
    mean_temperature = darboux_sum(Tair_LH, DELTA_T) / td
    print("with LH = ", LH, " mean T : ", mean_temperature)
    if abs(mean_temperature - Td) < tol :
        result = 0

    elif mean_temperature < Td:
        result = 1
    elif mean_temperature > Td:
        result = -1

    print(result)
    return result



def temperatures_heating_section(LH)->list:
    """Gives the temperature profile at the end of the drying section is calculated for a certain length of the
    drying section.

    Args:
       LH: length of the drying section  """

    t = t0
    profile_end_heating = []

    while t <= tf:
        x = temperature_time_t(Tamb, t, LH)
        profile_end_heating.append(x)
        t += DELTA_T

    return profile_end_heating

def key_satifies_condition(k, zmax):
    "Used to filter the dictionary STORAGE, the key (t,z) satisfies condition if z = zmax"
    length = k[0]
    return (length == zmax)

def filter_dictionnary(zmax):
    "Filters the dictionnary for all values of z == zmax. Returns the filtered dictionnary"
    filtered_dic = {k: v for (k, v) in STORAGE.items() if key_satifies_condition(k,zmax)}
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

    next = min(intervals_z, key=lambda x:abs(x-next))

    return next

def extract_temperature_air(filtered_storage):
    """From the filtered dictionnary, extract Tair for t from t0 to tf """

    temperature_air = []
    for key in filtered_storage:
        temperature_air.append(filtered_storage[key][3])

    return temperature_air

def main():
    LH = 3
    air = 3     # Tair is the 4th element of vector x
    energy = 2  # P is the 3rd element of vector x
    Tair_LH = []
    P_LH = []
    intervals = []
    intervals_z = [] # All the value of z tested
    z = 0
    while z <= LH:
        intervals_z.append(z)
        z += DELTA_Z

    global ADD_STORAGE
    ADD_STORAGE = True

    profile_end_heating =  temperatures_heating_section(LH)
    ADD_STORAGE = False

    # Get Tair and P profile in z = LH and
    for i in range(len(profile_end_heating)):
        Tair_LH.append(profile_end_heating[i][air]-273) # Converting temperature from K to °C
        P_LH.append(profile_end_heating[i][energy])

    t = t0
    while t <= tf:
        intervals.append(t)
        t += DELTA_T

    res = estimate_length_heating(Tair_LH, LH)

    test_length_heating = [0, LH]  # Keeps track of the LH values tested

    while res != 0 and (len(test_length_heating) == len(set(test_length_heating))):

        LH = find_next_value(test_length_heating, res, LH, intervals_z)
        test_length_heating.append(LH)

        print("LH/list ", LH, test_length_heating)
        filtered_storage = filter_dictionnary(LH)
        print(filtered_storage)
        Tair_LH = toCelsius(extract_temperature_air(filtered_storage))
        res = estimate_length_heating(Tair_LH, LH)


    print(STORAGE)



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


