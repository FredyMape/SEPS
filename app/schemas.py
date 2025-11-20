from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
 
# ============================================================
# 📧 EmailTemplate
# ============================================================
class EmailTemplateBase(BaseModel):
    Name: str
    EnvelopeSender: str
    Subject: str
    Content: str
 
class EmailTemplateCreate(EmailTemplateBase):
    pass
 
class EmailTemplateOut(EmailTemplateBase):
    Id: int
    CreatedAt: datetime
 
    class Config:
        orm_mode = True
 
 
# ============================================================
# 🌐 LandingPage
# ============================================================
class LandingPageBase(BaseModel):
    Name: str
    HtmlContent: str
    Description: str
    RedirectTo: Optional[str] = None
 
class LandingPageCreate(LandingPageBase):
    pass
 
class LandingPageOut(LandingPageBase):
    Id: int
    CreatedAt: datetime
 
    class Config:
        orm_mode = True
 
 
# ============================================================
# 📬 SMTP Profile
# ============================================================
class SmtpProfileBase(BaseModel):
    ProfileName: str
    SmtpFrom: str
    Host: str
    Username: str
    PasswordEncrypted: str
    Port: int
    UseTls: bool
 
class SmtpProfileCreate(SmtpProfileBase):
    pass
 
class SmtpProfileOut(BaseModel):
    Id: int
    ProfileName: str
    SmtpFrom: str
    Host: str
    Username: str
    Port: int
    UseTls: bool
    CreatedAt: datetime

    model_config = ConfigDict(from_attributes=True)
  
# ============================================================
# 👥 Groups
# ============================================================
class GroupBase(BaseModel):
    GroupName: str
    IsActive: bool = True
 
class GroupCreate(GroupBase):
    pass
 
class GroupOut(GroupBase):
    Id: int
    CreatedAt: datetime
 
    class Config:
        orm_mode = True
 
 
# ============================================================
# 👤 Users
# ============================================================
class UserBase(BaseModel):
    FirstName: str
    MiddleName: Optional[str] = None
    Email: str
    JobDepartment: Optional[str] = None
    IsActive: bool = True
 
class UserCreate(UserBase):
    pass
 
class UserOut(UserBase):
    Id: int
    CreatedAt: datetime
 
    class Config:
        orm_mode = True
 
 
# ============================================================
# 🔗 GroupUsers
# ============================================================
class GroupUserBase(BaseModel):
    GroupId: int
    UserId: int
 
class GroupUserCreate(GroupUserBase):
    pass
 
class GroupUserOut(GroupUserBase):
    Id: int
    AddedAt: datetime
 
    class Config:
        orm_mode = True
 
 
# ============================================================
# 🎯 Campaign
# ============================================================
class CampaignBase(BaseModel):
    CampaignName: str
    EmailTemplateId: int
    LandingPageId: int
    Url: Optional[str] = None
    LaunchDate: datetime
    SmtpProfileId: int
    GroupId: int
    Status: Optional[str] = None
 
class CampaignCreate(CampaignBase):
    pass
 
class CampaignOut(CampaignBase):
    Id: int
    CreatedAt: datetime
 
    class Config:
        orm_mode = True
 
 
# ============================================================
# 👀 Vista: vw_CampaignRecipients (solo lectura)
# ============================================================
class CampaignRecipientOut(BaseModel):
    CampaignId: int
    UserId: int
    Email: str
    CampaignName: str
    LaunchDate: datetime
 
    class Config:
        orm_mode = True

class LaunchCampaignResult(BaseModel):
    total_recipients: int
    emails_sent: int
    errors: int
    message: str

    
# ============================================================
# 🚀 LaunchCampaign
# ============================================================
class LaunchCampaignBase(BaseModel):
    IdCampaign: int
    Date: Optional[datetime] = None
    TotalRecipients: Optional[int] = 0
    EmailsSent: Optional[int] = 0

class LaunchCampaignCreate(LaunchCampaignBase):
    pass

class LaunchCampaignOut(LaunchCampaignBase):
    Id: int

    class Config:
        orm_mode = True


# ============================================================
# 📊 Metrics
# ============================================================
class MetricsBase(BaseModel):
    IdLaunch: int
    IdUser: int
    SendMail: bool = False
    OpenMail: bool = False
    OpenLandingPage: bool = False
    SendData: bool = False
    TrainingCompleted: bool = False

class MetricsCreate(MetricsBase):
    pass

class MetricsOut(MetricsBase):
    Id: int

    class Config:
        orm_mode = True