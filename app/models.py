from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class EmailTemplate(Base):
    __tablename__ = "EmailTemplate"
    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    EnvelopeSender = Column(String)
    Subject = Column(String)
    Content = Column(String)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

class LandingPage(Base):
    __tablename__ = "LandingPage"
    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    HtmlContent = Column(String)
    RedirectTo = Column(String)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

class SmtpProfile(Base):
    __tablename__ = "SmtpProfile"
    Id = Column(Integer, primary_key=True, index=True)
    ProfileName = Column(String)
    SmtpFrom = Column(String)
    Host = Column(String)
    Username = Column(String)
    PasswordEncrypted = Column(String)
    Port = Column(Integer)
    UseTls = Column(Boolean)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

class Groups(Base):
    __tablename__ = "Groups"
    Id = Column(Integer, primary_key=True, index=True)
    GroupName = Column(String)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    IsActive = Column(Boolean, default=True)
    users = relationship("GroupUsers", back_populates="group")

class Users(Base):
    __tablename__ = "Users"
    Id = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String)
    MiddleName = Column(String, nullable=True)
    Email = Column(String, unique=True)
    JobDepartment = Column(String)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    IsActive = Column(Boolean, default=True)
    groups = relationship("GroupUsers", back_populates="user")

class GroupUsers(Base):
    __tablename__ = "GroupUsers"
    Id = Column(Integer, primary_key=True, index=True)
    GroupId = Column(Integer, ForeignKey("Groups.Id"))
    UserId = Column(Integer, ForeignKey("Users.Id"))
    AddedAt = Column(DateTime, default=datetime.utcnow)
    group = relationship("Groups", back_populates="users")
    user = relationship("Users", back_populates="groups")

class Campaign(Base):
    __tablename__ = "Campaign"
    Id = Column(Integer, primary_key=True, index=True)
    CampaignName = Column(String)
    EmailTemplateId = Column(Integer, ForeignKey("EmailTemplate.Id"))
    LandingPageId = Column(Integer, ForeignKey("LandingPage.Id"))
    Url = Column(String)
    LaunchDate = Column(DateTime)
    SmtpProfileId = Column(Integer, ForeignKey("SmtpProfile.Id"))
    GroupId = Column(Integer, ForeignKey("Groups.Id"))
    Status = Column(String)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    
class vw_CampaignRecipients(Base):
    __tablename__ = "vw_CampaignRecipients"
    CampaignId = Column(Integer)
    UserId = Column(Integer)
    Email = Column(String)
    CampaignName = Column(String)
    LaunchDate = Column(DateTime)
    __mapper_args__ = {"primary_key": [CampaignId, UserId]}

class CampaignLog(Base):
    __tablename__ = "CampaignLog"
    Id = Column(Integer, primary_key=True, index=True)
    CampaignId = Column(Integer, ForeignKey("Campaign.Id"))
    UserId = Column(Integer, ForeignKey("Users.Id"))
    Email = Column(String)
    Status = Column(String)
    SentAt = Column(DateTime, default=datetime.utcnow)
