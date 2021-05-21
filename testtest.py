from math import sqrt
from model import tools as tool
from model import heat_transfer_coefficient as libh


def lenght_sup_dryer(H, h, Wd):
    """Calculates superior length of the dryer when cross section is trapezoidal"""

    return sqrt(pow((H - h), 2) + pow(Wd, 2))

print(lenght_sup_dryer(0.5,0.3,1.5))


def hydaulic_diameter(H, h, Wd):
    """Calculates hydraulic parameter defined as the ratio of 4 times the surface by the perimeter"""
    Lsup = lenght_sup_dryer(H, h, Wd)
    print('lsup', Lsup)
    print("Wp:", H+h+Lsup)
    Wp = H+h+Lsup
    R = Wp/Wd
    print("Aspect ratio R:", R)

    S = h * Wd + Wd * (H-h) / 2

    print("Surface:", S)
    P = H + h + Wd + Lsup
    print("P:", P)

    Lc = 4 * S / P
    print("Lc", Lc)
    return Lc

print(hydaulic_diameter(0.5,0.3,1.95))



def complete(t_list):
    # complete a list of L elements
    L = []
    t0 = t_list[0]
    mid = (t_list[0]+t_list[len(t_list)-1])/2
    t = t0
    i=0
    while t < mid:
        L.append(t_list[i]*5)
        print(i, ":", t_list[i])
        i+=1
        t+=t_list[1]-t_list[0]
        print("t", t)
    print("now t is:", t)
    print(t_list[-1])
    print(t_list)

    if t == mid:
        newlist = L[::-1]
        L.append(t_list[i] * 5)
        L.extend(newlist)
        print("oui")
        print(len(L))
    else:
        newlist = L[::-1]
        L.extend(newlist)
        #for j in range(1,len(L)+1,-1):
        #    print(j)
        #    L.append(L[-j])
    #else:
    #    L[j] = 1

    print(L)

print(1)
complete([1,2,3,4])
print("\n",2)
complete([1,2,3,4,5])