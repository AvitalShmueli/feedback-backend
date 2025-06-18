# Feedback Backend

This API provides functionality for collecting and managing in-app user feedback in a MongoDB-backed system. The service enables developers to integrate feedback forms into their mobile and web applications, gather user responses, and analyze the collected data. Built with Flask, the backend offers a RESTful architecture that supports multiple application integrations through a common feedback infrastructure.

---

## Overview

This backend service allows app developers to:
- Create and manage different types of feedback forms (rating, free text, or both)
- Collect user feedback from multiple applications/packages
- Retrieve and analyze feedback statistics
- Search through feedback submissions

---

## API Endpoints

### <ins>Form Management</ins>

### 1. Create Feedback Form
  **POST /admin/forms**
  
  **Description:** Creates a new feedback form for a package
  
**Request Body:**
```json
{
  "package_name": "com.example.app",
  "title": "Feedback Form",
  "description": "We value your feedback",
  "form_type": "rating_text",
  "is_active": true
}
```

**Responses:**
- **201** - Form created successfully
- **400** - Invalid form data
- **500** - Internal Server Error

---

###  2. Get All Package Names
**GET /forms/packages**

**Description:** Returns all unique package names from the forms collection

**Responses:**
- **200** -   List of unique package names
- **500** -  Internal Server Error

---

###  3. Get Active Form
**GET /forms/<package_name>**

**Description:** Returns the active form for the specified package

**Path Parameters:**
- `package_name` (string): The unique identifier of the application package

**Responses:**
- **200** - The active form of the specified package
- **404** - Package not found or no active form found for the specified package
- **500** - Internal Server Error

---

### 4. Get All Forms by Package
**GET /forms/<package_name>/all**

**Description:** Returns all forms for a specified package

**Path Parameters:**

- `package_name` (string): The unique identifier of the application package

**Query Parameters:**
- `active` (String, optional): Filter forms by active status [active, inactive]

**Responses:**
- **200** - List of all forms for the specified package
- **404** - Package not found or no active form found
- **500** - Internal Server Error

---

### 5. Get All Forms
**GET /forms/all**

**Description:** Returns all forms, optionally filtered by status

**Query Parameters:**
- `active` (String, optional): Filter forms by active status [active, inactive]

**Responses:**
- **200** - List of all forms
- **400** - Invalid status parameter
- **404** -  No forms found
- **500** - Internal Server Error

---

### 6. Activate Form
**PUT /forms/<form_id>/activate**

**Description:** Updates the active status of a form. Allows only one active form for a package.

**Path Parameters:**
   - `form_id` (String): The unique identifier of the form

**Request body:**
```json
{
  "is_active": true
}
```
**Responses:**
- **200** - Status updated successfully
- **400** - Missing or invalid parameter
- **404** - Form not found
- **500** - Internal Server Error

---

### 7. Search Forms
**GET /forms/search**

**Description:** Searches forms using optional filters: package_name, status, title, and type.
  
**Query Parameters:**
   - `package_name` (String, optional): Filter by package name
   - `title` (String, optional): Search in form title
   - `form_type` (String, optional): Filter by form type [rating, free_text, rating_text]
   - `active` (String, optional): Filter by active status [active, inactive]

**Responses:**
- **200** - List of matching forms
- **500** - Internal Server Error

---
<br>

### <ins>Feedback Submission and Analysis</ins>

### 1. Submit Feedback
**POST /feedback**

**Description:** Submits new user feedback
 
**Request body:**
```json
{
  "app_version": "1.0",
  "device_info": "Pixel 6",
  "form_id": "string",
  "message": "Feedback input from the user",
  "package_name": "com.example.myapp",
  "rating": 3,
  "user_id": "user123"
}
```

**Responses:**
- **201** - Feedback submitted successfully
- **400** - Invalid feedback data
- **404** - No active form found with the provided form id
- **500** - Internal Server Error

---

### 2. Get Package Feedback
**GET /feedback/<package_name>**

**Description:** Gets all feedback for a package

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package

**Query Parameters:**
- `form_id` (String, optional): The unique identifier of the form

**Responses:**
- **200** - List of all feedbacks
- **404** - Package not found
- **500** - Internal Server Error

---

### 3. Get Feedback Details
**GET /feedback/<package_name>/<feedback_id>**

**Description:** Gets details of a specific feedback submission

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package
   - `feedback_id` (String): The unique identifier of the feedback submission

