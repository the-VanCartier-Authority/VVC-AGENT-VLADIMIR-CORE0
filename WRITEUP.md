# Vladimir: Risk-Aware Hierarchical Decision-Making for Pokémon TCG Agents

## Resumen

Presentamos Vladimir, un agente de juego para Pokémon TCG diseñado para tomar decisiones robustas bajo información parcial, azar y un presupuesto estricto de tiempo. El sistema combina validación de entrada, representación estructurada del tablero y una política heurística jerárquica. La política no intenta enumerar todas las líneas posibles. En su lugar, prioriza primero la legalidad y la supervivencia, después el progreso táctico y finalmente la ventaja posicional.

La motivación de este diseño es práctica. En el simulador cabt, cada observación contiene los registros de eventos, el estado visible del tablero y una lista de opciones legales. Durante la fase inicial no existe estado de partida ni selección, porque el agente debe devolver el mazo. Durante el juego, la acción se expresa mediante índices de las opciones disponibles.[1]

## Problema de diseño

Un agente aleatorio puede completar partidas y demostrar que la integración técnica funciona, pero no representa una estrategia de juego. También puede desperdiciar ataques, no desarrollar la banca o ignorar estados negativos del Pokémon activo. Un agente que usa búsqueda exhaustiva puede superar el presupuesto de tiempo o depender demasiado de información que no está disponible.

Vladimir adopta una posición intermedia. El entorno restringe las acciones a opciones legales. El agente solo necesita ordenar esas opciones de acuerdo con objetivos visibles y consistentes. Esta separación reduce el riesgo de errores de interfaz y permite explicar cada decisión.

## Arquitectura

| Capa | Responsabilidad | Principio |
|---|---|---|
| Validación | Leer un mazo de 60 cartas y controlar el formato de respuesta | La robustez precede a la optimización |
| Estado | Separar jugador propio y rival y conservar el tablero visible | No confundir información propia con información del oponente |
| Evaluación | Puntuar cada opción legal con señales de progreso y riesgo | Preferir una función interpretable |
| Selección | Devolver las mejores opciones dentro de `maxCount` | Mantener tiempo y legalidad bajo control |
| Registro | Emitir errores solo en modo de depuración | No contaminar la ejecución competitiva |

La implementación usa el índice `yourIndex` cuando está presente. Si el campo no está disponible, aplica un valor conservador por defecto y evita asumir que la información del rival es la propia.

## Política de decisión

La política asigna mayor valor a las acciones que aumentan el progreso inmediato, como ataques, daño o una oportunidad de conseguir un nocaut. También recompensa la evolución, el acceso a recursos, la preparación de banca y la asignación de energía. La retirada o el cambio reciben valor adicional cuando el Pokémon activo presenta un estado negativo.

Desde el Ataque 3, la función conceptual es:

```text
V(a) = progreso(a) + desarrollo(a) + recursos(a) + recuperación(a)
       - exposición(a) - desperdicio(a) - pasividad(a)
```

Los términos se implementan como señales explícitas. Ataque, daño y nocaut reciben prioridad alta. Evolución, búsqueda y robo de cartas reciben prioridad intermedia. Pasar, cancelar o descartar sin una señal de beneficio reciben una penalización. Cuando dos opciones tienen el mismo valor, el índice original actúa como desempate estable; no se usa aleatoriedad.

La implementación combina el mapeo oficial de `OptionType` con una capa textual de respaldo. Por ejemplo, `ATTACK=13`, `PLAY=7`, `EVOLVE=9`, `RETREAT=12` y `END=14`. Para selecciones de cartas, el agente resuelve la referencia mediante `area`, `index` y `playerIndex`, y consulta el CSV oficial de 1,267 cartas. Usa características disponibles como etapa, HP y coste de retirada. Cuando una observación no expone suficiente información, conserva una contribución neutra en vez de inventar datos.

## Gestión de incertidumbre

