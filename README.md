# Cricket-Match-Ticket-Booking-System
A Python CLI application for cricket ticket booking with user authentication, allowing users to register, log in, browse cities/pavilions, book, and cancel tickets. It uses MySQL for data storage, managing users, sports event details, and bookings.
The system features robust user authentication, allowing new users to create accounts with unique phone numbers and emails, complete with a simulated OTP verification process. Existing users can simply log in. For ticket booking, users can first view a list of available cities , then select a city to see detailed stadium and pavilion information, including ticket prices. After choosing a pavilion and specifying the number of tickets, the system calculates the total cost and records the booking in the database. Users also have the functionality to cancel tickets, verifying their identity through their associated email.

The application's data is managed in a MySQL database named 

project. This database consists of three key tables: 

users, sports, and bookings. The 

users table stores user registration details like full_name, phone_number, email, password, and state. The 

sports table holds information about cricket venues, including city_name, ground_name, pavilion_name, and ticket_price. Finally, the 

bookings table records all ticket transactions, linking to users and detailing the city, stadium_name, pavilion_name, num_tickets, and total_cost. Basic input validation for phone numbers and email formats ensures data integrity.


To set up the project, a MySQL server is required. Users need to create the 

project database and populate it with the provided SQL schema and initial sports data. The 

mysql-connector-python library is a prerequisite and must be installed. The 

Cricket.py file also requires updating with the user's MySQL root password for database connection
