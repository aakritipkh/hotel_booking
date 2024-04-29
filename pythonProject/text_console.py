# Implements a text-based console interface for the hotel booking system
from common_functionalities import HotelManager, RoomManager, ReservationManager, Validator


# This class serves as the interface for users to interact with the hotel booking system via the console
class TextConsole:
    # Initialises a 'HotelManager' instance along with 'RoomManager', 'ReservationManager', and 'Validator' instances
    # from the 'common_functionalities' module
    def __init__(self):
        self.hotel_manager = HotelManager(RoomManager("hotel_room.csv", Validator()),
                                          ReservationManager("reservations.csv"),
                                          Validator())
        self.validator = Validator()

    # This method presents the main menu options to the user
    def display_menu(self):
        print("Thank you for choosing Aakriti's Hotel Booking System.")
        print("To complete your reservation, please provide the following details:")
        print("--------------------------------------------------------------")
        print("1. Make a reservation")
        print("2. Cancel a reservation")
        print("3. Exit")

    # This method handles the process of booking a room in the hotel
    #  Prompts the user to enter various details required for making a reservation, such as customer name, number of
    #  people, check-in date, and check-out date. It ensures that the provided inputs are valid using the Validator
    #  instance. Handles potential errors that may occur during the reservation process, such as invalid inputs or
    #  unexpected exceptions. It catches these errors and provides appropriate error messages to the user.
    def book_room(self):
        while True:
            try:
                print("Booking a room...")
                print("Please provide the following details to make a reservation:")

                # Gathers reservation details from the user
                while True:
                    customer_name = input("Enter your full name: ")
                    try:
                        self.validator.validate_name_filled(customer_name)  # Validates customer name
                        break
                    except ValueError as ve:
                        print(f"Error: {ve}")
                if customer_name:  # Checks if the customer name is not empty
                    print("--------------------------------------------------------------")
                    print(f"Hello, {customer_name}.")

                while True:
                    try:
                        num_people = int(input("Enter the number of people staying (1-4): "))
                        self.validator.validate_num_people(num_people)  # Ensures it's a valid number of people
                        break
                    except ValueError as ve:
                        print(f"Error: {ve}")
                print("--------------------------------------------------------------")

                # Loops to ask for valid check-in date
                # Gathers the check-in date
                while True:
                    check_in_date = input("Enter the check-in date (DD/MM/YYYY): ")
                    try:
                        self.validator.validate_date_format(check_in_date)
                        self.validator.validate_check_in(check_in_date)
                        break
                    except ValueError as ve:
                        print(f"Error: {ve}")
                print("--------------------------------------------------------------")

                # Loops to ask for valid check-out date
                while True:
                    check_out_date = input("Enter the check-out date (DD/MM/YYYY): ")
                    try:
                        self.validator.validate_date_format(check_out_date)
                        self.validator.validate_date_range(check_in_date, check_out_date)
                        break
                    except ValueError as ve:
                        print(f"Error: {ve}")
                print("--------------------------------------------------------------")

                # Gets available room options
                available_rooms = self.hotel_manager.room_manager.filter_room_options(check_in_date,
                                                                                      check_out_date,
                                                                                      num_people,
                                                                                      self.hotel_manager
                                                                                      .reservation_manager)

                if not available_rooms:
                    # If there are no rooms available, it says so to the user and asks if they want to book for
                    # another date
                    print("We apologize, but there are no available rooms for the selected dates.")
                    print("Please consider choosing different dates or contacting our support team for assistance.")
                    check_another_date = input("Do you want to check availability for another date? (yes/no): ").lower()
                    if check_another_date == "yes":
                        continue
                    else:
                        break

                # Displays available room options to the user
                print("Available Room Options:")
                print("-----------------------")
                for i, room in enumerate(available_rooms, start=1):
                    print(f"{i}. Room Type: {room['room_type']}, Price per Night: ${room['price_per_night']:.2f}")

                # Lets the user choose a room option
                choice = self.get_valid_choice("Enter the number of the room you want to book: ", len(available_rooms))

                # Makes reservation
                selected_room = available_rooms[choice - 1]
                reference_number, total_price = self.hotel_manager.make_reservation(customer_name, num_people,
                                                                                    check_in_date, check_out_date,
                                                                                    selected_room)

                # Displays reservation details and receipt
                print("--------------------------------------------------------------")
                print("Booking your room...")
                print("Please wait while we process your reservation.")
                print("--------------------------------------------------------------")
                self.display_receipt(reference_number, customer_name, selected_room['room_type'], check_in_date,
                                     check_out_date, total_price)

                # Asks for confirmation
                self.confirm_reservation(reference_number, customer_name, selected_room['room_type'],
                                         check_in_date, check_out_date, total_price)
                break  # Breaks the main loop if reservation is successful

            except ValueError as ve:
                print(f"Error: {ve}")
            except Exception as e:
                print(f"An error occurred during reservation: {e}")

    # Gets the number input and validates the number using the validator method from HotelManager class
    def get_valid_num_people(self):
        while True:
            try:
                num_people = int(input("Enter number of people (1-4): "))
                self.hotel_manager.validator.validate_num_people(num_people)
                return num_people
            except ValueError:
                print("Error: Please enter a valid number between 1 and 4.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                # I tried to error handle when user enters non integer value but I couldn't do it

    # Gets the date and validates the date format using the validator method from the HotelManager class
    def get_valid_date(self, prompt):
        while True:
            try:
                date_str = input(prompt)
                self.hotel_manager.validator.validate_date_format(date_str)
                return date_str
            except ValueError as ve:
                print(f"Error: {ve}")

    # Takes the valid choice for room options given to the user
    def get_valid_choice(self, prompt, max_value):
        while True:
            try:
                choice = int(input(prompt))
                if 1 <= choice <= max_value:
                    return choice
                else:
                    print("Invalid choice. Please enter a number corresponding to the room.")
            except ValueError:
                print("Error: Please enter a valid number.")

    # Displays the receipt using the method generate receipt from HotelManager class
    def display_receipt(self, reference_number, customer_name, room_type, check_in_date, check_out_date, total_price):
        receipt = self.hotel_manager.generate_receipt(reference_number, customer_name, room_type, check_in_date,
                                                      check_out_date, total_price)
        print("--------------------------------------------------------------")
        print("Reservation Details:")
        print(receipt)

    # Takes confirmation from the user for the reservation and again displays receipt using the above display receipt
    # method
    def confirm_reservation(self, reference_number, customer_name, room_type, check_in_date, check_out_date,
                            total_price):
        print("REFUND POLICY: Our hotel has a 70% refund policy in case of cancellation.")
        confirm = input("Confirm reservation (yes/no)? ").lower()
        if confirm == "yes":
            print("Reservation confirmed.")
            # Displays receipt
            self.display_receipt(reference_number, customer_name, room_type, check_in_date,
                                 check_out_date, total_price)
        else:
            print("Reservation canceled.")

    # This method cancels the room, first reads the reservation using HotelManager class and if they exist then shows
    # booking receipt and asks for confirmation for cancellation. It also shows the refund amount after the cancellation
    # is successful
    def cancel_room(self):
        try:
            reference_number = input("Enter the reference number of the reservation to cancel: ")
            # Using the ReservationManager instance to retrieve the reservation details
            reservations = self.hotel_manager.reservation_manager.read_reservation_data()
            reservation = None
            for res in reservations:
                if res[0] == reference_number:
                    reservation = res
                    break

            if reservation:
                # Extracts reservation details
                reference_number, customer_name, room_type, check_in_date, check_out_date, total_price = reservation

                # Calculates refund amount
                total_price = float(total_price)
                refund_amount = self.hotel_manager.calculate_refund(total_price)

                # Generates receipt and refund policy
                receipt = self.hotel_manager.generate_receipt(reference_number, customer_name, room_type,
                                                              check_in_date, check_out_date, total_price)
                refund_policy = (f"Refund Policy: You are eligible for a 70% refund of the total price"
                                 f" (${total_price:.2f}).\n")

                # Asks for confirmation
                print("Reservation Details:")
                print(receipt)
                print(refund_policy)
                confirmation = input("Do you want to cancel this reservation? (yes/no): ").strip().lower()
                if confirmation == "yes":
                    # Performs cancellation
                    result = self.hotel_manager.cancel_reservation(reference_number)
                    if result:
                        print("Cancellation successful for {reference_number}"
                              "\nHope we see you again!")
                        print(f"Your refund amount is ${refund_amount:.2f}")
                    else:
                        print("Cancellation failed.")
                else:
                    print("Cancellation canceled.")
            else:
                print("Reservation not found.")
        except Exception as e:
            print(f"Error: {e}")

    # This method arranges the overall flow of the console interface by displaying the menu, accepting user input,
    # and executing corresponding actions based on the user's choice.
    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")
            if choice == "1":
                self.book_room()
            elif choice == "2":
                self.cancel_room()
            elif choice == "3":
                print("Exiting program...")
                print("Thank you for using Aakriti's Hotel Booking System. Have a great day!")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    text_console = TextConsole()
    text_console.run()
