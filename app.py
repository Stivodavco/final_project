from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for("show_offers"))

@app.route('/offers')
def show_offers():
    return render_template("offers.html", active_page="offers", offers=[{"title":"ajdfblkajdfklbjadadfklbnadlfkbnfadklbnladkbnladfbn;adfblnadfk;bnadf;bnkadfbndankfbjnkdfbndkfbnjkdfbn"}])

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
