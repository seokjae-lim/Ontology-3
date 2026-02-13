from app.models import RequestStatus

TRANSITIONS = {
    RequestStatus.Requested: {RequestStatus.Approved, RequestStatus.Rejected, RequestStatus.Cancelled},
    RequestStatus.Approved: {RequestStatus.Executed, RequestStatus.Cancelled},
    RequestStatus.Executed: {RequestStatus.Closed},
}


def transition_allowed(current: RequestStatus, target: RequestStatus) -> bool:
    return target in TRANSITIONS.get(current, set())
