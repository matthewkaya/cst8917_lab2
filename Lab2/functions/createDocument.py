import azure.functions as func
import pymongo
import os
import json
from typing import Any

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get environment variables from Azure Functions configuration
        cosmos_db_connection = os.getenv("COSMOS_DB_CONNECTION_STRING")
        db_name = os.getenv("COSMOS_DB_NAME")
        collection_name = os.getenv("COSMOS_DB_COLLECTION")

        if not all([cosmos_db_connection, db_name, collection_name]):
            raise ValueError("Missing Cosmos DB configuration in application settings")

        # Initialize MongoDB client inside the function for better cold start performance
        mongo_client = pymongo.MongoClient(cosmos_db_connection)
        collection = mongo_client[db_name][collection_name]

        # Process request
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                "Please pass a document in the request body",
                status_code=400
            )

        # Insert document
        result = collection.insert_one(req_body)
        inserted_id = str(result.inserted_id)

        return func.HttpResponse(
            json.dumps({
                "id": inserted_id,
                "message": "Document created successfully",
                "database": db_name,
                "collection": collection_name
            }),
            status_code=201,
            mimetype="application/json",
            headers={"Content-Type": "application/json"}
        )

    except pymongo.errors.PyMongoError as mongo_error:
        return func.HttpResponse(
            json.dumps({"error": f"MongoDB error: {str(mongo_error)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as generic_error:
        return func.HttpResponse(
            json.dumps({"error": f"Server error: {str(generic_error)}"}),
            status_code=500,
            mimetype="application/json"
        )