from flask import Flask, render_template
from flask import request, escape, flash, Markup
import air_flow_rate as airflow
import sys



app = Flask(__name__)
app.secret_key = "key"


@app.route("/")
def index():
    print('Hello world!', file=sys.stderr)
    Q = ""
    mass_to_evaporate = ""
    RHamb = request.args.get("RHamb", type=float)
    Tamb = request.args.get("Tamb", type=float)
    M0 = request.args.get("M0", type=float)
    X0 = request.args.get("X0", type=float)
    Xf = request.args.get("Xf", type=float)
    td = request.args.get("td", type=float)
    Td = request.args.get("Td", type=float)

    i = 0

    if RHamb and Tamb and M0 and X0 and Xf and td and Td:
        if Xf > X0   :
            message = Markup('Warning: Final moisture content of the product (Xf) should be <b>lower</b> than inital moisture (X0).')
            i += 1
            flash(message)

        if Tamb >= Td :
            message = Markup('Warning: Ambient temperature (Tamb) should be <b>lower</b> than drying temperature (Td).')
            flash(message)
            i += 1

        elif (i==0):
            mass_to_evaporate = M0 / (1 + X0) * (X0 - Xf)
            Q = airflow.compute_air_flow_rate(RHamb, Tamb, M0, X0, Xf, td, Td)
            if Q < 0 :
                message = Markup(
                    'Error: Minimal air flow is negative. Not feasible with conditions given. Please try again.')
                flash(message)

            print(Q)

    return render_template('index.html', Q=Q, mass_to_evaporate = mass_to_evaporate)





def fahrenheit_from(celsius):
    """Convert Celsius to Fahrenheit degrees."""
    try:
        fahrenheit = float(celsius) * 9 / 5 + 32
        fahrenheit = round(fahrenheit, 3)  # Round to three decimal places
        return str(fahrenheit)
    except ValueError:
        return "invalid input"


@app.route("/contacts")
def contacts():
    return render_template('contacts.html')

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/t")
def test():
    return render_template('test.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)


#
# if __name__ == "__main__":
#     celsius = input("Celsius: ")
#     print("Fahrenheit:", fahrenheit_from(celsius))