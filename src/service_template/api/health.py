"""Liveness endpoint for load balancers and orchestrators."""

from fastapi import APIRouter

from service_template.api.schemas import HealthResponse

router = APIRouter(tags=["operations"])


@router.get(
    "/healthz",
    operation_id="getHealth",
    summary="Report that the service is running",
)
def get_health() -> HealthResponse:
    return HealthResponse(status="ok")
