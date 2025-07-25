from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class IdentityData(BaseModel):
    avatar_url: Optional[str]
    email: Optional[EmailStr]
    email_verified: Optional[bool]
    full_name: Optional[str]
    iss: Optional[str]
    name: Optional[str]
    phone_verified: Optional[bool]
    picture: Optional[str]
    provider_id: Optional[str]
    sub: Optional[str]

class Identity(BaseModel):
    identity_id: str
    id: str
    user_id: str
    identity_data: IdentityData
    provider: str
    last_sign_in_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    email: Optional[EmailStr]

class AppMetadata(BaseModel):
    provider: Optional[str]
    providers: Optional[List[str]]

class UserMetadata(BaseModel):
    avatar_url: Optional[str]
    email: Optional[EmailStr]
    email_verified: Optional[bool]
    full_name: Optional[str]
    iss: Optional[str]
    name: Optional[str]
    phone_verified: Optional[bool]
    picture: Optional[str]
    provider_id: Optional[str]
    sub: Optional[str]

class UserModel(BaseModel):
    id: str
    aud: str
    role: str
    email: EmailStr
    email_confirmed_at: Optional[datetime]
    phone: Optional[str]
    confirmed_at: Optional[datetime]
    last_sign_in_at: Optional[datetime]
    app_metadata: AppMetadata
    user_metadata: UserMetadata
    identities: List[Identity]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_anonymous: Optional[bool]

class UserResponse(BaseModel):
    user: UserModel
