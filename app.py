import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/weather.db'
app.config["SECRET_KEY"] = "verysecretkey"

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "City(id={}, name={})".format(self.id, self.name)


def get_city_weather(city_name):
    """
    Getting city weather
    """
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid={}"   # noqa
    r = requests.get(
        url.format(city_name, "metric", "60026bf1dd5d07bd4cfd4bed17e08f0e")
    ).json()
    return r


@app.route('/')
def index_get():
    cities = City.query.all()
    weather_data = []
    for city in cities:
        r = get_city_weather(city.name)
        weather_data.append({
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon']
        })

    return render_template("weather.html", weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    error_msg = None
    new_city = request.form.get('city')
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            r = get_city_weather(new_city)
            if r.get('weather'):
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                error_msg = "Invalid city!"
        else:
            error_msg = "City already exists!"
    if error_msg:
        flash(error_msg, "error")
    else:
        flash("City added!")

    return redirect(url_for("index_get"))


@app.route('/delete/<name>')
def delete_city(name):
    city_to_delete = City.query.filter_by(name=name).first()
    db.session.delete(city_to_delete)
    db.session.commit()
    flash("Successfully deleted {}!".format(city_to_delete.name))
    return redirect(url_for("index_get"))


if __name__ == '__main__':
    app.run(debug=True)
