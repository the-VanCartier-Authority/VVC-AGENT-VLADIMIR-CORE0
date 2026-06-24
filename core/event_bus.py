"""
VLADIMIR CORE 0 - Bus de Eventos Reactivo
Administra el ciclo de vida de los eventos e interrupciones del simulador.
"""

import sys

class EventBus:
    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_type: str, listener_callable):
        """Registra un módulo o habilidad para reaccionar a un evento específico."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener_callable)

    def publish(self, event_type: str, event_data: dict = None):
        """Despacha el evento a todos los oyentes registrados bajo auditoría."""
        if event_data is None:
            event_data = {}
            
        print(f"[EVENT_BUS] Dispatching: {event_type} | Data: {event_data}", file=sys.stderr)
        
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    listener(event_data)
                except Exception as e:
                    print(f"[CRITICAL EVENT ERROR] Fail in listener for {event_type}: {str(e)}", file=sys.stderr)
                  
