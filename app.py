import os
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

###############################################################################
# FLASK APP
###############################################################################
app = Flask(__name__)
app.secret_key = "irgendein_sicherer_schluessel"

def get_db_connection():
    """
    Stellt eine Verbindung zur MySQL-DB her.
    Nutzt ENV-Variablen oder Standardwerte (host=db, user=root, pass=secret, db=dartdb).
    """
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASS", "secret"),
        database=os.environ.get("DB_NAME", "dartdb")
    )

###############################################################################
# DARTGAME-KLASSE
###############################################################################
class DartGame:
    def __init__(self, player_names, start_score=501, double_out=True):
        self.double_out = double_out
        self.players = []
        for pname in player_names:
            self.players.append({
                "name": pname,
                "score": start_score
            })
        self.current_player_index = 0
        self.current_dart = 1
        self.game_finished = False

        # Zähler für alle Würfe (inkl. Bust)
        self.total_throws = 0

    def throw_dart(self, base_value, multiplier=1):
        """
        Verarbeitet einen einzelnen Dart.
        - Erhöht total_throws
        - Prüft BUST
        - Prüft Double-Out
        - Handhabt 3-Dart-Runden
        """
        if self.game_finished:
            return False

        # Wurf-Zähler hoch
        self.total_throws += 1

        player = self.players[self.current_player_index]
        current_score = player["score"]
        dart_value = base_value * multiplier

        # BUST ?
        if (current_score - dart_value) < 0:
            self.round_bust()
            return False

        new_score = current_score - dart_value
        # Double-Out ?
        if new_score == 0:
            if self.double_out and multiplier != 2:
                self.round_bust()
                return False
            player["score"] = 0
            self.game_finished = True
            return False

        # Regulärer Treffer
        player["score"] = new_score

        # Dritter Dart oder Weiterwurf?
        if self.current_dart < 3:
            self.current_dart += 1
            return True
        else:
            self.next_player()
            return False

    def round_bust(self):
        self.current_dart = 1
        self.next_player()

    def next_player(self):
        """
        Falls nur ein Spieler existiert, bleibe bei current_player_index=0.
        Bei mehreren Spielern rotiere reihum.
        """
        self.current_dart = 1
        if len(self.players) > 1:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def get_current_player_name(self):
        return self.players[self.current_player_index]["name"]

    def is_finished(self):
        return self.game_finished

    def get_scores(self):
        return [(p["name"], p["score"]) for p in self.players]


###############################################################################
# GLOBALE SPIEL-INSTANCE
###############################################################################
dart_game_instance = None

###############################################################################
# LOGIN / REGISTER -> MYSQL
###############################################################################
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form.get("username")
        pw = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (uname,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user["password_hash"] == pw:
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            return "<h3>Falsches Login oder Benutzer unbekannt!</h3>"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form.get("username")
        pw = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Prüfen, ob Name existiert
        cursor.execute("SELECT user_id FROM users WHERE username=%s", (uname,))
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            conn.close()
            return "<h3>Benutzer existiert bereits!</h3>"

        # Unverschlüsselt (Demo!). Bitte in echt Passwörter hashen.
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (uname, pw))
        conn.commit()
        cursor.close()
        conn.close()

        return "<h3>Registrierung erfolgreich! <a href='/login'>Login</a></h3>"
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

###############################################################################
# STARTSEITE
###############################################################################
@app.route("/")
def index():
    return render_template("index.html")

###############################################################################
# START_GAME -> KONFIGURIERT EIN NEUES SPIEL (1-2 SPIELER)
###############################################################################
@app.route("/start_game", methods=["GET", "POST"])
def start_game():
    global dart_game_instance
    if "username" not in session:
        return "<h3>Bitte <a href='/login'>einloggen</a>!</h3>"

    if request.method == "POST":
        p1 = request.form.get("player1", "").strip()
        p2 = request.form.get("player2", "").strip()
        double_out = bool(request.form.get("double_out"))

        player_names = []
        if p1:
            player_names.append(p1)
        if p2:
            player_names.append(p2)

        if not player_names:
            return "<h3>Bitte mindestens einen Spieler angeben!</h3>"

        # DartGame instanziert
        dart_game_instance = DartGame(player_names, 501, double_out)
        return redirect(url_for("play_game"))

    return render_template("start_game.html")

###############################################################################
# PLAY_GAME -> DART-SPIEL ABLUF
###############################################################################
@app.route("/play_game", methods=["GET","POST"])
def play_game():
    global dart_game_instance
    if "username" not in session:
        return "<h3>Bitte <a href='/login'>einloggen</a>!</h3>"
    if not dart_game_instance:
        return "<h3>Kein Spiel aktiv. <a href='/start_game'>Neues Spiel</a></h3>"

    if dart_game_instance.is_finished():
        scores = dart_game_instance.get_scores()
        # game_finished -> Formular ausblenden
        return render_template("play_game.html",
                               scores=scores,
                               game_finished=True,
                               current_player="--",
                               current_dart=0,
                               total_throws=dart_game_instance.total_throws)

    # Wurf
    if request.method == "POST":
        base_val = int(request.form.get("base_value", 0))
        multiplier = int(request.form.get("multiplier", 1))
        dart_game_instance.throw_dart(base_val, multiplier)

    current_player = dart_game_instance.get_current_player_name()
    current_dart = dart_game_instance.current_dart
    scores = dart_game_instance.get_scores()

    return render_template("play_game.html",
                           scores=scores,
                           game_finished=False,
                           current_player=current_player,
                           current_dart=current_dart,
                           total_throws=dart_game_instance.total_throws)

###############################################################################
# RESET_GAME -> SPIEL ZURÜCKSETZEN
###############################################################################
@app.route("/reset_game")
def reset_game():
    global dart_game_instance
    dart_game_instance = None
    return "<h3>Spiel zurückgesetzt! <a href='/start_game'>Neues Spiel</a></h3>"

###############################################################################
# START FLASK
###############################################################################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
