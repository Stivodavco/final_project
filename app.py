from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
import re
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
db = SQLAlchemy(app)

from login_management import setup_login_manager

setup_login_manager()

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
            "user": offer.user,
            "user_id": offer.user_id,
            "user_name": offer.user.name
        })
        offers.append(offer_dict)

    filter_by = request.args.get("filter")
    order = request.args.get("order")
    value = request.args.get("value")

    if value:
        offers = list(filter(lambda item: True if value.lower() in item["title"].lower() or value.lower() in item["user_name"].lower() else False, offers))

    if filter_by and order:
        if filter_by == "price":
            offers.sort(key=lambda item: item["price"],reverse=True if order == "desc" else False)
        elif filter_by == "rating":
            offers.sort(key=lambda item: item["user"].get_rating()[0] * item["user"].get_rating()[1], reverse=True if order == "desc" else False)
    return render_template("offers.html", active_page="offers", offers=offers, current_user=current_user, selected_filter=filter_by, selected_order=order, search_value="" if value is None else value)

@app.route('/offers/create')
@login_required
def create_offer():
    return render_template("create_offer.html", current_user=current_user)

@app.route('/about')
def about():
    return render_template("about.html", active_page="about", current_user=current_user)

@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("signup.html", active_page="login")
    elif request.method == "POST":
        name = request.form.get("name", None)
        description = request.form.get("description", "")
        username = request.form.get("username", None)
        password = request.form.get("password", None)

        regex = "^[a-zA-Z0-9_-]+$"

        name_valid = bool(name) and 3 <= len(name) <= 50
        username_valid = username and re.fullmatch(regex,username) and len(username) >= 3 <= 50 and not User.query.filter_by(username=username).first()
        description_valid = len(description) <= 300
        password_valid = password and len(password) >= 8 <= 255

        if name_valid and username_valid and description_valid and password_valid:
            new_user = User()
            new_user.name = name
            if description == "":
                new_user.description = None
            else:
                new_user.description = description
            new_user.username = username
            new_user.password = password

            try:
                db.session.add(new_user)
                db.session.commit()
            except Exception as error:
                db.session.rollback()
                print(error)
            else:
                login_user(new_user)
                return redirect(url_for("dashboard"))

        error_msg = "Chyba pri pridávaní uživateľa. Skontroluje či ste splnili všetky kritéria."

        if not username_valid:
            error_msg = "Použivateľské meno je už použité."

        return render_template("signup.html", error=error_msg)

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("login.html", active_page="login")
    elif request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)

        if username and password:
            user = User.query.filter_by(username=username).first()

            if user and user.password == password:
                login_user(user)
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", active_page="login",error="Nesprávne používateľské meno alebo heslo!")
    else:
        return "Invalid request method", 405

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("show_offers"))

@app.route('/user/<int:user_id>')
def display_user(user_id):
    user = User.query.get(user_id)
    offers = list(map(lambda offer: offer.dict(),user.offers))
    reviews = []

    for review in user.reviews:
        user_name = review.sender.name
        review_dict = review.dict()
        review_dict.update({
            "user_name": user_name,
        })
        reviews.append(review_dict)

    user_rating = user.get_rating()

    return render_template("user.html", offers=offers, reviews=reviews, user=user.dict(), reviews_num=user_rating[1], rating=user_rating[0])

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", active_page="dashboard",current_user=current_user)

if __name__ == '__main__':
    app.run()