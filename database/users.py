import os
import re
import uuid
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from postgrest.exceptions import APIError
from pydantic import BaseModel, EmailStr, ValidationError
from supabase import create_client, Client

from models import URLType, JWTToken, UserResponse, VideoResponse, CommentResponse
from config import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class UserResponse(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    password: str
    regist_date: date

class UserService:
    def __init__(self):
        if not config.SUPABASE_URL or not config.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        self.supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        self.table_columns_cache = {}

    async def get_table_columns(self, table_name: str) -> List[str]:
        """
        Get the columns of a table.
        """
        if table_name in self.table_columns_cache:
            return self.table_columns_cache[table_name]
        
        #Query the table to get the columns
        try:
            result = self.supabase.table(table_name).select("*").limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
            else:
                #If no data, use default columns based on the model
                if table_name == "users":
                    columns = ['id', 'email', 'username', 'created_at']
                elif table_name == "videos":
                    columns = ['id', 'title', 'description', 'created_at']
                elif table_name == "comments":
                    columns = ['id', 'content', 'created_at']
                elif table_name == "url_types":
                    columns = ['id', 'name', 'created_at']
                elif table_name == "jwt_tokens":
                    columns = ['id', 'token', 'created_at']
                elif table_name == "likes":
                    columns = ['id', 'user_id', 'video_id', 'created_at']
                elif table_name == "dislikes":
                    columns = ['id', 'user_id', 'video_id', 'created_at']
                elif table_name == "subscriptions":
                    columns = ['id', 'user_id', 'channel_id', 'created_at']
                elif table_name == "views":
                    columns = ['id', 'user_id', 'video_id', 'created_at']
                elif table_name == "ratings":
                    columns = ['id', 'user_id', 'video_id', 'rating', 'created_at']
                elif table_name == "playlists":
                    columns = ['id', 'name', 'description', 'created_at']
                elif table_name == "playlist_items":
                    columns = ['id', 'playlist_id', 'video_id', 'created_at']
                elif table_name == "notifications":
                    columns = ['id', 'user_id', 'notification_type', 'created_at']
                else:
                    columns = []

                self.table_columns_cache[table_name] = columns
                return columns
        except APIError as e:
            logger.error(f"Error getting columns for table {table_name}: {e}")
            return []
        return []
    
    async def get_user_by_email(self, email: str) -> Optiona[UserResponse]:
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        if result.data:
            return UserResponse(**result.data[0])

    async def create_user(self, user_data: Dict[str, Any]) -> UserResponse:

        """
        Get current schema columns(cached in produiction for efficiency)
        """
        user_columns = await self.get_table_columns("user")

        user_id = user_data.get("user_id", "")
        user_data.setdefault("user_name", "John Smith")
        user_data.setdefault("email", "johnsmith@gmail.com")
        user_data.setdefault("password", "John123!@#")
        user_data.setdefault("confirm_password", "Please confirm password")
        user_data.setdefault("regist_date", date)

        # --- Required fields
        required_fields = ["user_name", "email", "password", "confirm_password"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValueError(f"{field} is required")
            
        # ---Email Validation ---
        try:
            EmailStr.validate(user_data["email"])
        except ValidationError:
            raise ValueError("Invalid email format")
        
        # ---Password Validation ---
        password = user_data["password"]
        if len(password) < 8:
            raise ValueError("Password must be at least 8 charactors")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include at least a lowercase, a uppercase letter, a number and a special character")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include at least a lowercase, a uppercase letter, a number and a special character")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must include at least a lowercase, a uppercase letter, a number and a special character")
        if not re.search(r"[!@#$%^&*?\":{}|<>]", password):
            raise ValueError("Password must include at least a lowercase, a uppercase letter, a number and a special character")

        # ---Confirm Password ---
        if password != user_data.get("confirm_password"):
            raise ValueError("Password and confirm password do not match")
        
        # --- Check if email already exists ---
        existing_user = await self.get_user_by_email(user_data["email"])
        if existing_user:
            raise ValueError("Already exist user")
        
        # --- Prepare data for insertion ---
        user_columns = await self.get_table_columns("users")
        user_data.setdefault("regist_date", datetime.utcnow().data())
        
        # --- Keep only columns that exist in the table ---
        filtered_data = {k: v for k, v in user_data.items() if k in user_columns}

        # --- Serialize datetime/date objects ---
        for k, v in filtered_data.items():
            if isinstance(v, (datetime, date)):
                filtered_data[k] = v.isoformat()

        # --- Insert into database ---
        result = self.supabase.table("users").insert(filtered_data).execute()

        if result.data:
            # Merge server-returned values to satisfy Pydantic model
            final_row = {**filtered_data, **(result.data[0] or {})}
            return UserResponse(**final_row)
        
        raise Exception("Failed to create user entry")
    