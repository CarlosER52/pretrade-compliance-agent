# src/agents/context_agent.py
import os
import json
from typing import Dict, Any
from openai import OpenAI
from jsonschema import validate, ValidationError

class ContextAgent:
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Carga el prompt desde el archivo markdown versionado."""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "extractor.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def analizar_contexto(self, orden: Dict[str, Any], contexto_cliente: Dict[str, Any]) -> Dict[str, Any]:
        """Llama al LLM y retorna el JSON validado."""
        
        # 1. Preparamos el input para el LLM
        input_data = {
            "orden": orden,
            "contexto_cliente": contexto_cliente
        }
        
        try:
            # 2. Llamada a la API (Forzando JSON)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt_template},
                    {"role": "user", "content": json.dumps(input_data)}
                ],
                response_format={"type": "json_object"}, # Fuerza al LLM a devolver JSON válido
                temperature=0.1 # Baja temperatura para minimizar alucinaciones
            )
            
            output_text = response.choices[0].message.content
            output_json = json.loads(output_text)
            
            # 3. Inyectamos el orden_id (el LLM no lo genera para evitar errores)
            output_json["orden_id"] = orden["orden_id"]
            
            # 4. Validación contra nuestro Schema (El "Contrato")
            self._validar_output(output_json)
            
            return output_json

        except Exception as e:
            # Manejo de errores: Si el agente falla, el orquestador lo reintentará o escalará.
            raise RuntimeError(f"Fallo en el Agente de Contexto: {str(e)}")

    def _validar_output(self, data: Dict[str, Any]):
        """Valida que el LLM no haya alucinado campos extra o tipos incorrectos."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "schemas", "analisis_contexto.schema.json"
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise ValueError(f"El agente devolvió datos inválidos: {e.message}")