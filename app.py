from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, login_required
import unicodedata
import re
import os

from mypyc.primitives.set_ops import new_set_op

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
db = SQLAlchemy(app)

from login_management import setup_login_manager

setup_login_manager()

from models.user import User
from models.offer import Offer
from models.review import Review
from models.message import Message

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

@app.route('/')
def index():
    return redirect(url_for("show_offers"))

@app.errorhandler(404)
def show_error(e):
    return render_template("error.html", http_code=404, error="Stránka na ktorú ste sa chceli dostať neexistuje! Skontrolujte URL pre chyby.")

@app.errorhandler(500)
def show_error(e):
    return render_template("error.html", http_code=500, error="Ups! Naše servery spadli. Nič s vami!")

@app.route('/offers')
def show_offers():
    offers_objs = Offer.query.all()
    offers = []
    for offer in offers_objs:
        offer_dict = offer.dict()
        offer_dict.update({
            "user_id": offer.user_id,
            "user_name": offer.user.name,
            "owner_rating": offer.user.get_rating()[0]
        })
        if offer_dict["price"] is None:
            offer_dict.pop("price")
        offers.append(offer_dict)

    filter_by = request.args.get("filter")
    order = request.args.get("order")
    value = request.args.get("value")

    if value:
        offers = list(filter(lambda item: True if remove_accents(value.lower()) in remove_accents(item["title"].lower()) or remove_accents(value.lower()) in remove_accents(item["user_name"].lower()) else False, offers))

    offers = list(filter(lambda item: True if not item["interested_user_id"] else False, offers))

    if filter_by and order:
        if filter_by == "price":
            offers.sort(key=lambda item: item.get("price",0),reverse=True if order == "desc" else False)
        elif filter_by == "rating":
            offers.sort(key=lambda item: item["owner_rating"], reverse=True if order == "desc" else False)
    return render_template("offers.html", active_page="offers", offers=offers, current_user=current_user, selected_filter=filter_by, selected_order=order, search_value="" if value is None else value)

@app.route('/offers/create', methods=["GET", "POST"])
@login_required
def create_offer():
    if request.method == "GET":
        return render_template("create_offer.html", current_user=current_user)
    elif request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description", "")
        price = request.form.get("price")
        specification = request.form.get("specification")

        if request.form.get("no_price"):
            new_offer = Offer()
            new_offer.title = title
            new_offer.description = description
            new_offer.has_price = False
            new_offer.user_id = current_user.id
            db.session.add(new_offer)
            db.session.commit()
            return render_template("create_offer.html", current_user=current_user, success="Ponuka bola pridaná.")
        else:
            title_valid = 3 <= len(title) <= 100
            description_valid = len(description) <= 1000
            specification_valid = len(specification) <= 10
            try:
                price_valid = price and int(price) <= 1000000
            except ValueError:
                return render_template("create_offer.html", current_user=current_user, error="Cenu musí byť číslo.")

            if not price_valid:
                return render_template("create_offer.html", current_user=current_user, error="Cena ponuky nemôže byť nad 1 000 000€")

            if title_valid and description_valid and price_valid and specification_valid:
                new_offer = Offer()
                new_offer.title = title
                new_offer.description = description
                new_offer.has_price = True
                new_offer.price = price
                new_offer.user_id = current_user.id
                if specification != "":
                    new_offer.specification = specification
                db.session.add(new_offer)
                db.session.commit()
                return render_template("create_offer.html", current_user=current_user, success="Ponuka bola pridaná.")
        return render_template("create_offer.html", current_user=current_user, error="Nastala chyba.")
    else:
        return "Invalid request method", 405

