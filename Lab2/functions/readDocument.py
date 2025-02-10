import azure.functions as func
import pymongo
import redis
import os
import json
from bson import ObjectId
from typing import Optional

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get environment variables
        cosmos_db_connection = os.getenv("COSMOS_DB_CONNECTION_STRING")
        db_name = os.getenv("COSMOS_DB_NAME")
        collection_name = os.getenv("COSMOS_DB_COLLECTION")
        redis_connection = os.getenv("REDIS_CONNECTION")

        if not all([cosmos_db_connection, db_name, collection_name, redis_connection]):
            raise ValueError("Missing database configuration in application settings")

        # Initialize connections inside the function
        mongo_client = pymongo.MongoClient(cosmos_db_connection)
        collection = mongo_client[db_name][collection_name]
        redis_client = redis.Redis.from_url(redis_connection, ssl_cert_reqs=None)

        # Get document ID
        document_id = req.params.get('id')
        if not document_id:
            return func.HttpResponse(
                "Please provide a document ID in the query parameters",
                status_code=400
            )

        # Try Redis cache first
        cached_data = redis_client.get(document_id)
        if cached_data:
            return func.HttpResponse(
                cached_data.decode('utf-8'),
                status_code=200,
                mimetype="application/json",
                headers={"X-Cache": "HIT"}
            )

        # MongoDB lookup
        document = collection.find_one({"_id": ObjectId(document_id)})
        if not document:
            return func.HttpResponse(
                json.dumps({"error": "Document not found"}),
                status_code=404,
                mimetype="application/json"
            )

        # Convert and cache
        document_json = json.dumps(document, default=str)
        redis_client.set(
            name=document_id,
            value=document_json,
            ex=3600  # Cache for 1 hour (adjust as needed)
        )

        return func.HttpResponse(
            document_json,
            status_code=200,
            mimetype="application/json",
            headers={"X-Cache": "MISS"}
        )

    except (pymongo.errors.PyMongoError, redis.RedisError) as db_error:
        return func.HttpResponse(
            json.dumps({"error": f"Database error: {str(db_error)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as generic_error:
        return func.HttpResponse(
            json.dumps({"error": f"Server error: {str(generic_error)}"}),
            status_code=500,
            mimetype="application/json"
        )