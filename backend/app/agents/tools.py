SEARCH_VEHICLES_TOOL = {
    "type": "function",
    "name": "search_vehicles",
    "description": "Consulta veiculos disponiveis no CRM mockado da loja.",
    "parameters": {
        "type": "object",
        "properties": {
            "brand": {"type": "string"},
            "model": {"type": "string"},
            "max_price": {"type": "number"},
            "min_price": {"type": "number"},
            "transmission": {"type": "string"},
            "fuel": {"type": "string"},
            "status": {"type": "string"},
        },
        "additionalProperties": False,
    },
}


AGENT_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "car_sales_agent_response",
    "strict": False,
    "schema": {
        "type": "object",
        "properties": {
            "reply_text": {"type": "string"},
            "intent": {"type": "string"},
            "lead_status": {"type": "string"},
            "score": {"type": "integer"},
            "vehicle_interest": {"type": "string"},
            "budget_min": {"type": ["number", "null"]},
            "budget_max": {"type": ["number", "null"]},
            "payment_type": {"type": "string"},
            "trade_in_vehicle": {"type": ["string", "null"]},
            "interest_summary": {"type": "string"},
        },
        "required": ["reply_text"],
        "additionalProperties": True,
    },
}