@app.route('/offers/<int:offer_id>', methods=["GET","POST"])
def show_offer(offer_id):
    if request.method == "GET":
        offer = Offer.query.get(offer_id)

        if offer:
            offer_dict = offer.dict()

            available = True
            interested_user_name = None
            if offer.interested_user:
                available = False
                interested_user_name = offer.interested_user.name

            offer_dict.update({
                "user_name" : offer.user.name,
                "interested_user_name": interested_user_name,
                "available": available
            })

            messages = []
            show_chat = False
            owner_view = False
            if current_user.is_authenticated and (current_user.id == offer.interested_user_id or current_user.id == offer.user_id):
                message_objs = Message.query.filter_by(offer_id=offer.id)

                for message in message_objs:
                    message_dict = message.dict()
                    message_dict.update({
                        "sender_name": message.sender_user.name,
                        "sent_by_me": True if current_user.id == message.sender_user_id else False
                    })
                    messages.append(message_dict)

                if current_user.id == offer.user_id:
                    owner_view = True

                show_chat = True

            return render_template("offer.html", active_page="offers", offer=offer_dict, current_user=current_user, messages=messages, show_chat=show_chat, owner_view=owner_view)
        else:
            return render_template("error.html", http_code=404, error="Stránka na ktorú ste sa chceli dostať neexistuje! Skontrolujte URL pre chyby."), 404
    elif request.method == "POST":
        offer = Offer.query.get(offer_id)

        if not offer:
            return render_template("error.html", http_code=404, error="Stránka na ktorú ste sa chceli dostať neexistuje! Skontrolujte URL pre chyby."), 404

        join_chat = request.form.get("join_chat")
        leave_chat = request.form.get("leave_chat")

        if not current_user.is_authenticated:
            return render_template("login.html", active_page="login", current_user=current_user)

        # join and leave chat if you have interest
        if join_chat and not offer.interested_user and current_user.id != offer.user_id:
            offer.interested_user_id = current_user.id
            db.session.commit()
            return redirect(url_for("show_offer",offer_id=offer_id))
        elif leave_chat and (offer.interested_user_id == current_user.id or offer.user_id == current_user.id):
            offer.interested_user_id = None
            messages = offer.messages
            for message in messages:
                db.session.delete(message)

            db.session.commit()
            return redirect(url_for("show_offer",offer_id=offer_id))

        # handle messages if sent
        message = request.form.get("message")

        if message and len(message) <= 300 and offer.interested_user_id:
            new_message = Message()
            new_message.sender_user_id = current_user.id
            new_message.offer_id = offer.id
            new_message.text = message
            db.session.add(new_message)
            db.session.commit()

        return redirect(url_for("show_offer",offer_id=offer_id))

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
        name = request.form.get("name")
        description = request.form.get("description", "")
        username = request.form.get("username")
        password = request.form.get("password")

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
        username = request.form.get("username")
        password = request.form.get("password")

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

@app.route('/user/<int:user_id>', methods=["GET","POST"])
def display_user(user_id):
    if request.method == "GET":
        user = User.query.get(user_id)
        offers = list(map(lambda offer: offer.dict(), user.offers))
        reviews = []

        for review in user.reviews:
            user_name = review.sender.name
            review_dict = review.dict()
            review_dict.update({
                "user_name": user_name,
            })
            reviews.append(review_dict)

        user_rating = user.get_rating()

        sender_valid = True
        for review in user.reviews:
            if review.sender_id == current_user.id:
                sender_valid = False

        if current_user.is_authenticated and user_id == current_user.id:
            sender_valid = False

        return render_template("user.html", offers=offers, reviews=reviews, user=user.dict(), reviews_num=user_rating[1], rating=user_rating[0], can_review=sender_valid)
    elif request.method == "POST":
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        if not current_user.is_authenticated:
            return render_template("login.html", active_page="login", current_user=current_user)

        try:
            rating = int(rating)
        except ValueError:
            return redirect(url_for("display_user",user_id=user_id))

        rating_valid = rating and rating >= 1 <= 5
        comment_valid = comment and 3 <= len(comment) <= 300
        sender_valid = True

        user = User.query.get(user_id)

        for review in user.reviews:
            if review.sender_id == current_user.id:
                sender_valid = False

        if user_id == current_user.id:
            sender_valid = False

        if rating_valid and comment_valid and sender_valid:
            print("adding review!")
            new_review = Review()
            new_review.sender_id = current_user.id
            new_review.recipient_id = user_id
            new_review.rating = rating
            new_review.comment = comment

            db.session.add(new_review)

            try:
                db.session.commit()
            except Exception as error:
                print("Error while adding review: ", error)
                db.session.rollback()

        return redirect(url_for("display_user",user_id=user_id))

@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "GET":
        offers = Offer.query.filter_by(user_id=current_user.id)

        offers = list(map(lambda offer: offer.dict(), offers))

        return render_template("dashboard.html", active_page="dashboard", current_user=current_user, offers=offers)

    elif request.method == "POST":
        offer_id = request.form.get("delete_offer_id")

        if offer_id:
            offer = Offer.query.get(offer_id)

            if offer.user_id == current_user.id:
                db.session.delete(offer)

                try:
                    db.session.commit()
                except Exception as error:
                    print("Error while deleting offer:", error)
                    db.session.rollback()

        return redirect(url_for("dashboard"))

if __name__ == '__main__':
    app.run()