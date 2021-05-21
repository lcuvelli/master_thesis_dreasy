from time import process_time
import fluids.atmosphere as fl
from flask import Flask, render_template
from flask import request, flash, Markup

from model import heating_section as heatsectionlib, air_flow_rate as airflowlib, drying_section as dryingsectionlib

P_ATM = 101325  # atm pressure  (Pa)


app = Flask(__name__)
app.secret_key = "key"


def test_main():
    print("hello")
    print("hello again")

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/contacts")
def contacts():
    return render_template('contacts.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/database")
def database():
    return render_template('database.html')

@app.route("/dryer_dimensions")
def dryerdimensions():
    status = "waiting"

    # Climatic data
    Sm = request.args.get("Sm", type=float)
    RHamb = request.args.get("RHamb", type=float)
    Tamb_C = request.args.get("Tamb_C", type=float)
    trise = request.args.get("trise", type=float)
    tset = request.args.get("tset", type=float)
    Iatm = request.args.get("Iatm", type=float)

    # Specifications

    td = request.args.get("td", type=float)
    t0 = ""
    Td_C = request.args.get("Td_C", type=float)
    Q = request.args.get("Q", type=float)
    M0 = request.args.get("M0", type=float)
    X0 = request.args.get("X0", type=float)
    Xf = request.args.get("Xf", type=float)


    # Dryer design
    #R = request.args.get("R", type=float)
    #if not R :
    #    R = 1.5
    Wd = request.args.get("Wd", type=float)
    print("Wd")
    if not Wd:
        Wd = 1.5
    H = request.args.get("H", type=float)
    if not H:
        H = 0.5
    h = request.args.get("h", type=float)
    if not h:
        h = 0.3

    k = request.args.get("k", type=float)
    if not k:
        k = 0.85

    Lsup = round(heatsectionlib.lenght_sup_dryer(H, h, Wd), 3)
    Wp = round(Lsup + H + h,3)
    R =  round(Wp / Wd,3)
    Lc = round(heatsectionlib.hydaulic_diameter(H,h,Wd), 3)

    context = {"RHamb": RHamb, "Tamb_C": Tamb_C, "Sm": Sm, "trise": trise, "tset": tset,
               "R": R, "td": td, "t0": t0, "Iatm": Iatm, "Q": Q, "Td_C": Td_C, "M0": M0,
               "Wd": Wd, "h": h, "H": H, "Lsup": Lsup, "Wp": Wp, "Lc": Lc, "k": k, "status": status, "Xf": Xf, "X0": X0}

    solution = {}

    i = 0
    if request.method == 'GET':
        if request.args.get('Compute') == 'Compute':
            Tamb = Tamb_C + 273.15
            print(Tamb_C, Tamb)
            Td = Td_C + 273.15
            density = fl.ATMOSPHERE_1976.density(Td, P_ATM)  # densité de l'air
            Q_kg_s = Q/3600 * density

            if tset <= trise:
                message = Markup(
                    'Warning: Sunrise time (t<sub>rise</sub>) <b>before</b> sunset time ((t<sub>set</sub>).')
                i += 1
                flash(message)

            if td > tset - trise:
                message = Markup(
                    'Warning: Drying time (t<sub>d</sub>) is <b>bigger</b> than day time. The drying should be done in a day.')
                i += 1
                flash(message)

            if i == 0 :
                status = "running"
                t1_start = process_time()
                t0 = heatsectionlib.start_time_drying(td, tset, trise)


                print(X0, Xf, td)
                solution = heatsectionlib.compute_heating_length(Tamb, Iatm, Sm, tset, trise, Lc, R, k, Q_kg_s, Wd, td, Td)
                print("Tair:", solution['Tair_LH'])
                print("P:", solution['P_LH'])


                t1_stop = process_time()

                print("Elapsed time during the whole program in seconds:",
                      t1_stop - t1_start)
                drying_length = dryingsectionlib.compute_drying_length(X0, Xf, M0, td, t0, Td-273, Wd, solution['P_LH'], solution['Tair_LH'] )


                solution['LD'] = round(drying_length['LD'],1)
                solution['Td_mean'] = round(solution['Td_mean'], 1)
                print("LD:", solution['LD'])
                status = "waiting"

    context = {"RHamb": RHamb, "Tamb_C": Tamb_C, "Sm": Sm, "trise": trise, "tset": tset,
               "R": R, "td": td, "t0": t0, "Iatm": Iatm, "Q": Q, "Td_C": Td_C, "M0": M0,
               "Wd": Wd, "h": h, "H": H, "Lsup": Lsup, "Wp": Wp, "Lc": Lc, "k": k, "status": status, "Xf": Xf, "X0": X0}

    print(context)
    return render_template("dryerdimensions.html", context=context, solution=solution)

@app.route("/airflow")
def airflow():
    Q = ""
    mass_to_evaporate = ""
    RHamb = request.args.get("RHamb", type=float)
    Tamb_C = request.args.get("Tamb_C", type=float)
    M0 = request.args.get("M0", type=float)
    X0 = request.args.get("X0", type=float)
    Xf = request.args.get("Xf", type=float)
    td = request.args.get("td", type=float)
    Td_C = request.args.get("Td_C", type=float)


    #if request.method == 'GET':
    if request.args.get('Compute') == 'Compute':
        Tamb = Tamb_C + 273.15  # Conversion Celsius to Kelvin
        Td = Td_C + 273.15
        i = 0

        if Xf >= X0:
            message = Markup(
                'Warning: Final moisture content of the product (X<sub>f</sub>) should be <b>lower</b> than inital moisture (X<sub>0</sub>).')
            i += 1
            flash(message)

        if Tamb >= Td:
            message = Markup(
                'Warning: Ambient temperature (T<sub>amb</sub>) should be <b>lower</b> than drying temperature (T<sub>d</sub>).')
            flash(message)
            i += 1

        elif (i == 0):
            mass_to_evaporate = M0 / (1 + X0) * (X0 - Xf)
            mass_to_evaporate = round(mass_to_evaporate,1)
            density = 1.014 #fl.ATMOSPHERE_1976.density(Td, P_ATM) # densité de l'air
            Q = airflowlib.compute_air_flow_rate(RHamb, Tamb, M0, X0, Xf, td, Td)
            Q = round(Q * 3600 / density,1)   # in m^3/h

            if Q < 0:
                message = Markup(
                    'Error: Minimal air flow is negative. Not feasible with conditions given. Please try again.')
                flash(message)
            print(Q)

    context = {"RHamb": RHamb, "Tamb_C": Tamb_C, "M0": M0, "X0": X0, "Xf": Xf, "td": td, "Td_C": Td_C, "Q": Q}




    #context = {"active": "Miniaml Air Flow"}

    return render_template('airflow.html', mass_to_evaporate = mass_to_evaporate, context=context)




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
