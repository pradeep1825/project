# 🏦 Banking Management System
### HTML + CSS + JavaScript | Flask | MySQL

A simple, beginner-friendly full-stack banking web app — no React, no Bootstrap, no Node.js. Pure HTML/CSS/JS on the frontend, Flask APIs on the backend, MySQL for storage.

---

## 1. Project Overview

This app lets a customer:
1. Register an account (name, email, phone, password)
2. Login with email + password
3. Create one or more bank accounts (Savings/Current)
4. Deposit money
5. Withdraw money
6. Transfer funds to another account
7. Check balance
8. View transaction history
9. Logout

**TELUGU:** Ee project oka simple banking web application. Customer register avutadu, login avutadu, bank account create chesukuntadu, ఆ account లో deposit/withdraw/transfer చేస్తాడు, balance chuskuntadu, mariyu transaction history chuskuntadu. Anni operations Flask backend dwara MySQL database ki save avutayi.

**How the pieces talk to each other:**

```
Browser (HTML/CSS/JS)  --fetch() JSON-->  Flask (app.py)  --SQL queries-->  MySQL (banking_system DB)
        <---------------- JSON response -----------------        <---- rows ----
```

---

## 2. Project Folder Structure

```
banking_management_system/
│
├── app.py                  # Main Flask app - all routes & APIs
├── config.py                # MySQL connection settings
├── database.sql             # SQL script to create DB + tables
├── requirements.txt          # Python dependencies
│
├── templates/                # HTML pages (Flask Jinja templates)
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── deposit.html
│   ├── withdraw.html
│   ├── transfer.html
│   └── history.html
│
└── static/
    ├── css/
    │   └── style.css         # All styling, one shared file
    └── js/
        ├── common.js         # shared helper functions
        ├── register.js
        ├── login.js
        ├── dashboard.js
        ├── deposit.js
        ├── withdraw.js
        ├── transfer.js
        └── history.js
```

**TELUGU:** `templates/` lo anni HTML pages untayi. `static/css` lo styling, `static/js` lo prathi page ki separate JavaScript file undi (validation + Flask ki fetch calls kosam). `app.py` main backend file, `config.py` lo database connection details untayi, `database.sql` run cheste tables create avutayi.

---

## 3. MySQL Database Design (3 simple tables)

**customers** — registration/login info
| Column | Type |
|---|---|
| customer_id (PK) | INT AUTO_INCREMENT |
| full_name | VARCHAR(100) |
| email (UNIQUE) | VARCHAR(100) |
| phone | VARCHAR(15) |
| password | VARCHAR(255) — hashed |
| created_at | TIMESTAMP |

**accounts** — one customer can have many accounts
| Column | Type |
|---|---|
| account_id (PK) | INT AUTO_INCREMENT |
| customer_id (FK → customers) | INT |
| account_number (UNIQUE) | VARCHAR(20) |
| account_type | VARCHAR(20) |
| balance | DECIMAL(12,2) |
| created_at | TIMESTAMP |

**transactions** — every deposit/withdraw/transfer is logged here
| Column | Type |
|---|---|
| transaction_id (PK) | INT AUTO_INCREMENT |
| account_id (FK → accounts) | INT |
| transaction_type | VARCHAR(20) — DEPOSIT / WITHDRAW / TRANSFER_OUT / TRANSFER_IN |
| amount | DECIMAL(12,2) |
| balance_after | DECIMAL(12,2) |
| related_account | VARCHAR(20) — only for transfers |
| transaction_date | TIMESTAMP |

**TELUGU:** Moodu tables matrame: `customers` (login details), `accounts` (prathi customer ki account/s, balance), `transactions` (prathi deposit/withdraw/transfer ki oka row create avutundi — idi history chupinchadaniki use avutundi). Ee design chala beginner-friendly — interview lo easy ga explain cheyochu.

---

## 4. Flask Backend (app.py)

Two kinds of routes:
- **Page routes** (`/register`, `/login`, `/dashboard`, ...) → return HTML via `render_template()`
- **API routes** (`/api/register`, `/api/login`, `/api/deposit`, ...) → return JSON, called by JavaScript using `fetch()`