La información del rival es parcial. Por esta razón, Vladimir no asigna un valor exacto a cartas ocultas. En su lugar, utiliza señales robustas: número de cartas visibles, tamaño de la banca, presencia del Pokémon activo, estados negativos y disponibilidad de recursos. Si un campo no existe, la función devuelve una contribución neutra. Esta decisión evita que una observación incompleta produzca una excepción o una acción inválida.

La política también mantiene un modo de fallo seguro. Si la evaluación genera una excepción, devuelve los primeros índices legales disponibles. El fallback no intenta ser inteligente; solo evita romper el contrato de la API. El mazo de respaldo contiene 60 IDs y no supera cuatro copias de un mismo ID.

La versión V6 añade una hipótesis de tempo. En los dos primeros turnos, jugar, unir energía y evolucionar reciben una bonificación moderada para evitar pasividad durante el desarrollo. Si el daño visible alcanza la vida del activo rival, el ataque recibe una bonificación fuerte por nocaut. Cuando queda un solo premio, la política favorece el cierre legal de la partida. Esta modificación busca evitar una regla rígida de “atacar siempre” y adaptar la prioridad a la fase y al estado de la partida.

## Hipótesis y evaluación

La hipótesis principal es que una política jerárquica y determinista mejora la estabilidad respecto a la selección aleatoria, especialmente en situaciones repetidas de desarrollo inicial y selección de recursos. La progresión implementada permite evaluar esta hipótesis con tres comparaciones:

| Comparación | Métrica principal | Pregunta |
|---|---|---|
| Aleatorio frente a Vladimir | Rating medio y tasa de victoria | ¿La política básica aporta ventaja sobre una línea base sin estrategia? |
| Pesos conservadores frente a agresivos | Rating, premios y duración de partida | ¿Cuándo conviene cerrar la partida y cuándo conviene desarrollar? |
| Catálogo de cartas frente a señales genéricas | Rating y errores por decisión | ¿Cuánto valor adicional aporta el conocimiento explícito de cartas? |

Cada variante debe ejecutarse contra la misma colección de mazos y oponentes. Además del rating, conviene registrar la legalidad de las respuestas, el tiempo de decisión, los errores, los turnos hasta el primer ataque, el número de Pokémon en banca y los cambios de estado del activo. Estas métricas permiten distinguir una mejora estratégica de una simple variación causada por el azar.

## Diseño del mazo

El paquete incluye un mazo de prueba legal para validar la interfaz y el empaquetado. No lo presentamos como un mazo competitivo óptimo: la entrega de simulación obtuvo 191.6 y sirve como evidencia de integración, no como prueba causal de superioridad. La composición debe evaluarse como una fase independiente, justificando cada familia por su función: atacantes principales, líneas de evolución, energía, búsqueda, robo, recuperación y respuestas a estados negativos.

Esta separación entre infraestructura y diseño del mazo es intencional. Un mazo válido permite reproducir el agente. La optimización del mazo debe ser una fase experimental independiente, porque mezclar ambos cambios impide saber si una mejora proviene de la política o de la composición de cartas.

## Conclusión

Vladimir transforma un agente de integración mínima en una política explicable para decisiones bajo incertidumbre. Su contribución principal no es una búsqueda costosa, sino una arquitectura que mantiene juntas cuatro propiedades: legalidad, tiempo acotado, interpretación estratégica y uso reproducible de datos oficiales. El resultado es una base para calibrar pesos y evaluar hipótesis de juego con experimentos controlados.

El resultado de la categoría de simulación debe interpretarse con cautela: 191.6 es la puntuación del envío competitivo registrado y no permite atribuir por sí sola una mejora a cada cambio posterior del notebook. La propuesta estratégica documenta de forma auditable la transición desde una integración mínima hacia una política jerárquica, el uso del catálogo oficial, las pruebas reproducibles y las limitaciones que todavía deben medirse.

## Referencias

[1] PTCGABC cabt Engine Documentation  
[2] The Pokémon Company - PTCG AI Battle Challenge Simulation  
[3] The Pokémon Company - PTCG AI Battle Challenge Strategy
