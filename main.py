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

@app.route("/dryer_dimensions")
def dryer_dimensions():
    context = {"computing": True}
    return render_template('dryerdimensions.html', context = context)


@app.route("/contacts")
def contacts():
    return render_template('contacts.html')

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/t")
def test():

    # Climatic data
    Sm = request.args.get("Sm", type=float)
    RHamb = request.args.get("RHamb", type=float) #TODO: already input in airflow
    Tamb = request.args.get("Tamb", type=float) #TODO: already input in airflow
    trise = request.args.get("trise", type=float)
    tset = request.args.get("tset", type=float)
    Iatm = request.args.get("Iatm", type=float)

    # Specifications
    R = request.args.get("R", type=float)
    if not R :
        R = 1.5
    td = request.args.get("td", type=float) #TODO: already input in airflow
    t0 = ""
    Td = request.args.get("Td", type=float) #TODO: already input in airflow
    Q = request.args.get("Q", type=float)  #TODO: already input in airflow
    M0 = request.args.get("M0", type=float) #TODO: already input in airflow

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
                t0 = heatsectionlib.start_time_drying(td, tset, trise)

    context = {"RHamb": RHamb, "Tamb": Tamb, "Sm": Sm, "trise": trise, "tset": tset,
               "R": R, "td": td, "t0": t0, "Iatm": Iatm, "Q": Q, "Td": Td, "M0": M0}

    return render_template("test.html", context=context)

@app.route("/airflow")
def airflow():
    Q = ""
    mass_to_evaporate = ""
    RHamb = request.args.get("RHamb", type=float)
    Tamb = request.args.get("Tamb", type=float)
    M0 = request.args.get("M0", type=float)
    X0 = request.args.get("X0", type=float)
    Xf = request.args.get("Xf", type=float)
    td = request.args.get("td", type=float)
    Td = request.args.get("Td", type=float)

    context = {"RHamb": RHamb, "Tamb": Tamb, "M0": M0, "X0":X0, "Xf": Xf, "td": td, "Td": Td}

    i = 0

    if RHamb and Tamb and M0 and X0 and Xf and td and Td:
        if Xf >= X0   :
            message = Markup('Warning: Final moisture content of the product (Xf) should be <b>lower</b> than inital moisture (X0).')
            i += 1
            flash(message)

        if Tamb >= Td :
            message = Markup('Warning: Ambient temperature (Tamb) should be <b>lower</b> than drying temperature (Td).')
            flash(message)
            i += 1

        elif (i==0):
            mass_to_evaporate = M0 / (1 + X0) * (X0 - Xf)
            Q = round(airflowlib.compute_air_flow_rate(RHamb, Tamb, M0, X0, Xf, td, Td), 5)
            if Q < 0 :
                message = Markup(
                    'Error: Minimal air flow is negative. Not feasible with conditions given. Please try again.')
                flash(message)
            print(Q)



    #context = {"active": "Miniaml Air Flow"}

    return render_template('airflow.html', Q=Q, mass_to_evaporate = mass_to_evaporate, context=context)




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
