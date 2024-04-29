# This file serves as the "common_functionalities" module for my hotel management system project.
# It contains essential classes and functions that are shared across different components of the application, both for
# the text based console and TKinter based GUI.
# The code are organised into classes including validator where  each class focuses on a
# specific aspect of hotel management.
# While I was doing this coursework, after some trial and error I realised that since I am using this class in both
# text based console and GUI, for reusability, I am raising custom exceptions or returning
# error messages as strings within the HotelManager class. This ensures modularity and maintainability,
# allowing me to handle exceptions or messages appropriately in both console and GUI code without affecting
# the quality of my text console.

import csv
import random
import string
from datetime import datetime

# RoomManager class manages rooms in the hotel
class RoomManager:
    # Upon initialization, the RoomManager reads room data from a CSV file and stores it in a dictionary.
    def __init__(self, file_name, validator):
        self.rooms = self.read_room_data(file_name)
        self.validator = validator

    def read_room_data(self, file_name):
        # This method reads room data from a CSV file and organizes it into a dictionary.
        rooms = {}
        try:
            with open(file_name, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skips header row
                # Extracts room details from each row
                for row in reader:
                    room_id, room_type, max_people, price_per_night = row
                    room_id = int(room_id)
                    max_people = int(max_people)
                    price_per_night = float(price_per_night)
                    # Stores room details in the dictionary
                    if room_type not in rooms:
                        rooms[room_type] = {'room_id': room_id, 'price_per_night': price_per_night,
                                            'max_people': max_people}
                    else:
                        if price_per_night < rooms[room_type]['price_per_night']:
                            rooms[room_type] = {'room_id': room_id, 'price_per_night': price_per_night,
                                                'max_people': max_people}
            return rooms
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: File '{file_name}' not found.") from e
        except Exception as e:
            raise Exception(f"An error occurred while reading the file '{file_name}': {e}") from e

    def filter_room_options(self, check_in_date, check_out_date, num_people, reservation_manager):
        # Ensures that check_in_date and check_out_date are in the correct format
        self.validator.validate_date_format(check_in_date)
        self.validator.validate_date_format(check_out_date)

        # Converts check_in_date and check_out_date to datetime.date objects
        check_in_date = datetime.strptime(check_in_date, '%d/%m/%Y').date()
        check_out_date = datetime.strptime(check_out_date, '%d/%m/%Y').date()

        # Retrieves reservations
        reservations = reservation_manager.read_reservation_data()

        # Filters available rooms using list comprehensions
        available_rooms = [{
            'room_number': i + 1,
            'room_id': room_info['room_id'],
            'room_type': room_type,
            'price_per_night': room_info['price_per_night']
        } for i, (room_type, room_info) in enumerate(self.rooms.items())
            if room_info['max_people'] >= num_people
            and room_type not in {res[2] for res in reservations
                                  if datetime.strptime(res[3], '%d/%m/%Y').date() <= check_out_date
                                  and datetime.strptime(res[4], '%d/%m/%Y').date() >= check_in_date}
        ]

        return available_rooms

# Manages hotel reservations
class ReservationManager:
    def __init__(self, file_name):
        self.file_name = file_name

    # Reads reservation data from csv file
    def read_reservation_data(self):
        reservations = []
        try:
            with open(self.file_name, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    reservations.append(row)
            return reservations
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: File '{self.file_name}' not found.") from e
        except Exception as e:
            raise Exception(f"An error occurred while reading the file '{self.file_name}': {e}") from e

    # Writes new reservations and cancels existing ones
    def write_reservation_data(self, reservations):
        try:
            with open(self.file_name, 'a', newline='') as file:
                existing_reservations = set()  # Stores existing reservations to filter duplicates
                # Reads existing reservations from the file
                with open(self.file_name, 'r', newline='') as read_file:
                    reader = csv.reader(read_file)
                    next(reader)  # Skip header row
                    for row in reader:
                        existing_reservations.add(tuple(row[
                                                        :5]))
                        # Includes only reference number, customer name, room type, check-in date, and check-out date

                # Writes only unique reservations to the file
                writer = csv.writer(file)
                for reservation in reservations:
                    if tuple(reservation[:5]) not in existing_reservations:
                        writer.writerow(reservation)
                        existing_reservations.add(
                            tuple(reservation[:5]))  # Add the new reservation to existing reservations
        except Exception as e:
            raise Exception(f"An error occurred while saving reservation data: {e}") from e

    # Removes a reservation based on the provides reference number
    def cancel_reservation(self, reference_number):
        reservations = self.read_reservation_data()
        updated_reservations = []
        found = False
        for reservation in reservations:
            if reservation[0] == reference_number:
                found = True
            else:
                updated_reservations.append(reservation)
        if found:
            try:
                with open(self.file_name, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        ['Reference Number', 'Customer Name', 'Room Type', 'Check In', 'Check Out', 'Total Price'])
                    writer.writerows(updated_reservations)
                return True
            except Exception as e:
                raise ValueError(f"An error occurred while canceling reservation {reference_number}: {e}")
        else:
            raise ValueError("Reservation not found.")

# This class is for validating different aspects of user input
class Validator:
    # Validates that number of people are within 1 to 4
    def validate_num_people(self, num_people):
        try:
            num_people = int(num_people)
        except ValueError:
            raise ValueError("Invalid input. Please enter a valid number.")

        if not 1 <= num_people <= 4:
            raise ValueError("Number of people must be between 1 and 4.")

    # Validates that dates are in the correct chosen format which I have chosen is DD/MM/YYYY for this program
    def validate_date_format(self, date_str):
        try:
            datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Please use the format dd/mm/yyyy.")

    # Validates that check out date is after the check in date
    def validate_date_range(self, check_in_date, check_out_date):
        self.validate_date_format(check_in_date)
        self.validate_date_format(check_out_date)

        check_in = datetime.strptime(check_in_date, '%d/%m/%Y').date()
        check_out = datetime.strptime(check_out_date, '%d/%m/%Y').date()

        if check_out <= check_in:
            raise ValueError("Check-out date must be after the check-in date.")

    # This ensures that the provided check in date is not in the past
    def validate_check_in(self, check_in_date):
        self.validate_date_format(check_in_date)

        today = datetime.now().date()
        if datetime.strptime(check_in_date, '%d/%m/%Y').date() < today:
            raise ValueError("Check-in date cannot be in the past.")

    # This method validates that the customer's name is not empty
    def validate_name_filled(self, name):
        if not name.strip():
            raise ValueError("Name cannot be empty.")

# This class is for managing hotel operations
class HotelManager:
    # Initialises a 'HotelManager' object with instances of 'RoomManager;, 'ReservationManager', and 'Validator'
    def __init__(self, room_manager, reservation_manager, validator):
        self.room_manager = room_manager
        self.reservation_manager = reservation_manager
        self.validator = validator

    # Validates the input data such as the number of people, date formats, date range, check-in and the customer name
    # using the 'Validator' instance. Wraps the reservation process in a try-except block to handle any exceptions
    # that might occur during the reservation process. If an exception occurs, it raises the exception to be
    # handled at a higher level
    def make_reservation(self, customer_name, num_people, check_in_date, check_out_date, selected_room):
        try:
            # Validates input data
            self.validator.validate_num_people(num_people)
            self.validator.validate_date_format(check_in_date)
            self.validator.validate_date_format(check_out_date)
            self.validator.validate_date_range(check_in_date, check_out_date)
            self.validator.validate_check_in(check_in_date)
            self.validator.validate_name_filled(customer_name)

            # Generates a unique reference number for the reservation
            reference_number = self.generate_reference()

            # Calculates total price based on selected room and reservation dates
            total_price = float(self.calculate_total_price(selected_room['price_per_night'], check_in_date,
                                                           check_out_date))

            # Writes reservation data
            reservation_data = [reference_number, customer_name, selected_room['room_type'], check_in_date,
                                check_out_date, total_price]
            self.reservation_manager.write_reservation_data([reservation_data])

            return reference_number, total_price
        except Exception as e:
            raise e

    # This method generates a unique reference number for each reservation using a combination of uppercase letters
    # and digits
    def generate_reference(self):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(8))

    # This method is to calculate the total price for a reservation based on the selected room's price per night
    # and the duration of stay
    def calculate_total_price(self, price_per_night, check_in_date, check_out_date):
        check_in = datetime.strptime(check_in_date, '%d/%m/%Y').date()
        check_out = datetime.strptime(check_out_date, '%d/%m/%Y').date()
        num_nights = (check_out - check_in).days
        total_price = num_nights * price_per_night
        return float(total_price)

    # Cancels a reservation according to the given reference number
    def cancel_reservation(self, reference_number):
        # Read existing reservations data
        try:
            result = self.reservation_manager.cancel_reservation(reference_number)
            return result
        except ValueError as e:
            raise e

    # Generates a receipt for the reservation with the provided details
    def generate_receipt(self, reference_number, customer_name, room_type, check_in_date, check_out_date, total_price):
        receipt = f"Reference Number: {reference_number}\n"
        receipt += f"Customer Name: {customer_name}\n"
        receipt += f"Room Type: {room_type}\n"
        receipt += f"Check-in Date: {check_in_date}\n"
        receipt += f"Check-out Date: {check_out_date}\n"
        receipt += f"Total Price: ${total_price:.2f}\n"
        return receipt

    # Calculates the refund amount for the canceled reservation based on the total price
    def calculate_refund(self, total_price):
        return float(total_price * 0.7)
