import mysql.connector as sqltor
import random
import re # For email validation

# --- Database Connection Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Noxious@07', # <--- IMPORTANT: Enter your MySQL root password on this line
    'database': 'project'
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = sqltor.connect(**DB_CONFIG)
        return conn
    except sqltor.Error as err:
        print(f"Error connecting to MySQL: {err}")
        print(f"SQLSTATE: {err.sqlstate}")
        return None

def validate_phone_number(phone_num):
    """Validates if the phone number is 10 digits."""
    return len(phone_num) == 10 and phone_num.isdigit()

def validate_email(email):
    """Validates if the email format is correct."""
    # Basic regex for email validation
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def create_account(conn, cursor):
    """Handles new user registration."""
    print("\n--- CREATE NEW ACCOUNT ---")
    while True:
        full_name = input("ENTER YOUR FULL NAME: ").strip()
        if full_name:
            break
        else:
            print("Full name cannot be empty.")

    while True:
        phone_number = input("ENTER YOUR PHONE NO (10 digits): ").strip()
        if validate_phone_number(phone_number):
            break
        else:
            print("Invalid phone number. Please enter a 10-digit number.")

    while True:
        email = input("ENTER YOUR EMAIL ID: ").strip()
        if validate_email(email):
            break
        else:
            print("Invalid email format.")

    while True:
        password = input("CREATE YOUR PASSWORD: ").strip()
        if password:
            break
        else:
            print("Password cannot be empty.")

    state = input("ENTER YOUR STATE: ").strip()

    try:
        # Check if phone number or email already exists
        cursor.execute("SELECT * FROM users WHERE phone_number = %s OR email = %s", (phone_number, email))
        if cursor.fetchone():
            print("\nAccount with this phone number or email already exists. Please login or use different credentials.")
            return False, None # Return False for success and None for user_id
        
        # Simulate OTP (in a real app, send actual OTP)
        otp_sent = random.randint(1000, 9999)
        print(f"\nOTP SENT TO {phone_number} AND {email}: {otp_sent} (For demonstration purposes)")
        entered_otp = int(input("ENTER THE OTP NO: "))

        if entered_otp == otp_sent:
            sql = "INSERT INTO users (full_name, phone_number, email, password, state) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (full_name, phone_number, email, password, state))
            conn.commit()
            print("\n-------YOUR ACCOUNT IS CREATED SUCCESSFULLY-------")
            
            # Fetch the newly created user's ID
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            user_id = cursor.fetchone()[0]
            return True, user_id
        else:
            print("Incorrect OTP. Account creation failed.")
            return False, None

    except sqltor.Error as err:
        print(f"Error creating account: {err}")
        print(f"SQLSTATE: {err.sqlstate}")
        conn.rollback()
        return False, None

def login(conn, cursor):
    """Handles user login."""
    print("\n--- LOGIN ---")
    email = input("ENTER YOUR EMAIL ID: ").strip()
    password = input("ENTER YOUR PASSWORD: ").strip()

    try:
        sql = "SELECT user_id, full_name, phone_number, state FROM users WHERE email = %s AND password = %s"
        cursor.execute(sql, (email, password))
        user_data = cursor.fetchone()

        if user_data:
            print("\n-------LOGIN SUCCESSFUL-------")
            user_id, full_name, phone_number, state = user_data
            return user_id, full_name, phone_number, email, state
        else:
            print("\nInvalid email or password. Please try again.")
            return None, None, None, None, None
    except sqltor.Error as err:
        print(f"Error during login: {err}")
        print(f"SQLSTATE: {err.sqlstate}")
        return None, None, None, None, None

def display_cities(cursor):
    """Displays available cities for booking."""
    print("\n------------THESE ARE THE CITIES------------")
    query = "SELECT DISTINCT city_name FROM sports ORDER BY city_name"
    cursor.execute(query)
    cities = [city[0] for city in cursor.fetchall()]
    for city in cities:
        print(f"- {city.capitalize()}")
    return cities

def display_pavilions(cursor, city):
    """Displays pavilions for a given city."""
    print(f"\n------------Pavilions in {city.capitalize()}------------")
    query = "SELECT ground_name, pavilion_name, ticket_price FROM sports WHERE city_name = %s ORDER BY ground_name, pavilion_name"
    cursor.execute(query, (city,))
    pavilions_data = cursor.fetchall()
    
    current_stadium = ""
    stadium_pavilions = {}
    for ground, pavilion, price in pavilions_data:
        if ground != current_stadium:
            print(f"\nStadium: {ground}")
            current_stadium = ground
        print(f"  - {pavilion} (Price: Rs. {price:.2f})")
        stadium_pavilions[pavilion.lower()] = {'ground': ground, 'price': price}
    return stadium_pavilions