**Responses:**
- **200** - Feedback details
- **404** - Feedback not found
- **500** - Internal Server Error

---

### 4. Get User Feedback
**GET /feedback/<package_name>/user/<user_id>**

**Description:** Gets all feedback from a specific user for a package

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package
   - `user_id` (String): The unique identifier of the user

**Responses:**
- **200** - List of all feedbacks of the user for the package
- **404** - Package not found
- **500** - Internal Server Error

---

### 5. Get Average Rating
**GET /feedback/<package_name>/average-rating**

**Description:** Gets average rating for a package (and optionally for form id)

**Path Parameters:**
- `package_name` (String): The unique identifier of the application package

**Query Parameters:**
- `form_id` (String, optional): The unique identifier of the form

**Responses:**
- **200** - Average-rating of all package's feedback
- **404** - Package or form not found
- **500** - Internal Server Error

---

### 6. Get Feedback Statistics
**GET /feedback/<package_name>/stats**

**Description:** Gets feedback statistics (count, average rating, rating breakdown)  for a package (and optionally for form id)

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package

**Query Parameters:**
- `form_id` (String, optional): The unique identifier of the form

**Responses:**
- **200** - Successfully returned statistics
- **404** - Package or form not found
- **500** - Internal Server Error

---

### 7. Search Feedback
**GET /feedback/<package_name>/search**

**Description:** Searches feedback by message content

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package

**Query Parameters:**
   - `query` (String, optional): Search term within feedback messages

**Responses:**
- **200** - List of feedbacks that contain the search term
- **404** - Package not found
- **500** - Internal Server Error

---

### 8. Get Recent Feedback
**GET /feedback/<package_name>/recent**
 
**Description:** Gets most recent feedback submissions

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package

**Query Parameters:**
- `form_id` (String, optional): The unique identifier of the form
 - `limit` (Integer, optional): Number of recent items to return (default: 10)

**Responses:**
- **200** - List of recent feedbacks
- **404** - Package not found
- **500** - Internal Server Error

---

### 9. Delete Feedback
**DELETE /feedback/<package_name>/<feedback_id>**
 
**Description:** Deletes a specific feedback

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package
   - `feedback_id` (String): The unique identifier of the feedback submission

**Responses:**
 - **200** - Feedback deleted successfully
- **404** - Feedback not found
- **500** - Internal Server Error

---

### 10. Delete Form Feedback
**DELETE /feedback/<package_name>/form/<form_id>**
 
**Description:** Deletes all feedback for a specific form

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package
   - `form_id` (String): The unique identifier of the form

**Responses:**
- **200** - All feedbacks for the form in the package deleted successfully
- **404** - Package or form not found
- **500** - Internal Server Error

---

### 11. Delete All Package Feedback
**DELETE /feedback/<package_name>**
 
**Description:** Deletes all feedback for a package

**Path Parameters:**
   - `package_name` (String): The unique identifier of the application package

**Responses:**
- **200** - All feedbacks for the package deleted successfully
- **404** - Package not found
- **500** - Internal Server Error

---

## Form Types

The system supports three types of feedback forms:
- `rating`: Allows users to provide a rating from 1-5
- `free_text`: Allows users to provide written feedback
- `rating_text`: Combines rating and text feedback

---

## API Documentation

API documentation is available through Swagger UI when the server is running:
http://localhost:8088/apidocs/


## Deployment

This application is configured for deployment on Vercel. The `vercel.json` file includes the necessary configuration.


## Prerequisites

- Python 3.9+
- MongoDB Atlas account (or MongoDB instance)
- Virtual environment (recommended)


## Setup and Installation

1. Clone the repository:
	```
	git clone <repository-url> cd feedback-backend
	```

2. Create and activate a virtual environment:
	```
	python -m venv venv source venv/bin/activate # On Windows: venv\Scripts\activate
	```

3. Install dependencies:
	```
	pip install -r requirements.txt
	```

4. Create a `.env` file with the following variables:
	```
	DB_CONNECTION_STRING=<your-mongodb-connection-string>
	DB_NAME=<your-database-name>
	DB_USERNAME=<your-mongodb-username>
	DB_PASSWORD=<your-mongodb-password>
	```

5. Run the application:
	```
	python app.py
	```
	The server will start on port 8088 by default (configurable via PORT environment variable).

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
