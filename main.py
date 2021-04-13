from flask import Flask, render_template
from flask import request, flash, Markup
from flask_socketio import SocketIO, emit

import time
import air_flow_rate as airflowlib
import heating_section as heatsectionlib


app = Flask(__name__)
app.secret_key = "key"
socketio = SocketIO(app)


def test_main():
    print("hello")
    time.sleep(5)
    print("hello again")

@app.route("/")
def home():
    return render_template('home.html')
#TODO: nav.html logo renders strangely when changing page


@app.route("/contacts")
def contacts():
    return render_template('contacts.html')

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/dryer_dimensions")
def dryerdimensions():
    status = "waiting"

    # Climatic data
    Sm = request.args.get("Sm", type=float)
    RHamb = request.args.get("RHamb", type=float) #TODO: already input in airflow
    Tamb = request.args.get("Tamb", type=float) #TODO: already input in airflow
    trise = request.args.get("trise", type=float)
    tset = request.args.get("tset", type=float)
    Iatm = request.args.get("Iatm", type=float)

    # Specifications

    td = request.args.get("td", type=float)  # TODO: already input in airflow
    t0 = ""
    Td = request.args.get("Td", type=float)  # TODO: already input in airflow
    Q = request.args.get("Q", type=float)  # TODO: already input in airflow
    M0 = request.args.get("M0", type=float)  # TODO: already input in airflow


    # Dryer design
    #R = request.args.get("R", type=float)
    #if not R :
    #    R = 1.5
    Wd = request.args.get("Wd", type=float)
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

    solution = {}

    i = 0
    if request.method == 'GET':
        if request.args.get('Compute') == 'Compute':

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
                t0 = heatsectionlib.start_time_drying(td, tset, trise)
                solution = heatsectionlib.compute_heating_length(Tamb, Iatm, Sm, tset, trise, Lc, R, k, Q, Wd, td, Td)
                status = "waiting"

    context = {"RHamb": RHamb, "Tamb": Tamb, "Sm": Sm, "trise": trise, "tset": tset,
               "R": R, "td": td, "t0": t0, "Iatm": Iatm, "Q": Q, "Td": Td, "M0": M0,
               "Wd": Wd, "h": h, "H": H, "Lsup": Lsup, "Wp": Wp, "Lc": Lc, "k": k, "status": status}

    return render_template("dryerdimensions.html", context=context, solution=solution)

@app.route("/airflow")
def airflow():
    Q = ""
    mass_to_evaporate = ""
    RHamb = request.args.get("RHamb", type=float)
    Tamb_C = request.args.get("Tamb", type=float)
    M0 = request.args.get("M0", type=float)
    X0 = request.args.get("X0", type=float)
    Xf = request.args.get("Xf", type=float)
    td = request.args.get("td", type=float)
    Td_C = request.args.get("Td", type=float)


    if request.method == 'GET':
        if request.args.get('Compute') == 'Compute':
            Tamb = Tamb_C + 273  # Conversion Celsius to Kelvin
            Td = Td_C + 273
            i = 0
            print("YES")

            if Xf >= X0:
                message = Markup(
                    'Warning: Final moisture content of the product (Xf) should be <b>lower</b> than inital moisture (X0).')
                i += 1
                flash(message)

            if Tamb >= Td:
                message = Markup(
                    'Warning: Ambient temperature (Tamb) should be <b>lower</b> than drying temperature (Td).')
                flash(message)
                i += 1

            elif (i == 0):
                mass_to_evaporate = M0 / (1 + X0) * (X0 - Xf)
                Q = round(airflowlib.compute_air_flow_rate(RHamb, Tamb, M0, X0, Xf, td, Td), 4)
                if Q < 0:
                    message = Markup(
                        'Error: Minimal air flow is negative. Not feasible with conditions given. Please try again.')
                    flash(message)
                print(Q)

    context = {"RHamb": RHamb, "Tamb_C": Tamb_C, "M0": M0, "X0": X0, "Xf": Xf, "td": td, "Td_C": Td_C}




    #context = {"active": "Miniaml Air Flow"}

    return render_template('airflow.html', Q=Q, mass_to_evaporate = mass_to_evaporate, context=context)




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
