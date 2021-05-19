"""Functions not specially linked to the model, such as evaluating the area under a function
or deal with dictionnary structure """


def darboux_sum(y: list, dt)->float:
    """Gives the Darboux sum, computed as the mean value between the lower and upper Darboux.

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

    return (lower_sum + upper_sum)/2


def toCelsius(T: list):
    """Converts a list of temperatures in Kelvin to Celsius"""
    res = []
    for elem in T:
        res.append(elem-273)
    return res


def extract_temperature_air(filtered_storage):
    """From the filtered dictionnary, extract Tair for t from t0 to tf """

    temperature_air = []
    for key in filtered_storage:
        temperature_air.append(filtered_storage[key][3]) # 3rd element is temperature

    return temperature_air


def extract_energy_flux(filtered_storage):
    """From the filtered dictionnary, extract P for t from t0 to tf """

    energy_flux = []
    for key in filtered_storage:
        energy_flux.append(filtered_storage[key][2])

    return energy_flux

def key_satifies_condition(k, zmax):
    "Used to filter the dictionary STORAGE, the key (t,z) satisfies condition if z = zmax"
    length = k[0]
    return (length == zmax)

