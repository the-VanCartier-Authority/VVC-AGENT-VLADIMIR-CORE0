"""
VLADIMIR CORE 0 - Motor de Estado Corporativo
Centraliza y audita el estado del tablero y las métricas de rendimiento.
"""

class GameState:
    def __init__(self):
        # Datos de control de turnos y flujo
        self.turn = 0
        self.phase = "setup"  # setup, main, attack
        
        # Estado del tablero del Agente
        self.hand = []
        self.active = None
        self.bench = []
        self.prizes_remaining = 6
        self.energy_attached_this_turn = False
        
        # Estado del tablero del Oponente (Visibilidad según el simulador)
        self.opponent_active = None
        self.opponent_bench = []
        self.opponent_prizes_remaining = 6
        self.opponent_hand_count = 0
        
        # Métricas internas de auditoría
        self.estimated_skill_mu = 600.0
        self.estimated_skill_sigma = 200.0

    def update_from_dict(self, data: dict):
        """Actualización masiva de variables de estado."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
              
