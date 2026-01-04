curl -X POST "http://127.0.0.1:8000/request_plan" \
-H "Content-Type: application/json" \
-d '{
  "context": {
    "agent_character_type": "soldier_leader",
    "mission_objective": "Defend the central base from intruders."
  },
  "definitions": {
    "character_types": [
      { "type_id": "player", "display_name": "Player", "threat_level": 10 },
      { "type_id": "soldier", "display_name": "Soldier", "threat_level": 3 }
    ],
    "item_types": [
      { "item_id": "item-guid-potion", "name": "Health Potion", "utility": 8 }
    ]
  },
  "available_goals": [
    {
      "name": "DefeatCharacterType",
      "description": "Defeats all characters of a specific type.",
      "parameters": { "characterTypeId": { "type": "string" } }
    },
    {
      "name": "CollectItem",
      "description": "Collects a specific item.",
      "parameters": { "itemId": { "type": "string" } }
    }
  ]
}'