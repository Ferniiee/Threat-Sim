from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from sqlmodel import Session, select
from database import engine
from models import Target, TrackingEvent, Campaign

router = APIRouter(prefix="/track", tags=["tracking"])

@router.get("/pixel/{uuid}")
def track_open(uuid: str, request: Request):
    with Session(engine) as session:
        target = session.exec(
            select(Target).where(Target.tracking_uuid == uuid)
        ).first()
        if not target:
            raise HTTPException(status_code=404, detail="Invalid tracking link")
        event = TrackingEvent(
            tracking_uuid=uuid,
            event_type="open",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        session.add(event)
        session.commit()
    gif = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    return Response(content=gif, media_type="image/gif")

@router.get("/click/{uuid}")
def track_click(uuid: str, request: Request):
    with Session(engine) as session:
        target = session.exec(
            select(Target).where(Target.tracking_uuid == uuid)
        ).first()
        if not target:
            raise HTTPException(status_code=404, detail="Invalid tracking link")

        event = TrackingEvent(
            tracking_uuid=uuid,
            event_type="click",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        session.add(event)
        session.commit()

        campaign_id = target.campaign_id
        campaign = session.get(Campaign, campaign_id)
        campaign_type = campaign.campaign_type if campaign else "credential-harvest"

    return RedirectResponse(
        url=f"/track/training/{uuid}?type={campaign_type}",
        status_code=302
    )

@router.post("/report/{uuid}")
def track_report(uuid: str, request: Request):
    with Session(engine) as session:
        target = session.exec(
            select(Target).where(Target.tracking_uuid == uuid)
        ).first()
        if not target:
            raise HTTPException(status_code=404, detail="Invalid tracking link")
        event = TrackingEvent(
            tracking_uuid=uuid,
            event_type="report",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        session.add(event)
        session.commit()
    return {"message": "Thank you for reporting this email. This was a security test."}

@router.get("/training/{uuid}", response_class=HTMLResponse)
def training_page(uuid: str, type: str = "credential-harvest"):
    training_content = {
        "credential-harvest": {
            "title": "You fell for a credential harvesting attack",
            "what": "This email tried to steal your username and password by sending you to a fake login page.",
            "signs": [
                "Urgent language like 'immediate action required'",
                "Threats of account suspension",
                "Links that don't match the real company domain",
                "Requests for your password via email"
            ],
            "next": "Always verify requests for credentials by calling IT directly."
        },
        "urgency": {
            "title": "You fell for an urgency manipulation attack",
            "what": "This email used artificial urgency to make you act without thinking.",
            "signs": [
                "Countdown timers or deadlines",
                "Threats of negative consequences",
                "Pressure to act immediately",
                "No time given to verify the request"
            ],
            "next": "When in doubt, slow down. Legitimate requests can always wait for verification."
        },
        "attachment-lure": {
            "title": "You fell for an attachment lure attack",
            "what": "This email tried to get you to open a malicious file attachment.",
            "signs": [
                "Unexpected attachments from unknown senders",
                "Generic filenames like 'invoice.pdf' or 'document.exe'",
                "Pressure to open the file immediately",
                "Sender email does not match the display name"
            ],
            "next": "Never open attachments you were not expecting. Verify with the sender first."
        }
    }

    content = training_content.get(type, training_content["credential-harvest"])
    signs_html = "".join([f"<li>{s}</li>" for s in content["signs"]])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Awareness Training - ThreatSim</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .warning {{ background: #ff4444; color: white; padding: 20px; border-radius: 8px; }}
            .content {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin-top: 20px; }}
            .next-steps {{ background: #4CAF50; color: white; padding: 15px; border-radius: 8px; margin-top: 20px; }}
            ul {{ line-height: 2; }}
        </style>
    </head>
    <body>
        <div class="warning">
            <h1>Security Training Required</h1>
            <h2>{content["title"]}</h2>
        </div>
        <div class="content">
            <h3>What happened?</h3>
            <p>{content["what"]}</p>
            <h3>Warning signs you missed:</h3>
            <ul>{signs_html}</ul>
        </div>
        <div class="next-steps">
            <h3>What to do next time:</h3>
            <p>{content["next"]}</p>
        </div>
        <p style="margin-top:30px; color:#666;">
            This was a simulated phishing test conducted by your security team using ThreatSim.
            No real harm was done. Thank you for completing this training.
        </p>
    </body>
    </html>
    """