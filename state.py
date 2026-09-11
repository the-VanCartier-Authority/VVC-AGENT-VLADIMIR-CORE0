from __future__
class GameState:
    def __init__(self) -> None:
        self.turn = 0
        self.players: list[dict] = []
        self.your_index = 0
        self.stadium = None
        self.logs: list = []
        self.current: dict = {}
        self.select: dict = {}
    def update_from_dict(self, obs_dict: dict) -> None:
        self.logs = obs_dict.get("logs") or self.logs
        self.current = obs_dict.get("current") or {}
        self.select = obs_dict.get("select") or {}
        self.turn = self.current.get("turn", self.turn)
        self.players = self.current.get("players") or self.players
        self.your_index = self.current.get("yourIndex", self.current.get("player", self.your_index))
        self.stadium = self.current.get("stadium", self.stadium)
    def me(self) -> dict:
        if not self.players: return {}
        idx = self.your_index if 0 <= self.your_index < len(self.players) else 0
        return self.players[idx] or {}
    def opponent(self) -> dict:
        if len(self.players) < 2: return {}
        idx = self.your_index if 0 <= self.your_index < len(self.players) else 0
        return self.players[1 - idx] or {}
    @staticmethod
    def _card(value):
        if isinstance(value, list): return value[0] if value else {}
        return value or {}
    def active(self, player: dict | None = None) -> dict: return self._card((player or self.me()).get("active"))
    def bench(self, player: dict | None = None) -> list[dict]: return (player or self.me()).get("bench") or []
    def hand(self, player: dict | None = None) -> list[dict]: return (player or self.me()).get("hand") or []
    def card_from_option(self, option: dict) -> dict:
        if not isinstance(option, dict): return {}
        direct = option.get("card")
        if isinstance(direct, dict): return direct
        player_index = option.get("playerIndex", self.your_index)
        try: player = self.players[int(player_index)]
        except (IndexError, TypeError, ValueError): player = self.me()
        area = option.get("area")
        index = option.get("index")
        if option.get("type") == 7 and index is not None: area = 2
        try: index = int(index)
        except (TypeError, ValueError): return {}
        area_key = str(getattr(area, "value", area)).lower()
        if area_key in ("2", "hand"): cards = player.get("hand") or []
        elif area_key in ("4", "active"): cards = player.get("active") or []
        elif area_key in ("5", "bench"): cards = player.get("bench") or []
        elif area_key in ("3", "discard"): cards = player.get("discard") or []
        else: cards = []
        return self._card(cards[index]) if 0 <= index < len(cards) else {}
