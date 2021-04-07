from flask import Flask, render_template
from flask import request, escape
import air_flow_rate as calc



app = Flask(__name__)

@app.route("/")
def index():
    air_flow = str(calc.main())
    celsius = str(escape(request.args.get("celsius", "")))
    print(type(celsius))
    print(celsius)
    if celsius:
        fahrenheit = fahrenheit_from(celsius)
    else :
        fahrenheit = ""
    return "Fahrenheit: " + fahrenheit + render_template('index.html', greetings=celsius) + "TEST: " + air_flow

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