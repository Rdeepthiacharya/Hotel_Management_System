# Project Title
Users can book rooms based on their preferences, dates, and room type. Users can also view photos of the hotel rooms and book other facilities to help them make an informed decision.

The backend of the application manages user authentication, hotel information, room availability, and booking transactions using FastAPI endpoints to interact with the SQLite database. Users can create accounts, log in securely, and manage their bookings through the website.

The frontend interface allows users to easily navigate the website, search for rooms and facilities, view available rooms and, and book their desired accommodations. 

Overall, this website provides a convenient platform for users to find and book accommodations for their travel needs.

## Getting Started

To get started with this project, you will need to have the following installed on your system:
- Python 3
- DB Browser(SQLite)
- VS Code (or any other application of your choice)

Once you have these installed, you can clone the repository and run the application on your local machine.

## Prerequisites

Before running the application, you will need to create an SQLite database and configure the connection details in the dbcontroller.py file. You can find this file in the backend directory.

## Running the Application

To run the application, follow these steps:
1. Clone the repository to your local machine.
2. Open a terminal and navigate to the backend directory.
3. Install the required dependencies using pip install -r requirements.txt.
4. Start the backend server using python -m uvicorn app:app --reload.
5. Open a web browser and navigate to http://localhost:8000/ to access the application.

## Features

The application offers the following features:
- User-friendly interface
- Easy navigation
- Secure login and registration system
- CRUD operations on data
- Responsive design

## Built With

- Python FastAPI framework for the backend
- SQLite for the database
- HTML, CSS, and JavaScript for user interface

## License

This project is licensed under the MIT License - see the [LICENSE]([LICENSE](https://github.com/Rdeepthiacharya/Hotel_Management_System/commit/94ef675ff57824d8cd4e2d9e4ba37f7e0d801f00)https://github.com/Rdeepthiacharya/Hotel_Management_System/commit/94ef675ff57824d8cd4e2d9e4ba37f7e0d801f00) file for details.
