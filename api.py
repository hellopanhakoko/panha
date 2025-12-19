from flask import Flask, request, jsonify, render_template, redirect
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "prices.db"
ADMIN_TOKEN = "SUPERSECRET"

# -----------------------------
# Initialize DB
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    # Insert default items if table is empty
    c.execute("SELECT COUNT(*) FROM items")
    count = c.fetchone()[0]
    if count == 0:
        default_items = [
            ("mlbb", "86 Diamonds", 1.3),
            ("mlbb", "172 Diamonds", 3.99),
            ("mlbb", "257 Diamonds", 5.99),
            ("mlbb", "514 Diamonds", 11.99),
            ("mlbb", "Weekly Pass", 2.49),
            ("ff", "50 Diamonds", 0.03),
            ("ff", "120 Diamonds", 1.99),
            ("ff", "250 Diamonds", 3.99),
            ("ff", "500 Diamonds", 6.99),
            ("ff", "Weekly Pass", 2.49),
            ("ff", "100 Diamonds", 1.49),
            ("ff", "200 Diamonds", 3.49),
            ("ff", "300 Diamonds", 5.49)
        ]
        c.executemany("INSERT INTO items (game, name, price) VALUES (?, ?, ?)", default_items)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# API: Get all items
# -----------------------------
@app.route("/api/items", methods=["GET"])
def api_get_items():
    game = request.args.get("game")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if game:
        c.execute("SELECT id, name, price FROM items WHERE game=?", (game,))
        rows = c.fetchall()
        items = [{"id": r[0], "game": game, "name": r[1], "price": r[2]} for r in rows]
    else:
        c.execute("SELECT id, game, name, price FROM items")
        rows = c.fetchall()
        items = [{"id": r[0], "game": r[1], "name": r[2], "price": r[3]} for r in rows]

    conn.close()
    return jsonify({"success": True, "items": items})


# -----------------------------
# Admin HTML panel
# -----------------------------
@app.route("/api/admin", methods=["GET", "POST"])
def admin_panel():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("item_"):
                item_id = int(key.split("_")[1])
                try:
                    new_price = float(value)
                    c.execute("UPDATE items SET price=? WHERE id=?", (new_price, item_id))
                except:
                    pass
        conn.commit()

    c.execute("SELECT id, game, name, price FROM items")
    items = c.fetchall()
    conn.close()
    return render_template("admin_api.html", items=items)

# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