Key backend concepts used:
- `session` — keeps the customer "logged in" between requests (Flask's built-in cookie-based session)
- `generate_password_hash` / `check_password_hash` — passwords are **never** stored in plain text
- `login_required` — a custom decorator that blocks access to protected pages/APIs if not logged in
- Every money operation (deposit/withdraw/transfer) **updates `accounts.balance`** AND **inserts a row into `transactions`** in the same request — so the two tables never go out of sync

**TELUGU:** `app.py` lo rendu types routes untayi — page routes (HTML pages ivvadam kosam) mariyu API routes (JSON data ivvadam kosam, JS vాటిని call chestundi). Login state ni track cheyadaniki Flask `session` use chestham. Password ni direct ga DB lo save cheyakunda, hash chesi save chestham (security kosam). `login_required` ane decorator prathi protected page/API mundu login check chestundi.

---

## 5. HTML Pages

| Page | File | Purpose |
|---|---|---|
| Register | `templates/register.html` | New customer sign-up form |
| Login | `templates/login.html` | Email + password login form |
| Dashboard | `templates/dashboard.html` | Shows accounts, balances, quick action links, "Create Account" |
| Deposit | `templates/deposit.html` | Form to deposit money into an account |
| Withdraw | `templates/withdraw.html` | Form to withdraw money |
| Transfer | `templates/transfer.html` | Form to transfer money to another account |
| History | `templates/history.html` | Search account → shows balance + full transaction table |

All pages use Jinja's `{{ url_for(...) }}` to correctly link CSS/JS files, and share the same `style.css` for a consistent look.

---

## 6. CSS (static/css/style.css)

One single stylesheet used by every page — no framework, just plain CSS:
- `.navbar` — top blue navigation bar with Logout button
- `.card` / `.auth-wrapper` — centered form boxes for login/register/deposit/etc.
- `.accounts-grid` / `.account-card` — dashboard account cards
- `table` — styled transaction history table
- `.message-box` (`.message-success` / `.message-error`) — feedback banners
- `.error-text` — small red text under each invalid input

---

## 7. JavaScript

| File | Responsibility |
|---|---|
| `common.js` | `callApi()` (wraps `fetch`), `showMessage()`, `logout()`, email/phone validators, `formatMoney()` |
| `register.js` | Validates the registration form, calls `/api/register` |
| `login.js` | Validates login form, calls `/api/login`, redirects to dashboard |
| `dashboard.js` | Loads accounts (`/api/accounts`), handles "Create Account" modal |
| `deposit.js` | Validates + calls `/api/deposit` |
| `withdraw.js` | Validates + calls `/api/withdraw` |
| `transfer.js` | Validates + calls `/api/transfer` |
| `history.js` | Calls `/api/balance/<acc>` and `/api/transactions/<acc>`, renders the table |

Validation is done **before** calling Flask (empty fields, invalid email, amount ≤ 0, password mismatch, etc.) — this is basic frontend validation as required.

**TELUGU:** Prathi form submit ayye mundu JavaScript validation chestundi (empty fields, invalid email, negative amount, password mismatch లాంటివి). Validation pass ayithene, JS `fetch()` use chesi Flask API ki data pampistundi.

---

## 8. How Frontend Connects to Flask

1. User fills a form (e.g., deposit form) and clicks submit.
2. JavaScript's `submit` event listener runs, **prevents the default page reload** (`e.preventDefault()`), and validates inputs.
3. If valid, JS calls `callApi("/api/deposit", "POST", {...})` which internally does:
   ```js
   fetch(url, { method, headers: {"Content-Type": "application/json"}, body: JSON.stringify(data) })
   ```
4. Flask receives it at `@app.route("/api/deposit", methods=["POST"])`, reads it with `request.get_json()`.
5. Flask sends back a JSON response like `{"success": true, "new_balance": 5000.00}`.
6. JavaScript reads `result.data` and updates the page (shows a message, redirects, refreshes the account list) — **no page reload needed**.

---

## 9. How Flask Connects to MySQL

1. `config.py` defines `get_db_connection()` using `mysql.connector.connect(**DB_CONFIG)`.
2. Every API route in `app.py` calls `get_db_connection()` to open a fresh connection.
3. It runs SQL with a cursor: `cursor.execute("SELECT ... WHERE ... = %s", (value,))` — **parameterized queries** are used everywhere to prevent SQL injection.
4. For inserts/updates, `connection.commit()` saves the change; if something fails, `connection.rollback()` undoes it.
5. The connection and cursor are always closed in a `finally` block.

---

## 10. Complete Project Flow

```
1. REGISTER
   Browser (register.html) → JS validates → POST /api/register
   → Flask hashes password → INSERT INTO customers → returns success

2. LOGIN
   Browser (login.html) → JS validates → POST /api/login
   → Flask checks email + password hash → sets session["customer_id"]
   → redirect to /dashboard

3. DASHBOARD
   GET /api/accounts → Flask SELECTs all accounts for this customer_id
   → JS renders account cards (account number, balance, type)

4. CREATE ACCOUNT
   POST /api/create_account → Flask generates a random account_number
   → INSERT INTO accounts (balance = 0)

5. DEPOSIT
   POST /api/deposit {account_number, amount}
   → Flask verifies the account belongs to logged-in customer
   → UPDATE accounts SET balance = balance + amount
   → INSERT INTO transactions (type = DEPOSIT)

6. WITHDRAW
   POST /api/withdraw {account_number, amount}
   → Flask checks balance >= amount
   → UPDATE accounts SET balance = balance - amount
   → INSERT INTO transactions (type = WITHDRAW)

7. TRANSFER
   POST /api/transfer {from_account, to_account, amount}
   → Flask checks sender balance >= amount
   → UPDATE both accounts' balances
   → INSERT two transaction rows (TRANSFER_OUT for sender, TRANSFER_IN for receiver)

8. CHECK BALANCE / HISTORY
   GET /api/balance/<acc> and GET /api/transactions/<acc>
   → Flask returns balance + all transaction rows for that account
   → JS renders them in the history table

9. LOGOUT
   POST /api/logout → Flask clears session → redirect to /login
```

**TELUGU (Full Flow):** Customer register avutadu → login avutadu → dashboard lo account create chesukuntadu → deposit/withdraw/transfer operations chestadu → prathi operation account balance update chesi, transaction row insert chestundi → history page lo prathi operation chudochu → logout click cheste session clear ayyi login page ki veltadu.

---

## 11. How to Run the Project

### Step 1 — Install MySQL and create the database
```bash
mysql -u root -p < database.sql
```
(Or open the file in MySQL Workbench and run it.)

### Step 2 — Update database credentials
Open `config.py` and set your MySQL username/password:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "banking_system"
}
```

### Step 3 — Install Python dependencies
```bash
cd banking_management_system
pip install -r requirements.txt
```

### Step 4 — Run the Flask app
```bash
python app.py
```

### Step 5 — Open in browser
```
http://127.0.0.1:5000
```

**TELUGU:** Modata MySQL lo `database.sql` run chesi database create cheyandi. Tarvata `config.py` lo mee MySQL password pettandi. Tarvata `pip install -r requirements.txt` run chesi, `python app.py` run cheste, browser lo `http://127.0.0.1:5000` open cheyandi — appudu app run avutundi.

---

## 12. Quick Interview Talking Points

- **Why hashed passwords?** Plain text passwords are a security risk; `werkzeug.security` hashes them so even if the DB is leaked, passwords aren't exposed directly.
- **Why `session`?** HTTP is stateless — session (a signed cookie) lets Flask remember which customer is logged in across multiple requests.
- **Why parameterized SQL (`%s`)?** Prevents SQL injection attacks — user input is never directly concatenated into SQL strings.
- **Why JSON APIs + fetch instead of normal form POST?** Keeps the page from reloading, gives a smoother experience, and cleanly separates frontend (HTML/CSS/JS) from backend (Flask/MySQL) — this is the same pattern real-world REST APIs use.
- **Why both `accounts.balance` update AND a `transactions` insert on every operation?** `balance` is the fast "current state" lookup; `transactions` is the audit trail/history — a very common real banking pattern.

**TELUGU:** Interview lo ee points cheppochu — password hash enduku, session enduku, SQL injection prevent cheyadam ela, JSON API + fetch use cheyadam valla em advantage, balance + transactions rendu update cheyadam enduku (real banking systems lo kuda ide pattern follow avutundi).
