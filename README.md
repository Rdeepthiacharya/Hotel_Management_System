# Project Title
Users can search for and book hotel rooms based on their preferences, dates, and room type. Users can also view photos of the hotel rooms and facilities to help them make an informed decision.

The backend of the application manages user authentication, hotel information, room availability, and booking transactions using FastAPI endpoints to interact with the SQL database. Users can create accounts, log in securely, and manage their bookings through the website.

The frontend interface allows users to easily navigate the website, search for hotels, view available rooms, and book their desired accommodation. The website also includes features such as filtering options, sorting by price or rating, and viewing reviews from other guests.

Overall, this website provides a convenient platform for users to find and book accommodations for their travel needs.

## Getting Started

To get started with this project, you will need to have the following installed on your system:
- Python 3
- An SQL server (DB Browser)

Once you have these installed, you can clone the repository and run the application on your local machine.

## Prerequisites

Before running the application, you will need to create an SQL database and configure the connection details in the config.py file. You can find this file in the backend directory.

## Running the Application

To run the application, follow these steps:
1. Clone the repository to your local machine.
2. Open a terminal and navigate to the backend directory.
3. Install the required dependencies using pip install -r requirements.txt.
4. Start the backend server using uvicorn main:app --reload.
5. Open a web browser and navigate to http://localhost:8000/ to access the application.

## Features

The application offers the following features:
- User-friendly interface
- Easy navigation
- Secure login and registration system
- CRUD operations on data
- Responsive design

## Built With

- FastAPI framework for the backend
- SQL server for the database
- HTML, CSS, and JavaScript for user interface

## Authors

- [Deepthi G Acharya ](https://github.com/Rdeepthiacharya)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
