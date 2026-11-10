# src/rules/rules_engine.py
import hashlib
import json
from typing import Dict, Any, List

def calcular_hash(data: Dict[str, Any]) -> str:
    """Helper para generar hashes de auditoría."""
    encoded = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()

class RulesEngine:
    def __init__(self, limites_config: Dict[str, Any]):
        # En producción, esto vendría de una BD o archivo de configuración
        self.limites = limites_config

    def evaluar_todas(self, orden: Dict[str, Any], contexto_cliente: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta las 4 reglas duras y devuelve el artefacto de validación."""
        resultados = []
        
        # R1: Límite de posición
        resultados.append(self._r1_posicion(orden, contexto_cliente))
        
        # R2: Lista restringida (Sanctions / Watchlist)
        resultados.append(self._r2_lista_restringida(orden))
        
        # R3: Concentración sectorial
        resultados.append(self._r3_concentracion(orden, contexto_cliente))
        
        # R4: Wash trading (Patrón de compra/venta cruzada)
        resultados.append(self._r4_wash_trading(orden, contexto_cliente))

        fallos_total = sum(1 for r in resultados if r["resultado"] == "fail")

        return {
            "orden_id": orden["orden_id"],
            "reglas": resultados,
            "fallos_total": fallos_total,
            "hash_evaluacion": calcular_hash({"orden": orden, "resultados": resultados})
        }

    def _r1_posicion(self, orden: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, str]:
        """R1: Verifica que la posición resultante no exceda el límite permitido."""
        posicion_actual = contexto.get("posicion_actual", 0)
        nueva_posicion = posicion_actual + orden["cantidad"]
        limite = self.limites.get(orden["instrumento"], {}).get("limite_posicion", 1000)
        
        if nueva_posicion > limite:
            return {
                "regla_id": "R1_posicion",
                "resultado": "fail",
                "detalle": f"Posición resultante ({nueva_posicion}) excede el límite ({limite}) para {orden['instrumento']}."
            }
        return {
            "regla_id": "R1_posicion",
            "resultado": "pass",
            "detalle": f"Posición resultante ({nueva_posicion}) dentro del límite."
        }

    def _r2_lista_restringida(self, orden: Dict[str, Any]) -> Dict[str, str]:
        """R2: Verifica si el instrumento o cliente está en listas de restricción."""
        # Simulamos una lista de restricciones (ej. sanciones, MNPI)
        lista_restringida = ["BABA", "NIO", "RUSAL"] 
        
        if orden["instrumento"] in lista_restringida:
            return {
                "regla_id": "R2_lista_restringida",
                "resultado": "fail",
                "detalle": f"El instrumento {orden['instrumento']} está en la lista de restricciones."
            }
        return {
            "regla_id": "R2_lista_restringida",
            "resultado": "pass",
            "detalle": "Instrumento no restringido."
        }

    def _r3_concentracion(self, orden: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, str]:
        """R3: Verifica la concentración por sector."""
        sector = self.limites.get(orden["instrumento"], {}).get("sector", "Tech")
        exposicion_sector_actual = contexto.get("exposicion_sector", 0.0) # Porcentaje 0-100
        nueva_exposicion = exposicion_sector_actual + (contexto.get("valor_orden", 0) / contexto.get("valor_portafolio", 1) * 100)
        
        limite_sector = self.limites.get("limites_sector", {}).get(sector, 25.0) # 25% default
        
        if nueva_exposicion > limite_sector:
            return {
                "regla_id": "R3_concentracion",
                "resultado": "fail",
                "detalle": f"Exposición al sector {sector} ({nueva_exposicion:.2f}%) excede el límite ({limite_sector}%)."
            }
        return {
            "regla_id": "R3_concentracion",
            "resultado": "pass",
            "detalle": f"Exposición al sector {sector} ({nueva_exposicion:.2f}%) aceptable."
        }

    def _r4_wash_trading(self, orden: Dict[str, Any], contexto: Dict[str, Any]) -> Dict[str, str]:
        """R4: Detecta patrones de wash trading (ej. comprar y vender el mismo activo en poco tiempo)."""
        historial_reciente = contexto.get("historial_ordenes_24h", [])
        
        for h in historial_reciente:
            if h["instrumento"] == orden["instrumento"] and h["tipo"] != orden["tipo"]:
                return {
                    "regla_id": "R4_wash_trading",
                    "resultado": "fail",
                    "detalle": f"Posible wash trading: Se detectó una orden {h['tipo']} de {h['instrumento']} en las últimas 24h."
                }
        
        return {
            "regla_id": "R4_wash_trading",
            "resultado": "pass",
            "detalle": "Sin patrones de wash trading detectados."
        }