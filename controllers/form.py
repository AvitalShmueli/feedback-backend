from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionHolder
from datetime import datetime
from bson import ObjectId
import uuid
import logging

logger = logging.getLogger(__name__)

form_bp = Blueprint("form", __name__)


@form_bp.route("/admin/forms", methods=["POST"])
def create_form():
    """
    Create a new feedback form for a package.
    ---
    tags:
      - Admin Forms
    description: Creates a new form for the given package and deactivates any previously active forms.
    parameters:
        - name: feedback
          in: body
          required: true
          description: The feedback to create
          schema:
                id: form
                required:
                    - package_name
                    - title
                    - type
                properties:
                    package_name:
                        type: string
                        description: The name of the package
                        example: com.example.myapp
                    title:
                        type: string
                        description: The text to be displayed in the feedback form popup
                        example: How satisfied are you with our app?
                    type:
                        type: string
                        enum: [rating, free_text, rating_text]
                        example: rating
            
    responses:
        201:
            description: Form created successfully
            schema:
                type: object
                properties:
                    message:
                        type: string
                    form_id:
                        type: string
                    created_at:
                        type: string
                        format: date-time
                    type:
                        type: string
                        enum: [rating, free_text, rating_text]
        400:
            description: The request was invalid
        500:
            description: An error occurred while creating the form
    """
    logger.info("Received a request to submit new form.")
    data = request.get_json()
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Could not connect to the database.")
        return jsonify({"error": "Could not connect to the database"}), 500
    
    package_name = data.get("package_name")
    title = data.get("title")
    form_type = data.get("type")  # "rating" or "free_text" or "rating_text"

    if not package_name or not title or form_type not in ["rating", "free_text", "rating_text"]:
        logger.warning("Invalid request data received.")
        return jsonify({"error": "Invalid request"}), 400

    # Disable existing active forms for this package
    result = db["forms"].update_many(
        {"package_name": package_name, "is_active": True},
        {"$set": {
            "is_active": False,
            "updated_at": datetime.now()
            }}
    )
    disabled_count = result.modified_count
    logger.info(f"Disabled {disabled_count} active form(s) for package '{package_name}'.")
    
    # Create new form document
    form_doc = {
        "_id": str(uuid.uuid4()),
        "package_name": package_name,
        "title": title,
        "type": form_type,
        "created_at": datetime.now(),
        "updated_at" : datetime.now(),
        "is_active": True
    }

    logger.debug(f"Inserting form: {form_doc}")
    db["forms"].insert_one(form_doc)

    logger.info("Form created successfully.")
    return jsonify({
        "message": "Form created successfully!",
        "_id": form_doc["_id"],
        "created_at": form_doc["created_at"],
        "type": form_type
        }), 201


