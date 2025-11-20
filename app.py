from flask import Flask, render_template, request, redirect, session
import json, os
from datetime import date

app = Flask(__name__)
app.secret_key = "HelloFaraday"

ADMIN_PASSWORD = "faraday"

DAILY_FILE = "./data/daily.json"
HISTORY_FILE = "./data/history.json"


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def require_login():
    return session.get("auth", False)


# ============================
# LOGIN
# ============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == ADMIN_PASSWORD:
            session["auth"] = True
            return redirect("/")
        else:
            return render_template("login.html", error=True)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ============================
# PÁGINA PRINCIPAL
# ============================
@app.route("/")
def index():
    if not require_login():
        return redirect("/login")

    daily = load_json(DAILY_FILE)
    return render_template("index.html", tarefas=daily)


# ============================
# ADICIONAR TAREFA
# ============================
@app.route("/add", methods=["POST"])
def add():
    if not require_login():
        return redirect("/login")

    daily = load_json(DAILY_FILE)
    daily.append(
        {
            "titulo": request.form.get("titulo"),
            "concluida": False,
        }
    )
    save_json(DAILY_FILE, daily)
    return redirect("/")


# ============================
# CONCLUIR TAREFA
# ============================
@app.route("/done/<int:i>")
def done(i):
    if not require_login():
        return redirect("/login")

    daily = load_json(DAILY_FILE)
    daily[i]["concluida"] = True
    save_json(DAILY_FILE, daily)
    return redirect("/")


# ============================
# FECHAR O DIA
# ============================
@app.route("/fechar")
def fechar():
    if not require_login():
        return redirect("/login")

    daily = load_json(DAILY_FILE)
    history = load_json(HISTORY_FILE)

    concluidas = [t["titulo"] for t in daily if t["concluida"]]

    history.append(
        {
            "data": str(date.today()),
            "tarefas_concluidas": len(concluidas),
            "tarefas_feitas": concluidas,
        }
    )

    save_json(HISTORY_FILE, history)
    save_json(DAILY_FILE, [])
    return redirect("/")


# ============================
# HISTÓRICO
# ============================
@app.route("/historico")
def historico():
    if not require_login():
        return redirect("/login")

    history = load_json(HISTORY_FILE)
    return render_template("history.html", history=history)


# ============================
# BOOTSTRAP
# ============================
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DAILY_FILE):
        save_json(DAILY_FILE, [])
    if not os.path.exists(HISTORY_FILE):
        save_json(HISTORY_FILE, [])
    app.run()
