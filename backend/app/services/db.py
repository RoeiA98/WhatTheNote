import os
from motor.motor_asyncio import AsyncIOMotorClient
from zoneinfo import ZoneInfo
from bson.errors import InvalidId
from fastapi import HTTPException
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME")

# Create async MongoDB client
client = AsyncIOMotorClient(DB_URL)
db = client[DB_NAME]


async def get_database():
    return db


# User operations
async def get_users_collection():
    return db["users"]


async def get_user_by_email(email: str):
    users = await get_users_collection()
    return await users.find_one({"email": email})


async def create_user(user_data):
    users = await get_users_collection()
    return await users.insert_one(user_data)


async def update_user(user_id: str, update_data: dict):
    users = await get_users_collection()
    return await users.update_one({"id": user_id}, {"$set": update_data})


async def delete_user(user_id: str):
    users = await get_users_collection()
    return await users.delete_one({"id": user_id})


# Document operations
async def add_document_to_user(user_id: str, document_data: dict):
    users = await get_users_collection()
    return await users.update_one(
        {"id": user_id}, {"$push": {"documents": document_data}}
    )


async def get_user_documents(user_id: str, subject: str):
    users = await get_users_collection()
    user = await users.find_one({"id": user_id})
    return user.get("documents", []) if user else []


async def update_document(user_id: str, document_id: int, update_data: dict):
    users = await get_users_collection()
    return await users.update_one(
        {"id": user_id, "documents.id": document_id},
        {"$set": {"documents.$": update_data}},
    )


async def update_document_last_viewed(user_id: str, document_id: int):
    users = await get_users_collection()
    return await users.update_one(
        {"id": user_id, "documents.id": document_id},
        {"$set": {"documents.$.lastViewed": datetime.now(ZoneInfo("Asia/Jerusalem"))}},
    )


async def add_query_to_document(user_id: str, document_id: int, query_data: dict):
    users = await get_users_collection()
    return await users.update_one(
        {"id": user_id, "documents.id": document_id},
        {"$push": {"documents.$.queries": query_data}},
    )


async def get_next_document_id():
    counter_collection = db["counters"]
    counter = await counter_collection.find_one_and_update(
        {"_id": "document_id"}, {"$inc": {"seq": 1}}, upsert=True, return_document=True
    )
    return counter["seq"]


async def get_document(user_id: str, document_id: int):
    if not isinstance(document_id, int):
        raise HTTPException(status_code=400, detail="Document ID must be an integer")
    try:
        users = await get_users_collection()
        # print(f"Searching for user {user_id} with document {document_id}")
        user = await users.find_one(
            {"id": user_id, "documents.id": document_id}, {"documents.$": 1}
        )
        # print(f"Found user document: {bool(user)}")
        if not bool(user) or not user.get("documents"):
            return None

        doc = user["documents"][0]
        return {
            "id": doc["id"],
            "title": doc["title"],
            "content": doc["content"],
            "subject": doc["subject"],
            "summary": doc.get("summary", ""),
            "queries": doc.get("queries", []),
            "uploadedDate": doc["uploadedDate"].isoformat(),
            "lastViewed": datetime.now(ZoneInfo("Asia/Jerusalem")),
        }
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid document ID")


async def delete_document(user_id: str, document_id: int):
    users = await get_users_collection()
    result = await users.update_one(
        {"id": user_id}, {"$pull": {"documents": {"id": document_id}}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return result
