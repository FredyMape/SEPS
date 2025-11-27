from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import launch_campaigns, metrics
from .routers import email_template, campaign, landing_page, smtp_profile, users, group, group_users
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI(
    title="Campaign Management API",
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None
)
origins = [
    "https://training.empleados.com.co",
    "https://sofka.empleados.com.co",
    "https://wesofka.empleados.com.co",
    "https://drive.empleados.com.co",
    "https://profilehub.empleados.com.co"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.mount("/pages", StaticFiles(directory="assets/templates"), name="assets")
 
app.include_router(email_template.router)
app.include_router(campaign.router)
app.include_router(landing_page.router)
app.include_router(smtp_profile.router)
app.include_router(users.router)
app.include_router(group.router)
app.include_router(group_users.router)
app.include_router(metrics.router)
app.include_router(launch_campaigns.router)