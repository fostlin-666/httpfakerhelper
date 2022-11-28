#Yuxin Lin 2020/12/20

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from helpers import apology, login_required, lookup, usd
import json
import time


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    user_id = session['user_id']
    symbol = db.execute("select * from stock where user_id = ?;", user_id)

    total_value = 0
    for i in symbol:
        price = lookup(i['symbol'])
        db.execute("update stock set latest_price = ? where user_id = ? and symbol = ?;", price['price'], user_id, i['symbol'])
        total_value += i['latest_price'] * i['share']
    res = db.execute("select * from stock where user_id = ?;", user_id)
    cash = db.execute("select cash from users where id = ?;", user_id)
    total_value += cash[0]['cash']
    total_value = "{:.2f}".format(total_value)
    cash = "{:.2f}".format(cash[0]['cash'])


    return render_template('index.html', stock = res, total_value = total_value, cash = cash)




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock
    1. 通过接口查询价格
    2. 返回json中的价格*股数 = 买入价格
    3. 计算cash 是否够买入，不够的话返回错误信息，不够钱
    4. 够的话， cash - 买入价格，更新stock表格
    5. 如果stock用户持有该股为0，那就insert表格，如果已经有持有，那就update表格的share
    5. 写入 transaction 表格
    """
    if request.method == "POST":
        symbol = request.form.get("symbol")
        share = request.form.get("share")
        price = lookup(symbol)
        if price is None:
            return apology("请输入正确股票代码",403)

        else:
            priceTobuy = price['price'] * int(share)
            cash = db.execute("select cash from users where id = ?;", session['user_id'])
            if cash[0]['cash'] < priceTobuy:
                print('1')
                return apology("余额不足以购买，请联系老板充钱。",403)

            else:
                currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                print("2")
                db.execute("update users set cash = ? where id = ?;", cash[0]['cash'] - priceTobuy, session['user_id'])
                shareOwn = db.execute("select share from stock where user_id = ? and symbol = ?;", session['user_id'], symbol)
                if len(shareOwn) == 1:
                    db.execute("update stock set share = share + ? where user_id = ? and symbol = ?;", share, session['user_id'], symbol)
                    db.execute("insert into history (user_id, symbol, share, price, time) values (?,?,?,?,?);", session['user_id'], symbol, share, priceTobuy, currentTime)
                    flash("恭喜，{}公司的股票购入成功，股数为{}，购入价格为{}$，股票代码:{}。".format(price['name'], share, priceTobuy, symbol))
                    return redirect('/')
                else:
                    db.execute("insert into stock (user_id, symbol, name, share, latest_price) values (?,?,?,?,?);", session['user_id'],symbol,price['name'],share,price['price'])
                    db.execute("insert into history (user_id, symbol, share, price, time) values (?,?,?,?,?);", session['user_id'], symbol, share, priceTobuy, currentTime)
                    flash("恭喜，{}公司的股票购入成功，股数为{}，购入价格为{}$，股票代码:{}。".format(price['name'], share, priceTobuy, symbol))
                    return redirect('/')
    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock
    1. 查询用户已持有的股票，写入select
    2. 如果股数超过，则apology
    2. 获取选择的股票，api查询股票价格，股票价格*股数 = 卖出价格
    3. update user 表格 ， cash += 卖出价格
    4. flash（卖出成功），redirect to index
    """
    user_id = session['user_id']


    if request.method == "POST":
        sharesTosell = request.form.get("shares")
        symbolTosell = request.form.get("symbol")
        sharesOwn = db.execute("select share from stock where symbol = ? and user_id = ?;",symbolTosell, user_id)
        sharesTosell = int(sharesTosell)

        if sharesOwn[0]['share'] < sharesTosell:
            return apology("超过持有股数。")
        else:
            currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            price = lookup(symbolTosell)
            priceSold = sharesTosell * price['price']
            db.execute("update stock set share = share - ? where user_id = ? and symbol = ?;", sharesTosell, user_id, symbolTosell)
            db.execute("update users set cash = cash + ? where id = ?;", priceSold, user_id)
            db.execute("insert into history (user_id, symbol, share, price, time) values (?,?,?,?,?);", user_id, symbolTosell, -sharesTosell, priceSold, currentTime)
            flash("恭喜，{}公司的股票卖出成功，股数为{}，卖出价格为{}$，股票代码:{}。".format(price['name'], sharesTosell, priceSold, symbolTosell))
            return redirect("/")
    else:
        symbols = db.execute("select symbol from stock where user_id = ?", user_id)

        return render_template("sell.html",symbols = symbols)

@app.route("/history")
@login_required
def history():
    """Show history of transactions
    1. 选中session user_id 
    2. 查询用户的transaction表格，并写入html表格
    """
    user_id = session['user_id']

    history = db.execute('select * from history where user_id = ?', user_id)
    return render_template("history.html", history = history)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("请输入正确用户名。", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("请输入正确密码。", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("用户名或密码错误。", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("欢迎回来，{}".format(request.form.get("username")))
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")




@app.route("/register", methods=["GET","POST"])
def register():

    session.clear()
    """user register"""
    """
    1. 当请求方式是post时，检查两次密码输入是否一致，以及用户名是否已经注册过
    2. 如果检查通过，generate_password_hash.
    """
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("password-confirm"):
            return apology("请输入完整信息。", 403)

        row = db.execute("select username from users where username = ?;", request.form.get("username"))

        if len(row) != 0:
            return apology("该用户名已被注册。", 403)
        if request.form.get("password") != request.form.get("password-confirm"):
            return apology("两次密码不一致。",403)


        name = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        db.execute("insert into users (username, hash) values (:name, :password);", name = name, password = password)
        row = db.execute("select * from users where username = ?;", name)
        session["user_id"] = row[0]["id"]

        flash("注册成功！")
        return redirect("/")

    else:
        return render_template("register.html")

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
    """
    1.检查返回码是否等于200
    如果不等于，提示输入了错误的股票代码
    2. 如果是200 返回价格。
    """
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("股票代码错误。",403)
        symbol = request.form.get("symbol")
        res = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")


        if res.status_code == 200:
            dic = json.loads(res.text)
            latestPrice = dic["latestPrice"]
            companyName = dic["companyName"]
            result = companyName + ", " + symbol + " 目前价格为 $" + str(latestPrice) + "(每股)."
            return render_template("quote.html", result = result)
        else:
            return apology("股票代码错误", 403)
    else:
        return render_template("quote.html")





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
