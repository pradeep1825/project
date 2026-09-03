"""
app.py
-------
Main Flask application for the Banking Management System.

This file contains:
1. Page routes  -> return HTML pages (render_template)
2. API routes   -> return JSON data (used by JavaScript via fetch())

TELUGU: Idi maa main Flask file. Rendu type routes untayi -
1) Page routes - HTML pages chupistayi
2) API routes  - JSON data pampistayi, JS fetch() vాటిని use chesi
   data teesukuni page meeda chupistundi.
"""

import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from config import get_db_connection

app = Flask(__name__)
app.secret_key = "change_this_secret_key_in_production"  # needed for session/login


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def generate_account_number():
    """Creates a random 10 digit account number, e.g. 4839201567"""
    return str(random.randint(1000000000, 9999999999))


def login_required(func):
    """A simple decorator that blocks access if the customer is not logged in."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "customer_id" not in session:
            # If it's an API call, return JSON error; else redirect to login page
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Please login first."}), 401
            return redirect(url_for("login_page"))
        return func(*args, **kwargs)
    return wrapper


# =========================================================
# PAGE ROUTES  (return HTML templates)
# =========================================================

@app.route("/")
def home():
    if "customer_id" in session:
        return redirect(url_for("dashboard_page"))
    return redirect(url_for("login_page"))


@app.route("/register")
def register_page():
    return render_template("register.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html", name=session.get("full_name"))


@app.route("/deposit")
@login_required
def deposit_page():
    return render_template("deposit.html")


@app.route("/withdraw")
@login_required
def withdraw_page():
    return render_template("withdraw.html")


@app.route("/transfer")
@login_required
def transfer_page():
    return render_template("transfer.html")


@app.route("/history")
@login_required
def history_page():
    return render_template("history.html")


# =========================================================
# API ROUTES  (return JSON, called by JavaScript fetch())
# =========================================================

# ---------------------------------------------------------
# 1. CUSTOMER REGISTRATION
# ---------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")

    if not full_name or not email or not phone or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"success": False, "message": "Database connection error."}), 500

    cursor = connection.cursor()
    try:
        # Check if email already exists
        cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Email already registered."}), 400

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO customers (full_name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (full_name, email, phone, hashed_password)
        )
        connection.commit()
        return jsonify({"success": True, "message": "Registration successful! Please login."})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# 2. CUSTOMER LOGIN
# ---------------------------------------------------------
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    connection = get_db_connection()
    if connection is None:
        return jsonify({"success": False, "message": "Database connection error."}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        customer = cursor.fetchone()

        if not customer or not check_password_hash(customer["password"], password):
            return jsonify({"success": False, "message": "Invalid email or password."}), 401

        # Save login info in session
        session["customer_id"] = customer["customer_id"]
        session["full_name"] = customer["full_name"]
        session["email"] = customer["email"]

        return jsonify({"success": True, "message": "Login successful!"})
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# 9. LOGOUT
# ---------------------------------------------------------
@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})


# ---------------------------------------------------------
# 3. CREATE BANK ACCOUNT
# ---------------------------------------------------------
@app.route("/api/create_account", methods=["POST"])
@login_required
def api_create_account():
    data = request.get_json()
    account_type = data.get("account_type", "Savings")
    customer_id = session["customer_id"]

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        account_number = generate_account_number()
        cursor.execute(
            "INSERT INTO accounts (customer_id, account_number, account_type, balance) VALUES (%s, %s, %s, %s)",
            (customer_id, account_number, account_type, 0.00)
        )
        connection.commit()
        return jsonify({
            "success": True,
            "message": "Account created successfully!",
            "account_number": account_number
        })
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# Get all accounts belonging to logged-in customer
# ---------------------------------------------------------
@app.route("/api/accounts", methods=["GET"])
@login_required
def api_get_accounts():
    customer_id = session["customer_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT account_number, account_type, balance, created_at FROM accounts WHERE customer_id = %s",
            (customer_id,)
        )
        accounts = cursor.fetchall()
        # Convert Decimal/datetime to string for JSON
        for acc in accounts:
            acc["balance"] = float(acc["balance"])
            acc["created_at"] = str(acc["created_at"])
        return jsonify({"success": True, "accounts": accounts})
    finally:
        cursor.close()
        connection.close()


def _get_account_for_customer(cursor, account_number, customer_id):
    """Helper: fetch an account row only if it belongs to this customer."""
    cursor.execute(
        "SELECT * FROM accounts WHERE account_number = %s AND customer_id = %s",
        (account_number, customer_id)
    )
    return cursor.fetchone()


# ---------------------------------------------------------
# 4. DEPOSIT MONEY
# ---------------------------------------------------------
@app.route("/api/deposit", methods=["POST"])
@login_required
def api_deposit():
    data = request.get_json()
    account_number = data.get("account_number", "").strip()
    amount = data.get("amount")
    customer_id = session["customer_id"]

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid amount."}), 400

    if amount <= 0:
        return jsonify({"success": False, "message": "Amount must be greater than zero."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        account = _get_account_for_customer(cursor, account_number, customer_id)
        if not account:
            return jsonify({"success": False, "message": "Account not found."}), 404

        new_balance = float(account["balance"]) + amount

        cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s",
                        (new_balance, account["account_id"]))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after) VALUES (%s, %s, %s, %s)",
            (account["account_id"], "DEPOSIT", amount, new_balance)
        )
        connection.commit()
        return jsonify({"success": True, "message": "Deposit successful!", "new_balance": new_balance})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# 5. WITHDRAW MONEY
# ---------------------------------------------------------
@app.route("/api/withdraw", methods=["POST"])
@login_required
def api_withdraw():
    data = request.get_json()
    account_number = data.get("account_number", "").strip()
    amount = data.get("amount")
    customer_id = session["customer_id"]

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid amount."}), 400

    if amount <= 0:
        return jsonify({"success": False, "message": "Amount must be greater than zero."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        account = _get_account_for_customer(cursor, account_number, customer_id)
        if not account:
            return jsonify({"success": False, "message": "Account not found."}), 404

        current_balance = float(account["balance"])
        if amount > current_balance:
            return jsonify({"success": False, "message": "Insufficient balance."}), 400

        new_balance = current_balance - amount

        cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s",
                        (new_balance, account["account_id"]))
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after) VALUES (%s, %s, %s, %s)",
            (account["account_id"], "WITHDRAW", amount, new_balance)
        )
        connection.commit()
        return jsonify({"success": True, "message": "Withdrawal successful!", "new_balance": new_balance})
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# 6. FUND TRANSFER
# ---------------------------------------------------------
@app.route("/api/transfer", methods=["POST"])
@login_required
def api_transfer():
    data = request.get_json()
    from_account_number = data.get("from_account", "").strip()
    to_account_number = data.get("to_account", "").strip()
    amount = data.get("amount")
    customer_id = session["customer_id"]

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid amount."}), 400

    if amount <= 0:
        return jsonify({"success": False, "message": "Amount must be greater than zero."}), 400

    if from_account_number == to_account_number:
        return jsonify({"success": False, "message": "Cannot transfer to the same account."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # sender account must belong to the logged in customer
        from_account = _get_account_for_customer(cursor, from_account_number, customer_id)
        if not from_account:
            return jsonify({"success": False, "message": "Sender account not found."}), 404

        cursor.execute("SELECT * FROM accounts WHERE account_number = %s", (to_account_number,))
        to_account = cursor.fetchone()
        if not to_account:
            return jsonify({"success": False, "message": "Receiver account not found."}), 404

        if amount > float(from_account["balance"]):
            return jsonify({"success": False, "message": "Insufficient balance."}), 400

        sender_new_balance = float(from_account["balance"]) - amount
        receiver_new_balance = float(to_account["balance"]) + amount

        # Update both balances
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s",
                        (sender_new_balance, from_account["account_id"]))
        cursor.execute("UPDATE accounts SET balance = %s WHERE account_id = %s",
                        (receiver_new_balance, to_account["account_id"]))

        # Record two transaction rows (one for each side)
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, related_account) "
            "VALUES (%s, %s, %s, %s, %s)",
            (from_account["account_id"], "TRANSFER_OUT", amount, sender_new_balance, to_account_number)
        )
        cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount, balance_after, related_account) "
            "VALUES (%s, %s, %s, %s, %s)",
            (to_account["account_id"], "TRANSFER_IN", amount, receiver_new_balance, from_account_number)
        )

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Transfer successful!",
            "new_balance": sender_new_balance
        })
    except Exception as e:
        connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# 7. CHECK BALANCE
# ---------------------------------------------------------
@app.route("/api/balance/<account_number>", methods=["GET"])
@login_required
def api_balance(account_number):
    customer_id = session["customer_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        account = _get_account_for_customer(cursor, account_number, customer_id)
        if not account:
            return jsonify({"success": False, "message": "Account not found."}), 404
        return jsonify({"success": True, "balance": float(account["balance"])})
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------------------------
# 8. TRANSACTION HISTORY
# ---------------------------------------------------------
@app.route("/api/transactions/<account_number>", methods=["GET"])
@login_required
def api_transactions(account_number):
    customer_id = session["customer_id"]
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        account = _get_account_for_customer(cursor, account_number, customer_id)
        if not account:
            return jsonify({"success": False, "message": "Account not found."}), 404

        cursor.execute(
            "SELECT transaction_type, amount, balance_after, related_account, transaction_date "
            "FROM transactions WHERE account_id = %s ORDER BY transaction_date DESC",
            (account["account_id"],)
        )
        rows = cursor.fetchall()
        for r in rows:
            r["amount"] = float(r["amount"])
            r["balance_after"] = float(r["balance_after"])
            r["transaction_date"] = str(r["transaction_date"])

        return jsonify({"success": True, "transactions": rows})
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    app.run(debug=True)
