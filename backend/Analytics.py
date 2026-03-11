from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from database import get_session
from models import Campaign, Target, TrackingEvent
from routers.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ─── helpers ────────────────────────────────────────────────────────────────

def _campaign_stats(campaign_id: int, session: Session) -> dict:
    """Compute full stats for a single campaign."""

    total = session.exec(
        select(func.count(Target.id)).where(Target.campaign_id == campaign_id)
    ).one()

    if total == 0:
        return {
            "campaign_id": campaign_id,
            "total_targets": 0,
            "opened": 0,  "open_rate": 0.0,
            "clicked": 0, "click_rate": 0.0,
            "reported": 0,"report_rate": 0.0,
            "training_completed": 0, "training_completion_rate": 0.0,
        }

    uuids = list(session.exec(
        select(Target.tracking_uuid).where(Target.campaign_id == campaign_id)
    ).all())

    def unique_targets_with_event(event_type: str) -> int:
        if not uuids:
            return 0
        return session.exec(
            select(func.count(func.distinct(TrackingEvent.tracking_uuid))).where(
                TrackingEvent.tracking_uuid.in_(uuids),
                TrackingEvent.event_type == event_type,
            )
        ).one() or 0

    opened   = unique_targets_with_event("open")
    clicked  = unique_targets_with_event("click")
    reported = unique_targets_with_event("report")

    training_completed = session.exec(
        select(func.count(Target.id)).where(
            Target.campaign_id == campaign_id,
            Target.training_completed == True,
        )
    ).one()

    def rate(n): return round((n / total) * 100, 1)

    return {
        "campaign_id":              campaign_id,
        "total_targets":            total,
        "opened":                   opened,
        "open_rate":                rate(opened),
        "clicked":                  clicked,
        "click_rate":               rate(clicked),
        "reported":                 reported,
        "report_rate":              rate(reported),
        "training_completed":       training_completed,
        "training_completion_rate": rate(training_completed),
    }


# ─── routes ─────────────────────────────────────────────────────────────────

@router.get("/summary")
def platform_summary(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Top-level KPI cards for the dashboard header."""
    total_campaigns  = session.exec(select(func.count(Campaign.id))).one()
    active_campaigns = session.exec(
        select(func.count(Campaign.id)).where(Campaign.status == "active")
    ).one()
    total_targets = session.exec(select(func.count(Target.id))).one()
    total_clicks  = session.exec(
        select(func.count(func.distinct(TrackingEvent.tracking_uuid))).where(
            TrackingEvent.event_type == "click"
        )
    ).one()
    total_training = session.exec(
        select(func.count(Target.id)).where(Target.training_completed == True)
    ).one()

    click_rate    = round((total_clicks / total_targets * 100), 1) if total_targets else 0.0
    training_rate = round((total_training / total_targets * 100), 1) if total_targets else 0.0

    return {
        "total_campaigns":       total_campaigns,
        "active_campaigns":      active_campaigns,
        "total_targets":         total_targets,
        "overall_click_rate":    click_rate,
        "overall_training_rate": training_rate,
    }


@router.get("/campaigns")
def all_campaigns_analytics(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Stats for every campaign — used by the analytics overview table/chart."""
    campaigns = session.exec(select(Campaign)).all()
    results = []
    for c in campaigns:
        stats = _campaign_stats(c.id, session)
        stats["campaign_name"]   = c.name
        stats["campaign_status"] = c.status
        stats["campaign_type"]   = c.campaign_type
        results.append(stats)
    return results


@router.get("/campaigns/{campaign_id}")
def single_campaign_analytics(
    campaign_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Full stats + per-target breakdown for one campaign."""
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    stats = _campaign_stats(campaign_id, session)
    stats["campaign_name"]   = campaign.name
    stats["campaign_status"] = campaign.status
    stats["campaign_type"]   = campaign.campaign_type

    targets = session.exec(
        select(Target).where(Target.campaign_id == campaign_id)
    ).all()

    target_rows = []
    for t in targets:
        events = session.exec(
            select(TrackingEvent)
            .where(TrackingEvent.tracking_uuid == t.tracking_uuid)
            .order_by(TrackingEvent.timestamp)
        ).all()

        event_types = {e.event_type for e in events}
        first_event = events[0].timestamp.isoformat() if events else None

        target_rows.append({
            "target_id":          t.id,
            "name":               f"{t.first_name} {t.last_name}",
            "email":              t.email,
            "department":         t.department,
            "opened":             "open"   in event_types,
            "clicked":            "click"  in event_types,
            "reported":           "report" in event_types,
            "training_completed": t.training_completed,
            "first_event_at":     first_event,
            "total_events":       len(events),
        })

    stats["targets"] = target_rows
    return stats


@router.get("/departments")
def department_breakdown(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Click + training rates grouped by department (across all campaigns)."""
    departments = session.exec(select(Target.department).distinct()).all()

    rows = []
    for dept in departments:
        targets = session.exec(
            select(Target).where(Target.department == dept)
        ).all()
        total = len(targets)
        if total == 0:
            continue

        uuids = [t.tracking_uuid for t in targets]
        clicks = session.exec(
            select(func.count(func.distinct(TrackingEvent.tracking_uuid))).where(
                TrackingEvent.tracking_uuid.in_(uuids),
                TrackingEvent.event_type == "click",
            )
        ).one() or 0

        trained = sum(1 for t in targets if t.training_completed)

        rows.append({
            "department":         dept,
            "total_targets":      total,
            "clicked":            clicks,
            "click_rate":         round(clicks / total * 100, 1),
            "training_completed": trained,
            "training_rate":      round(trained / total * 100, 1),
        })

    rows.sort(key=lambda r: r["click_rate"], reverse=True)
    return rows