from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
db = SQLAlchemy(app)

from models.user import User
from models.offer import Offer
from models.review import Review
from models.message import Message

@app.route('/')
def index():
    return redirect(url_for("show_offers"))

@app.route('/offers')
def show_offers():
    offers_objs = Offer.query.all()
    offers = []
    for offer in offers_objs:
        offer_dict = offer.dict()
        offer_dict.update({
            "user": offer.user.dict()
        })
        offers.append(offer_dict)
    return render_template("offers.html", active_page="offers", offers=offers)

@app.route('/offers/create')
def create_offer():
    return render_template("create_offer.html")

@app.route('/about')
def about():
    return render_template("about.html", active_page="about")

@app.route('/signup')
def signup():
    return render_template("signup.html", active_page="login")

@app.route('/login')
def login():
    return render_template("login.html", active_page="login")

@app.route('/user/<int:id>')
def user(id):
    return render_template("user.html")

if __name__ == '__main__':
    app.run()
