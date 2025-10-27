from fastapi import FastAPI
from .routers import email_template, campaign, landing_page, smtp_profile, users, group, group_users

app = FastAPI(title="Campaign Management API")

app.include_router(email_template.router)
app.include_router(campaign.router)
app.include_router(landing_page.router)
app.include_router(smtp_profile.router)
app.include_router(users.router)
app.include_router(group.router)
app.include_router(group_users.router)