def book_ticket(conn, cursor, user_id, user_name, user_phone, user_email, user_state):
    """Handles the ticket booking process."""
    ch10 = 'y'
    while ch10.lower() == 'y':
        cities = display_cities(cursor)
        
        chosen_city = input("\nEnter the city you want (e.g., 'banglore'): ").strip().lower()
        if chosen_city not in cities:
            print("Invalid city. Please choose from the list.")
            continue

        pavilions_info = display_pavilions(cursor, chosen_city)
        
        chosen_pavilion = input("Enter the Pavilion you want (e.g., 'anil kumble pavilion'): ").strip().lower()
        
        if chosen_pavilion not in pavilions_info:
            print("Invalid pavilion. Please choose from the list.")
            continue

        pavilion_details = pavilions_info[chosen_pavilion]
        stadium_name = pavilion_details['ground']
        ticket_price = pavilion_details['price']

        print(f"The cost for one ticket in {chosen_pavilion} is Rs. {ticket_price:.2f}")
        try:
            num_tickets = int(input("Enter The No. Of Tickets Required: "))
            if num_tickets <= 0:
                print("Number of tickets must be positive.")
                continue
        except ValueError:
            print("Invalid input. Please enter a number for tickets.")
            continue

        total_cost = num_tickets * ticket_price

        print("\n****These Are Your Ticket Details****")
        print(f"Name: {user_name}")
        print(f"Phone Number: {user_phone}")
        print(f"State: {user_state}")
        print(f"City: {chosen_city.capitalize()}")
        print(f"Stadium Name: {stadium_name}")
        print(f"Pavilion Name: {chosen_pavilion.title()}")
        print(f"Total No Of Tickets: {num_tickets}")
        print(f"Total Cost For the Tickets: Rs. {total_cost:.2f}")
        print(f"The Copy Of The Ticket Has Been Sent To Your Mail: {user_email}")

        try:
            sql_insert_booking = """
            INSERT INTO bookings (user_id, city, stadium_name, pavilion_name, num_tickets, total_cost)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert_booking, (user_id, chosen_city, stadium_name, chosen_pavilion, num_tickets, total_cost))
            conn.commit()
            print("\nBooking successful! Your booking has been recorded.")
        except sqltor.Error as err:
            print(f"Error saving booking: {err}")
            print(f"SQLSTATE: {err.sqlstate}")
            conn.rollback()

        ch10 = input("\nDo You Want To Continue Booking? Yes(y)/No(n): ").strip()
    print("Thank you for booking!")

def cancel_ticket(conn, cursor, user_id):
    """Handles ticket cancellation."""
    print("\n--- CANCEL TICKET ---")
    user_email_input = input("ENTER YOUR EMAIL ID used for booking: ").strip()

    try:
        # Verify the booking belongs to the logged-in user and the provided email
        sql_check_booking = """
        SELECT booking_id, city, stadium_name, pavilion_name, num_tickets, total_cost
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        WHERE b.user_id = %s AND u.email = %s
        """
        cursor.execute(sql_check_booking, (user_id, user_email_input))
        bookings_to_cancel = cursor.fetchall()

        if not bookings_to_cancel:
            print("No bookings found for this email associated with your account.")
            return

        print("\n--- Your Current Bookings ---")
        for i, booking in enumerate(bookings_to_cancel):
            print(f"{i+1}. Booking ID: {booking[0]}, City: {booking[1].capitalize()}, Stadium: {booking[2]}, Pavilion: {booking[3].title()}, Tickets: {booking[4]}, Cost: Rs. {booking[5]:.2f}")
        
        try:
            choice = int(input("Enter the number of the booking you wish to cancel: "))
            if 1 <= choice <= len(bookings_to_cancel):
                booking_id_to_cancel = bookings_to_cancel[choice-1][0]
                confirm = input(f"Are you sure you want to cancel booking ID {booking_id_to_cancel}? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    sql_delete = "DELETE FROM bookings WHERE booking_id = %s AND user_id = %s"
                    cursor.execute(sql_delete, (booking_id_to_cancel, user_id))
                    conn.commit()
                    print(f"\nBooking ID {booking_id_to_cancel} has been cancelled successfully.")
                else:
                    print("Cancellation aborted.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    except sqltor.Error as err:
        print(f"Error cancelling ticket: {err}")
        print(f"SQLSTATE: {err.sqlstate}")
        conn.rollback()

def main():
    """Main function to run the cricket booking system."""
    conn = get_db_connection()
    if not conn:
        print("Exiting application due to database connection error.")
        return

    cursor = conn.cursor()
    current_user_id = None
    current_user_name = None
    current_user_phone = None
    current_user_email = None
    current_user_state = None

    print("\n********************WELCOME TO SPORTS ARENA***********************")

    while True:
        acc_choice = input("\nDO YOU HAVE AN ACCOUNT (Y/N)? ").strip().lower()

        if acc_choice == 'y' or acc_choice == 'yes':
            current_user_id, current_user_name, current_user_phone, current_user_email, current_user_state = login(conn, cursor)
            if current_user_id:
                break # Exit loop if login is successful
        elif acc_choice == 'n' or acc_choice == 'no':
            success, user_id = create_account(conn, cursor)
            if success:
                # After successful creation, log them in automatically
                cursor.execute("SELECT full_name, phone_number, email, state FROM users WHERE user_id = %s", (user_id,))
                user_data = cursor.fetchone()
                current_user_id, current_user_name, current_user_email, current_user_state = user_data
                current_user_phone = user_data[1] # Phone number is second in the tuple
                break # Exit loop if account created and user data fetched
        else:
            print("Invalid choice. Please enter 'Y' or 'N'.")

    # Main menu after successful login/registration
    while True:
        print("\nWhat Do You Want To Do?")
        print("1. Book Ticket")
        print("2. Cancel Ticket")
        print("3. Exit")

        try:
            choice = int(input("Enter your choice (1, 2, or 3): "))
            if choice == 1:
                book_ticket(conn, cursor, current_user_id, current_user_name, current_user_phone, current_user_email, current_user_state)
            elif choice == 2:
                cancel_ticket(conn, cursor, current_user_id)
            elif choice == 3:
                print("\nThank you for using Sports Arena! Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # Close the connection when done
    if conn:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
