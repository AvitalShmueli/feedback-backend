from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionHolder
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    Create a new feedback
    ---
    tags:
      - Feedback
    parameters:
        - name: feedback
          in: body
          required: true
          description: The feedback to create
          schema:
                id: feedback
                required:
                    - package_name
                    - app_version
                    - form_id
                    - user_id
                properties:
                    package_name:
                        type: string
                        description: The name of the package
                        example: com.example.myapp
                    message:
                        type: string
                        description: The content of the feedback
                    rating:
                        type: integer
                        description: Rating between 1-5
                    app_version:
                        type: string
                        description: The version of the app
                    device_info:
                        type: string
                        description: The info of the device
                    form_id:
                        type: string
                        description: Identifier for the feedback form
                    user_id:
                        type: string
                        description: unique identifier of the user
    responses:
        201:
            description: The feedback was created successfully
            schema:
                type: object
                properties:
                    package_name:
                        type: string
                    _id:
                        type: string
                    message:
                        type: string
                    rating:
                        type: integer
                    app_version:
                        type: string
                    device_info:
                        type: string
                    form_id:
                        type: string
                    user_id:
                        type: string
                    created_at:
                        type: string
                        format: date-time
        400:
            description: The request was invalid
        500:
            description: An error occurred while creating the feedback
    """
    logger.info("Received a request to submit new feedback.")
    data = request.json
    db = MongoConnectionHolder.get_db()
    # Check if the database connection was successful
    if db is None:
        logger.error("Could not connect to the database.")
        return jsonify({"error": "Could not connect to the database"}), 500

    # Check if the request is valid
    #required_fields = ["package_name", "message", "rating", "app_version", "form_id", "user_id"]
    required_fields = ["package_name", "app_version", "form_id", "user_id"]
    if not data:
        logger.warning("No JSON payload received.")
        return jsonify({
            "error": "Missing request body",
            "details": "Expected JSON payload with required fields"
        }), 400

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        logger.warning(f"Missing required fields: {missing_fields}")
        return jsonify({
            "error": "Invalid request",
            "details": f"Missing required field(s): {', '.join(missing_fields)}"
        }), 400
    
    # Check that at least 'message' or 'rating' is provided
    if not data.get("message") and data.get("rating") is None:
        logger.warning("Both 'message' and 'rating' are missing.")
        return jsonify({
            "error": "Invalid request",
            "details": "At least one of 'message' or 'rating' must be provided"
        }), 400
    
    # If rating is present, validate that it's an integer between 1 and 5
    if "rating" in data:
        try:
            rating = int(data["rating"])
            if not (1 <= rating <= 5):
                raise ValueError
        except (ValueError, TypeError):
            logger.warning(f"Invalid rating value: {data.get('rating')}")
            return jsonify({
                "error": "Invalid request",
                "details": "Rating must be an integer between 1 and 5"
            }), 400

    #if not data or not all(key in data for key in ["package_name", "message", "rating", "app_version", "form_id", "user_id"]):
    #    logger.warning("Invalid request data received.")
    #    return jsonify({"error": "Invalid request"}), 400

    feedback_item = {
        "_id": str(uuid.uuid4()),
        "message": data.get("message"),
        "rating": data.get("rating"),
        "app_version": data.get("app_version"),
        "device_info": data.get("device_info"),
        "form_id": data["form_id"],
        "user_id": data["user_id"],
        "created_at": datetime.now(),
    }

    try:
        logger.debug(f"Inserting feedback: {feedback_item}")
        package_collection = db[data["package_name"]]
        package_collection.insert_one(feedback_item)
    except Exception as e:
        logger.error(f"Error inserting feedback: {e}")
        return jsonify({"error": "Failed to store feedback"}), 500

    logger.info("Feedback submitted successfully.")
    return jsonify({
        "response": "Feedback submitted successfully",
        "package_name" : data["package_name"],
        "_id": feedback_item["_id"],
        "created_at": feedback_item["created_at"],
        "message": feedback_item["message"],
        "rating": feedback_item["rating"],
        "user_id": feedback_item["user_id"],
        "form_id": feedback_item["form_id"],
        "app_version": feedback_item["app_version"],
        "device_info": feedback_item["device_info"]
    }), 201
    
    # Insert the feature toggle into the database
    #logger.debug(f"Inserting feedback: {feedback_item}")
    #package_collection = db[data["package_name"]]
    #package_collection.insert_one(feedback_item)

    #logger.info("Feedback submitted successfully.")
    #return jsonify({
    #        "response": "Feedback submitted successfully",
    #        "_id": feedback_item["_id"],
    #        "created_at" : feedback_item["created_at"],
    #        "message": feedback_item["message"],
    #        "rating" : feedback_item["rating"],
    #        "user_id" : feedback_item["user_id"],
    #        "form_id" : feedback_item["form_id"],
    #        "app_version" : feedback_item["app_version"],
    #        "device_info" : feedback_item["device_info"]
    #    }),201
    

@feedback_bp.route("/feedback/<package_name>", methods=["GET"])
def get_all_package_feedback(package_name):
    """
    Get all feedbacks for a package
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: form_id
          in: query
          type: string
          required: false
          description: The id of the form
    responses:
        200:
            description: List of all feedbacks
            schema:
                type: array
                items:
                    type: object
                    properties:
                        _id:
                            type: string
                            description: Unique identifier of the feedback
                        message:
                            type: string
                            description: Content of the feedback
                        rating:
                            type: integer
                            description: Rating given by the user
                        app_version:
                            type: string
                            description: App version
                        device_info:
                            type: string
                            description: Device information
                        user_id:
                            type: string
                            description: User identifier
                        created_at:
                            type: string
                            format: date-time
                            description: Creation timestamp
        404:
            description: Package or form not found
        500:
            description: An error occurred while retrieving feedbacks
    """
    logger.info(f"Received request to get all feedback for package: {package_name}")
    form_id = request.args.get("form_id")
    query = {}
    if form_id is not None and form_id != "":
        query["form_id"] = form_id

    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    feedback_list = []
    # Find all feedbacks
    feedbacks = list(package_collection.find(query))
    if not feedbacks:
        logger.warning(f"No feedback entries found for form '{form_id}' in package '{package_name}'.")
        return jsonify({"error": "No feedbacks found for the form"}), 404
    
    for feedback in feedbacks:
        feedback_list.append(feedback)

    logger.info(f"Retrieved {len(feedback_list)} feedback entries for package '{package_name}'.")
    return jsonify(feedback_list), 200


@feedback_bp.route("/feedback/<package_name>/<feedback_id>", methods=["GET"])
def get_feedback_details(package_name, feedback_id):
    """
    Get a feedback by feedback-id
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: feedback_id
          in: path
          type: string
          required: true
          description: ID of the feedback to get
    responses:
        200:
            description: Feedback details
            schema:
                type: object
                properties:
                    _id:
                        type: string
                    message:
                        type: string
                    rating:
                        type: integer
                    app_version:
                        type: string
                    device_info:
                        type: string
                    user_id:
                        type: string
                    form_id:
                        type: string
                    created_at:
                        type: string
                        format: date-time
        404:
            description: Feedback not found
        500:
            description: An error occurred while retrieving feedback details
    """
    logger.info(f"Request to get feedback '{feedback_id}' for package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    # Find specific feedback
    for feedback in package_collection.find():
        if feedback["_id"] == feedback_id:
            logger.info(f"Feedback '{feedback_id}' found.")
            return jsonify(feedback), 200

    logger.warning(f"Feedback '{feedback_id}' not found.")
    return jsonify({"error": "Feedback not found"}), 404


@feedback_bp.route("/feedback/<package_name>/user/<user_id>", methods=["GET"])
def get_feedback_by_user(package_name, user_id):
    """
    Get a feedback by user id for package name
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: user_id
          in: path
          type: string
          required: true
          description: ID of the user to get
    responses:
        200:
            description: List of all feedbacks of the user for the package
            schema:
                type: array
                items:
                    type: object
                    properties:
                        _id:
                            type: string
                            description: Unique identifier of the feedback
                        message:
                            type: string
                            description: Content of the feedback
                        rating:
                            type: integer
                            description: Rating given by the user
                        app_version:
                            type: string
                            description: App version
                        device_info:
                            type: string
                            description: Device information
                        user_id:
                            type: string
                            description: User identifier
                        created_at:
                            type: string
                            format: date-time
                            description: Creation timestamp
        404:
            description: Package not found
        500:
            description: An error occurred while calculating the average rating
    """
    logger.info(f"Request to get feedback by user '{user_id}' for package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    feedbacks = list(package_collection.find({"user_id": user_id}))
    logger.info(f"Retrieved {len(feedbacks)} feedback entries for user '{user_id}'.")
    return jsonify(feedbacks), 200


@feedback_bp.route("/feedback/<package_name>/average-rating", methods=["GET"])
def get_average_rating(package_name):
    """
    Get an avereage rating for all feedback by package name
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: form_id
          in: query
          type: string
          required: false
          description: The id of the form
    responses:
        200:
            description: Average-rating of all package's feedback
            schema:
                type: object
                properties:
                    average_rating:
                        type: number
                        format: float
                        description: Average rating
        404:
            description: Package or form not found
        500:
            description: Database not initialized
    """
    logger.info(f"Request to get average rating for package '{package_name}'.")
    form_id = request.args.get("form_id")
    query = {}
    if form_id is not None and form_id != "":
        query["form_id"] = form_id

    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    ratings = []
    #ratings = [f["rating"] for f in package_collection.find(query) if "rating" in f]
    feedbacks = list(package_collection.find(query))
    if not feedbacks:
        logger.warning(f"No feedback entries found for form '{form_id}' in package '{package_name}'.")
        return jsonify({"error": "No feedbacks found for the form"}), 404
    
    for f in feedbacks:
        rating = f.get("rating")
        # Accept only integer ratings between 1 and 5
        if isinstance(rating, int) and 1 <= rating <= 5:
            ratings.append(rating)
            
    if ratings:
        avg = sum(ratings) / len(ratings)
        logger.info(f"Calculated average rating: {avg:.2f}")
        return jsonify({"average_rating": avg}), 200
    else:
        logger.info("No ratings found for this package.")
        return jsonify({"average_rating": 0}), 200


@feedback_bp.route("/feedback/stats/<package_name>", methods=["GET"])
def get_feedback_stats(package_name):
    """
    Get feedback statistics for a package
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: form_id
          in: query
          type: string
          required: false
          description: The id of the form
    responses:
        200:
            description: Feedback statistics (total count, average rating, rating breakdown)
            schema:
                type: object
                properties:
                    total_feedback:
                        type: integer
                    average_rating:
                        type: number
                        format: float
                    rating_breakdown:
                        type: object
                    additionalProperties:
                        type: integer
        404:
            description: Package or form not found
        500:
            description: An error occurred while retrieving feedback statistics
    """
    logger.info(f"Request to get feedback statistics for package '{package_name}'.")
    form_id = request.args.get("form_id")
    query = {}
    if form_id is not None and form_id != "":
        query["form_id"] = form_id

    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    feedbacks = list(package_collection.find(query))
    if not feedbacks:
        logger.warning(f"No feedback entries found for form '{form_id}' in package '{package_name}'.")
        return jsonify({"error": "No feedbacks found for the form"}), 404

    total_feedback = len(feedbacks)
    rating_breakdown = {str(i): 0 for i in range(1, 6)}
    ratings = []

    for f in feedbacks:
        rating = f.get("rating")
        if isinstance(rating, int) and 1 <= rating <= 5:
            rating_breakdown[str(f["rating"])] += 1
            ratings.append(rating)

    #ratings = [f["rating"] for f in feedbacks if "rating" in f]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    stats = {
        "total_feedback": total_feedback,
        "average_rating": avg_rating,
        "rating_breakdown": rating_breakdown,
    }

    logger.info(f"Feedback stats for package '{package_name}': {stats}")
    return jsonify(stats), 200


@feedback_bp.route("/feedback/<package_name>/search", methods=["GET"])
def search_feedback_by_message(package_name):
    """
    Search feedbacks by message content
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: q
          in: query
          type: string
          required: false
          description: Search term for the message
    responses:
        200:
            description: List of feedbacks that contain the search term
            schema:
                type: array
                items:
                    type: object
                    properties:
                        _id:
                            type: string
                        message:
                            type: string
                        rating:
                            type: integer
                        app_version:
                            type: string
                        device_info:
                            type: string
                        user_id:
                            type: string
                        created_at:
                            type: string
                            format: date-time
        404:
            description: Package not found
        500:
            description: An error occurred while searching for feedbacks
    """
    query = request.args.get("q", "")
    logger.info(f"Searching feedback for package '{package_name}' with query '{query}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    feedbacks = list(
        package_collection.find({"message": {"$regex": query, "$options": "i"}})
    )

    logger.info(f"Found {len(feedbacks)} feedback entries containing '{query}'.")
    return jsonify(feedbacks), 200


@feedback_bp.route("/feedback/<package_name>/recent", methods=["GET"])
def get_recent_feedback(package_name):
    """
    Get the most recent feedbacks for a package
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: form_id
          in: query
          type: string
          required: false
          description: The id of the form
        - name: limit
          in: query
          type: integer
          required: false
          description: Number of recent feedbacks to return
    responses:
        200:
            description: List of recent feedbacks
            schema:
                type: array
                items:
                    type: object
                    properties:
                        _id:
                            type: string
                        message:
                            type: string
                        rating:
                            type: integer
                        app_version:
                            type: string
                        device_info:
                            type: string
                        user_id:
                            type: string
                        created_at:
                            type: string
                            format: date-time
        404:
            description: Package not found
        500:
            description: An error occurred while retrieving recent feedbacks
    """
    limit = int(request.args.get("limit", 10))
    form_id = request.args.get("form_id")
    query = {}
    if form_id is not None and form_id != "":
        query["form_id"] = form_id
    logger.info(f"Fetching {limit} recent feedback entries for package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    feedbacks = list(package_collection.find(query).sort("created_at", -1).limit(limit))
    if not feedbacks:
        logger.warning(f"No feedback entries found for form '{form_id}' in package '{package_name}'.")
        return jsonify({"error": "No feedbacks found for the form"}), 404
    #feedbacks = list(package_collection.find().sort("created_at", -1).limit(limit))

    logger.info(f"Retrieved {len(feedbacks)} recent feedback entries.")
    return jsonify(feedbacks), 200


@feedback_bp.route("/feedback/<package_name>/<feedback_id>", methods=["DELETE"])
def delete_feedback(package_name, feedback_id):
    """
    Delete a specific feedback by ID for a package
    ---
    tags:
      - Feedback
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: Name of the package
      - name: feedback_id
        in: path
        type: string
        required: true
        description: ID of the feedback to delete
    responses:
        200:
            description: Feedback deleted successfully
            schema:
                type: object
                properties:
                    message:
                        type: string
        404:
            description: Feedback not found
        500:
            description: An error occurred while deleting the feedback
    """
    logger.info(f"Request to delete feedback '{feedback_id}' from package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    result = package_collection.delete_one({"_id": feedback_id})

    if result.deleted_count == 0:
        logger.warning(f"Feedback '{feedback_id}' not found for deletion.")
        return jsonify({"error": "Feedback not found"}), 404

    logger.info(f"Feedback '{feedback_id}' deleted successfully.")
    return jsonify({"message": "Feedback deleted successfully"}), 200


@feedback_bp.route("/feedback/<package_name>/form/<form_id>", methods=["DELETE"])
def delete_feedbacks_for_form(package_name, form_id):
    """
    Delete all feedbacks for a form in a package
    ---
    tags:
      - Feedback
    parameters:
        - name: package_name
          in: path
          type: string
          required: true
          description: Name of the package
        - name: form_id
          in: path
          type: string
          required: false
          description: The id of the form
    responses:
        200:
            description: All feedbacks for the form in the package deleted successfully
            schema:
                type: object
                properties:
                    message:
                        type: string
        404:
            description: Package / form not found
        500:
            description: An error occurred while deleting feedbacks
    """
    logger.info(f"Request to delete all feedback entries for form '{form_id}' in package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    delete_result = package_collection.delete_many({"form_id": form_id})
    deleted_count = delete_result.deleted_count

    if deleted_count == 0:
        logger.warning(f"No feedback entries found for form '{form_id}' in package '{package_name}'.")
        return jsonify({"error": "No feedbacks found for the form"}), 404

    logger.info(f"Deleted {deleted_count} feedback entries for form '{form_id}' in package '{package_name}'.")
    return jsonify({"message": f"Deleted {deleted_count} feedback entries for form '{form_id}'"}), 200


@feedback_bp.route("/feedback/<package_name>", methods=["DELETE"])
def delete_all_feedbacks(package_name):
    """
    Delete all feedbacks for a package
    ---
    tags:
      - Feedback
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: Name of the package
    responses:
        200:
            description: All feedbacks for the package deleted successfully
            schema:
                type: object
                properties:
                    message:
                        type: string
        404:
            description: Package not found
        500:
            description: An error occurred while deleting feedbacks
    """
    logger.info(f"Request to delete all feedback entries for package '{package_name}'.")
    db = MongoConnectionHolder.get_db()
    if db is None:
        logger.error("Database not initialized.")
        return jsonify({"error": "Database not initialized"}), 500

    if package_name not in db.list_collection_names():
        logger.warning(f"Package '{package_name}' not found.")
        return jsonify({"error": "Package not found"}), 404

    package_collection = db[package_name]
    deleted_count = package_collection.delete_many({}).deleted_count

    logger.info(f"Deleted {deleted_count} feedback entries for package '{package_name}'.")
    return jsonify({"message": f"Deleted {deleted_count} feedback entries"}), 200
