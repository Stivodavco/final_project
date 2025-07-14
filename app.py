from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for("show_offers"))

@app.route('/offers')
def show_offers():
    return render_template("offers.html", active_page="offers")

if __name__ == '__main__':
    app.run()
