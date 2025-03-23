# game_logic.py
class DartGame:
    def __init__(self, player_names, start_score=501, double_out=True):
        self.double_out = double_out
        self.players = []
        for name in player_names:
            self.players.append({
                "name": name,
                "score": start_score
            })
        self.current_player_index = 0
        self.current_dart = 1
        self.game_finished = False

    def throw_dart(self, base_value, multiplier=1):
        if self.game_finished:
            return False

        current_player = self.players[self.current_player_index]
        current_score = current_player["score"]
        dart_value = base_value * multiplier

        # BUST?
        if (current_score - dart_value) < 0:
            self.round_bust()
            return False

        # Double-Out?
        new_score = current_score - dart_value
        if new_score == 0:
            if self.double_out and multiplier != 2:
                self.round_bust()
                return False
            else:
                current_player["score"] = 0
                self.game_finished = True
                return False

        # Regulärer Wurf
        current_player["score"] = new_score
        # Check: 3 Darts pro Runde
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
        self.current_dart = 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def get_current_player_name(self):
        return self.players[self.current_player_index]["name"]

    def is_finished(self):
        return self.game_finished

    def get_scores(self):
        # Liefert (Name, Score) für jeden Spieler
        return [(p["name"], p["score"]) for p in self.players]
