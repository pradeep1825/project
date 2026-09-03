-- =========================================================
-- Banking Management System - Database Schema
-- =========================================================
-- Run this file in MySQL to create the database and tables.
-- Command: mysql -u root -p < database.sql
-- =========================================================

CREATE DATABASE IF NOT EXISTS banking_system;
USE banking_system;

-- ---------------------------------------------------------
-- Table 1: customers
-- Stores customer registration + login details
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    phone       VARCHAR(15)  NOT NULL,
    password    VARCHAR(255) NOT NULL,   -- stored as a hashed password
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- Table 2: accounts
-- Each customer can have one or more bank accounts
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    account_id      INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    account_number  VARCHAR(20) NOT NULL UNIQUE,
    account_type    VARCHAR(20) DEFAULT 'Savings',
    balance         DECIMAL(12,2) DEFAULT 0.00,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- Table 3: transactions
-- Stores every deposit / withdraw / transfer for history
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id    INT AUTO_INCREMENT PRIMARY KEY,
    account_id        INT NOT NULL,
    transaction_type  VARCHAR(20) NOT NULL,   -- DEPOSIT, WITHDRAW, TRANSFER_OUT, TRANSFER_IN
    amount             DECIMAL(12,2) NOT NULL,
    balance_after      DECIMAL(12,2) NOT NULL,
    related_account    VARCHAR(20),           -- used only for transfers
    transaction_date   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        ON DELETE CASCADE
);
