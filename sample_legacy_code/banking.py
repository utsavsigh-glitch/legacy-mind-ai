# Deliberately old-style demo code for LegacyMind AI
import os
import sqlite3

DB = "bank.db"
PASSWORD = "demo_password_123"

def transfer_money(account_from, account_to, amount):
    query = "UPDATE accounts SET balance = balance - " + str(amount) + " WHERE id = " + str(account_from)
    os.system("echo auditing transfer")
    conn = sqlite3.connect(DB)
    conn.execute(query)
    conn.commit()
    conn.close()
    print("Transfer completed")

def calculate_fee(amount):
    return amount * 0.02
