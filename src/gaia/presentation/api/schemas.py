# The API layer uses the DTOs from the application layer as its contract.
# In more complex apps, you might have API-specific models here for validation or formatting.
from gaia.application.dtos import PlanRequest
from gaia.domain.entities import Plan

# Re-exporting for clarity in the presentation layer
ApiPlanRequest = PlanRequest
ApiPlanResponse = Plan
