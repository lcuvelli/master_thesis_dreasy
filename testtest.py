from math import sqrt
import heat_transfer_coefficient as libh


def lenght_sup_dryer(H, h, Wd):
    """Calculates superior length of the dryer when cross section is trapezoidal"""

    return sqrt(pow((H - h), 2) + pow(Wd, 2))

print(lenght_sup_dryer(0.5,0.3,1.5))


def hydaulic_diameter(H, h, Wd):
    """Calculates hydraulic parameter defined as the ratio of 4 times the surface by the perimeter"""
    Lsup = lenght_sup_dryer(H, h, Wd)
    print('lsup', Lsup)

    S = h * Wd + Wd * (H-h) / 2

    print("Surface:", S)
    P = H + h + Wd + Lsup
    print("P:", P)

    Lc = 4 * S / P
    print("Lc", Lc)
    return Lc

print(hydaulic_diameter(0.5,0.3,1.5))

print("h*:", libh.convective_heat_transfer_coefficient(300, 330, 1.5))
print("hnormal:", libh.convective_heat_transfer_coefficient(300, 330, 0.7))
context = {}
context = {"Tair": 3}
print(context['Tair'])
context['Tair'] = context['Tair'] + 273
print(context['Tair'])