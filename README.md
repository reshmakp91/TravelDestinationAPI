# Travel Destination API

## Description
This project is an API for managing and showcasing travel destinations. It provides functionality to create, retrieve, update, and delete destinations, making it easy for users to explore various travel options.

## Key Features
- **CRUD operations** for travel destinations
- Search functionality to find destinations by name, location, or other criteria
- RESTful API for easy integration with frontend applications

## Technologies Used
- Python
- Django
- Django REST Framework
- PostgreSQL/MySQL (depending on your setup)
- HTML/CSS (if applicable)

## API Endpoints
### Destinations
- localhost/register : Register new user
- localhost/login : Login form
- localhost/destinations/: Create and list destinations
- localhost/destinations/<int:id>/: Retrieve, update and delete a destination by ID

### Additional Views
- http://localhost:8000/: Render the home page

## Installation
1. Clone the repository: git clone https://github.com/reshmakp91/TravelDestinationAPI.git
2. Navigate into the project directory: cd TravelDestinationAPI
3. Install the required packages: pip install -r requirements.txt
4. Run database migrations (if using Django): python manage.py migrate
6. Start the application: python manage.py runserver
   
## Usage
You can use tools like Postman or cURL to interact with the API endpoints.

## License
This project is open-source and available for educational and project development purposes.