@form_bp.route("/forms/packages", methods=["GET"])
def get_all_package_names():
    """
    Get all unique package names from the forms collection.
    ---
    tags:
      - Admin Forms
    description: Returns a list of all distinct package names in the forms database.
    responses:
        200:
            description: List of unique package names
            schema:
                type: array
                items:
                    type: string
        500:
            description: Internal server error
    """
    logger.info("Request to get all unique package names.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    try:
        package_names = db["forms"].distinct("package_name")
        logger.info(f"Found {len(package_names)} unique package name(s).")
        return jsonify(package_names), 200
    except Exception as e:
        logger.exception("Error retrieving package names.")
        return jsonify({"error": "Failed to retrieve package names."}), 500


@form_bp.route("/forms/<package_name>", methods=["GET"])
def get_active_form(package_name):
    """
    Get active form for a package.
    ---
    tags:
      - Forms
    description: Returns the currently active form for the specified package.
    parameters:
        - in: path
          name: package_name
          type: string
          required: true
          description: Package name to retrieve the active form for
    responses:
        200:
            description: Active form found
            schema:
                type: object
                properties:
                    _id:
                        type: string
                    package_name:
                        type: string
                    title:
                        type: string
                    type:
                        type: string
                    created_at:
                        type: string
                    is_active:
                        type: boolean
        404:
            description: Package no found or no active form found
        500:
            description: An error occurred while retrieving the form
    """
    logger.info(f"Request to get active form for package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500
   
    form_doc = db["forms"].find_one(
        {"package_name": package_name, "is_active": True}
    )

    if not form_doc:
        logger.warning("No active form found for this package.")
        return jsonify({"error": "No active form found for this package"}), 404

    logger.info(f"Form '{form_doc}' found.")
    return jsonify(form_doc), 200


@form_bp.route("/forms/<package_name>/all", methods=["GET"])
def get_all_forms_by_package(package_name):
    """
    Get all forms for a package.
    ---
    tags:
      - Admin Forms
    description: Returns all forms for the specified package, optionally filtered by status.
    parameters:
        - in: path
          name: package_name
          type: string
          required: true
          description: Package name to retrieve the active form for
        - name: status
          in: query
          type: string
          enum: [active, inactive]
          required: false
          description: Filter forms by active/inactive status.
    responses:
        200:
            description: List of all forms for the specified package
            schema:
                type: array
                items:
                    type: object
                    properties:
                        _id:
                            type: string
                        package_name:
                            type: string
                        title:
                            type: string
                        type:
                            type: string
                        created_at:
                            type: string
                        is_active:
                            type: boolean
        404:
            description: Package no found or no active form found
        400:
            description: Invalid status parameter
        500:
            description: An error occurred while retrieving the form
    """
    logger.info(f"Request to get all forms for package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500
    
    status = request.args.get("status")
    query = {"package_name": package_name}

    if status:
        status = status.lower()
        if status not in ["active", "inactive"]:
            logger.warning(f"Invalid status filter: {status}")
            return jsonify({"error": "Invalid status parameter. Must be 'active' or 'inactive'."}), 400
        query["is_active"] = (status == "active")
   
    form_list = list(db["forms"].find(query))

    if not form_list:
        logger.warning("No forms found for this package.")
        return jsonify({"error": "No forms found for this package"}), 404

    logger.info(f"Retrieved {len(form_list)} forms entries for package '{package_name}'.")
    return jsonify(form_list), 200


@form_bp.route("/forms/all", methods=["GET"])
def get_all_forms():
    """
    Get all forms.
    ---
    tags:
      - Admin Forms
    description: Returns all forms, optionally filtered by status.
    parameters:
        - name: status
          in: query
          type: string
          enum: [active, inactive]
          required: false
          description: Filter forms by active/inactive status.
    responses:
        200:
            description: List of all forms
            schema:
                type: array
                items:
                    type: object
                    properties:
                        _id:
                            type: string
                        package_name:
                            type: string
                        title:
                            type: string
                        type:
                            type: string
                        created_at:
                            type: string
                        is_active:
                            type: boolean
        404:
            description: No forms found
        400:
            description: Invalid status parameter
        500:
            description: An error occurred while retrieving the form
    """
    logger.info(f"Request to get all forms.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500
    
    status = request.args.get("status")
    query = {}
    if status:
        status = status.lower()
        if status not in ["active", "inactive"]:
            logger.warning(f"Invalid status filter: {status}")
            return jsonify({"error": "Invalid status parameter. Must be 'active' or 'inactive'."}), 400
        query["is_active"] = (status == "active")
    
    form_list = list(db["forms"].find(query))

    if not form_list:
        logger.warning("No forms found.")
        return jsonify({"error": "No forms found"}), 404

    logger.info(f"Retrieved {len(form_list)} forms entries.")
    return jsonify(form_list), 200


@form_bp.route("/forms/<form_id>/activate", methods=["PUT"])
def update_form_status(form_id):
    """
    Update the `is_active` status of a form by form_id and deactivate other forms for the same package_name.
    ---
    tags:
      - Admin Forms
    parameters:
        - name: form_id
          in: path
          required: true
          schema:
          type: string
          description: Unique ID of the form
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                is_active:
                    type: boolean
            required:
                - is_active
    responses:
        200:
            description: Status updated successfully
            schema:
                type: object
                properties:
                    message:
                        type: string
                    form_id:
                        type: string
                    is_active:
                        type: boolean
                    updated_at:
                        type: string
                        format: date-time
                    deactivated_forms_count:
                        type: integer
        400:
            description: Missing or invalid parameter
        404:
            description: Form not found
        500: 
            description: An error occurred while updating the form
    """
    logger.info(f"Request to get form by id '{form_id}'.")
    data = request.get_json()
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500
    
    if not data or "is_active" not in data:
        logger.warning("Invalid request data received.")
        return jsonify({"message": "Invalid request data received."}), 400

    is_active = data["is_active"]

    form = db["forms"].find_one({"_id": form_id})
    if not form:
        logger.warning(f"Form '{form_id}' not found.")
        return jsonify({"message": "Form not found."}), 404

    # If activating this form, deactivate others in the same package_name
    deactivated_forms_count = 0
    if is_active:
        result = db["forms"].update_many(
            {
                "package_name": form["package_name"],
                "_id": {"$ne": form_id},
                "is_active": True
            },
            {"$set": {"is_active": False}}
        )
        deactivated_forms_count = result.modified_count

    # Update the target form
    updated_at = datetime.now()
    db["forms"].update_one(
        {"_id": form_id},
        {"$set": {
            "is_active": is_active,
            "updated_at": datetime.now()
            }}
    )

    logger.info(f"Form {form_id} updated. is_active={is_active}. Deactivated {deactivated_forms_count} other forms.")

    return jsonify({
        "message": "Form status updated successfully.",
        "_id": form_id,
        "is_active": is_active,
        "updated_at": updated_at,
        "deactivated_forms_count": deactivated_forms_count
    }), 200


@form_bp.route("/forms/search", methods=["GET"])
def search_forms():
    """
    Search for forms using optional filters: package_name, status, title, and type.
    ---
    tags:
      - Admin Forms
    description: Returns a list of forms filtered by any combination of package_name, status (active/inactive), title (partial), and type.
    parameters:
        - name: package_name
          in: query
          type: string
          required: false
          description: Filter by exact package name
        - name: status
          in: query
          type: string
          enum: [active, inactive]
          required: false
          description: Filter by status (active/inactive)
        - name: title
          in: query
          type: string
          required: false
          description: Filter by partial title (case-insensitive)
        - name: type
          in: query
          type: string
          enum: [rating, free_text, rating_text]
          required: false
          description: Filter by form type (rating/free_text/rating_text)
    responses:
        200:
            description: List of matching forms
        500:
            description: Internal error
    """
    logger.info("Request to search forms with optional filters.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    # Collect optional query params
    package_name = request.args.get("package_name")
    status = request.args.get("status")
    title = request.args.get("title")
    form_type = request.args.get("type")

    # Build query dynamically
    query = {}
    if package_name:
        query["package_name"] = package_name

    if status:
        if status.lower() == "active":
            query["is_active"] = True
        elif status.lower() == "inactive":
            query["is_active"] = False
        else:
            return jsonify({"error": "Invalid status value. Must be 'active' or 'inactive'."}), 400

    if title:
        query["title"] = {"$regex": title, "$options": "i"}  # case-insensitive partial match

    if form_type:
        query["type"] = form_type

    try:
        forms = list(db["forms"].find(query))
        logger.info(f"Found {len(forms)} form(s) matching filters: {query}")
        return jsonify(forms), 200
    except Exception as e:
        logger.exception("Error occurred during advanced form search.")
        return jsonify({"error": "Failed to retrieve forms"}), 500

