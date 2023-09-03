import os
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# iigure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
  # Create a table for index
    rows = db.execute("SELECT symbol, SUM(shares),shares FROM transactions WHERE user_id=:user_id GROUP BY symbol HAVING SUM(shares) > 0", user_id=session["user_id"])

    # Creates a place to save the informations
    holdings = []
    all_total = 0

    for row in rows:
        stock = lookup(row['symbol'])
        sum_value = (stock["price"] * row["SUM(shares)"])
        holdings.append({"symbol": stock["symbol"], "name": stock["name"], "shares": row["SUM(shares)"], "price": usd(stock["price"]), "total": usd(sum_value)})
        all_total += stock["price"] * row["SUM(shares)"]
        if row['shares']<0:
            all_total -= row['shares']*stock['price']

    rows = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    cash = rows[0]["cash"]
    all_total += cash

    return render_template("index.html", holdings=holdings, cash=usd(cash), all_total=usd(all_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    #user accessing page (via GET)
    if request.method == 'GET':
        return render_template('buy.html')
    #user submiting transaction info (via POST)
    else:
        #get user info
        buy_symbol = request.form.get("symbol")
        buy_shares = int(request.form.get('shares'))
        stock = lookup(buy_symbol.upper())
        #validade user info
        if not buy_symbol:
            apology("Must provide a stock symbol")
        elif stock == None:
            apology("This is not a valid stock symbol")
        elif buy_shares < 0:
            apology("This share is not allowed")
        #get transaction value and compare with user`s cash
        transaction_value = buy_shares * stock['price']
        user_id = session['user_id']
        user_cash_from_db = db.execute("SELECT cash FROM users WHERE id=?", user_id)
        user_cash = user_cash_from_db[0]['cash']
        if user_cash < transaction_value:
            return apology("There is not enough money")
        updated_user_cash = user_cash - transaction_value
        #update user table
        db.execute("UPDATE users SET cash=? WHERE id=?", updated_user_cash, user_id)
        #get date and update transactions table
        date = datetime.datetime.now()
        db.execute("INSERT INTO transactions(user_id, symbol, shares, price, date) VALUES(?,?,?,?,?)", user_id, buy_symbol,buy_shares,stock['price'], date)
        #redirect to main route
        flash("Bought!")
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT symbol, shares, price FROM transactions WHERE user_id=:user_id", user_id=session["user_id"])
    for i in range(len(transactions)):
        transactions[i]["price"] = usd(transactions[i]["price"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote"""
    if request.method == 'GET': #user accessing page via GET
        return render_template('quote.html')

    else: #user submiting info to server via POST
        #get symbol inputed by user
        stock_symbol = request.form.get("symbol")
        #data validation for stock symbol
        if not stock_symbol:
            return apology("Provide a symbol")
        stock = lookup(stock_symbol.upper())
        if stock == None:
            return apology("This sybol does not exist")
        #display results and stock information from back-end to front-end
        return render_template("quoted.html", name = stock['name'], price = stock['price'], symbol = stock['symbol'])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #forget any user id
    session.clear()

    #user sendind info to server to register
    if request.method == 'POST':
        #get user`s credentials (form)
        username = request.form.get("username")
        psw = request.form.get("password")
        confirm_psw = request.form.get("confirmation")

        #user`s credentials validation
        if not username or not psw or not confirm_psw:
            return apology("A username, password, and password confirmation must be provided.")
        if len(db.execute("SELECT username FROM users WHERE username = ?", username)) != 0:
            return apology("This username is already taken.")
        if psw != confirm_psw:
            return apology("The confirmation does not match with the originally provided password.")
        #hash psw
        hashed_psw = generate_password_hash(psw)

        #insert user on db
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES(?,?)", username, hashed_psw)
        except:
            return apology("Something went wrong. Try again.")
        #remember user
        session["user_id"] = new_user
        #redirect to main page
        return redirect("/")


    #user getting to register page (via GET)
    else:
        return render_template('register.html')


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
   # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure stock was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol")

        # Ensure shares was submitted
        elif not request.form.get("shares"):
            return apology("must provide shares")

        # Ensure shares is greater than 0
        elif int(request.form.get("shares")) < 0:
            return apology("must provide a valid number of shares")

        # Ensure shock exists
        if not request.form.get("symbol"):
            return apology("must provide an existing symbol")

        # Lookup function
        symbol = request.form.get("symbol").upper()
        stock = lookup(symbol)

        rows = db.execute("SELECT symbol, SUM(shares) FROM transactions WHERE user_id=:user_id GROUP BY symbol HAVING SUM(shares) > 0", user_id=session["user_id"])

        # Value of transaction
        shares = int(request.form.get("shares"))
        for row in rows:
            if row["symbol"] == symbol:
                if shares > row["SUM(shares)"]:
                    return apology("you're doing something wrong")

        transaction = shares * stock['price']

        # Check if user has enough cash for transaction
        user_cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = user_cash[0]["cash"]

        # Subtract user_cash by value of transaction
        updt_cash = cash + transaction

        # Update how much left in his account (cash) after the transaction
        db.execute("UPDATE users SET cash=:updt_cash WHERE id=:id", updt_cash=updt_cash, id=session["user_id"]);
        # Update de transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=session["user_id"], symbol=stock['symbol'], shares= -1 * shares, price=stock['price'])
        flash("Sold!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        rows = db.execute("SELECT symbol FROM transactions WHERE user_id=:user_id GROUP BY symbol HAVING SUM(shares) > 0", user_id=session["user_id"])
        return render_template("sell.html", symbols = [row["symbol"] for row in rows])



