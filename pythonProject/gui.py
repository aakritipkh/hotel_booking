# This file is for the code for GUI application for my hotel booking system implemented using the Tkinter library
# It imports classes from common_functionalities to create the application
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
from common_functionalities import HotelManager, RoomManager, ReservationManager, Validator

class HotelManagementApp:
    def __init__(self, master):
        # Initialises the GUI window (master)
        self.master = master
        master.title("Hotel Management System")

        # Load the logo image
        self.logo_image = tk.PhotoImage(file="logo.png")  # Replace "logo.png" with the path to your logo image

        # Initialises RoomManager, ReservationManager, and Validator
        self.room_manager = RoomManager("hotel_room.csv", Validator())
        self.reservation_manager = ReservationManager("reservations.csv")
        self.validator = Validator()

        # Initialises HotelManager with RoomManager, ReservationManager, and Validator
        self.hotel_manager = HotelManager(self.room_manager, self.reservation_manager, self.validator)

        # Creates labels and entry widgets for reservation details
        tk.Label(master, image=self.logo_image).grid(row=0, columnspan=2)  # Display the logo

        # Label and Entry widget for Customer Name
        tk.Label(master, text="Customer Name:").grid(row=1, column=0)
        self.customer_name_entry = tk.Entry(master)
        self.customer_name_entry.grid(row=1, column=1)

        # Label and Entry widget for Check-in Date
        tk.Label(master, text="Check-in Date (DD/MM/YYYY):").grid(row=2, column=0)
        self.check_in_entry = ttk.Entry(master)
        self.check_in_entry.grid(row=2, column=1)
        self.check_in_entry.insert(0, self.get_default_date())

        # Label and Entry widget for Check-out Date
        tk.Label(master, text="Check-out Date (DD/MM/YYYY):").grid(row=3, column=0)
        self.check_out_entry = ttk.Entry(master)
        self.check_out_entry.grid(row=3, column=1)
        self.check_out_entry.insert(0, self.get_default_date())

        # Label and Entry widget for Number of People
        tk.Label(master, text="Number of People:").grid(row=4, column=0)
        self.num_people_entry = tk.Entry(master)
        self.num_people_entry.grid(row=4, column=1)

        # Button to search for available rooms
        self.search_rooms_button = tk.Button(master, text="Search for Available Rooms", command=self.search_rooms)
        self.search_rooms_button.grid(row=5, columnspan=2)

        # Listbox to display available rooms
        self.room_listbox = tk.Listbox(master)
        self.room_listbox.grid(row=6, columnspan=2)

        # Button to book a room
        self.book_button = tk.Button(master, text="Book Room", command=self.book_room)
        self.book_button.grid(row=7, columnspan=2)

        # Button to cancel a reservation
        self.cancel_reservation_button = tk.Button(master, text="Cancel Reservation", command=self.cancel_reservation)
        self.cancel_reservation_button.grid(row=8, columnspan=2)

        # Button to quit the application
        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.grid(row=9, columnspan=2)

    def get_default_date(self):
        # Method to get the current date in the format "DD/MM/YYYY"
        return datetime.now().strftime("%d/%m/%Y")

    def search_rooms(self):
        # Method to search for available rooms based on user input

        # Retrieves user inputs
        customer_name = self.customer_name_entry.get()
        check_in_date = self.check_in_entry.get()
        check_out_date = self.check_out_entry.get()

        # Validates and handles empty input for number of people
        num_people_str = self.num_people_entry.get()
        if num_people_str.strip() == '':
            messagebox.showerror("Error", "Please enter the number of people.")
            return

        try:
            # Converts number of people input to integer
            num_people = int(num_people_str)
        except ValueError:
            # Displays error message if input is not a valid number
            messagebox.showerror("Error", "Please enter a valid number for the number of people.")
            return

        try:
            # Validates inputs using the Validator instance
            self.validator.validate_num_people(num_people)
            self.validator.validate_date_format(check_in_date)
            self.validator.validate_date_format(check_out_date)
            self.validator.validate_date_range(check_in_date, check_out_date)
            self.validator.validate_check_in(check_in_date)

            # Filters available rooms based on inputs using RoomManager
            available_rooms = self.room_manager.filter_room_options(check_in_date, check_out_date, num_people,
                                                                    self.reservation_manager)

            if not available_rooms:
                # If no available rooms, shows info message
                messagebox.showinfo("No Rooms Available", "There are no rooms available for the "
                                                          "selected dates and number of people.")
            else:
                # Displays available rooms in the listbox
                self.room_listbox.delete(0, tk.END)
                for room in available_rooms:
                    self.room_listbox.insert(tk.END, f"{room['room_type']}"
                                                     f" - Price: ${room['price_per_night']:.2f}")
                messagebox.showinfo("Available Rooms", "Available rooms have been loaded.")
        except ValueError as ve:
            # Handles validation errors
            messagebox.showerror("Value Error", str(ve))
        except Exception as e:
            # Handles other exceptions
            messagebox.showerror("Error", str(e))

    def generate_receipt_message(self, reference_number, customer_name, room_type, check_in_date,
                                 check_out_date, total_price):
        # method to generate receipt message
        try:
            # Attempts to generate a receipt message using the HotelManager instance
            receipt_message = self.hotel_manager.generate_receipt(reference_number, customer_name, room_type,
                                                                  check_in_date, check_out_date, total_price)
            if receipt_message:
                # If receipt message is generated successfully, returns it
                return receipt_message
            else:
                # If receipt message is not generated, returns an error message
                return "Error: Unable to generate receipt message. Please try again later."
        except Exception as e:
            # If an exception occurs during receipt generation, returns an error message with the exception details
            return f"Error: {str(e)}"

    def book_room(self):
        # Method to book a room based on user input

        # Retrieves customer name from entry widget
        customer_name = self.customer_name_entry.get()
        # Gets the index of the selected room from the listbox
        selected_index = self.room_listbox.curselection()

        if selected_index:
            # If a room is selected
            selected_room_index = selected_index[0]
            selected_room_info = self.room_listbox.get(selected_room_index)
            # Then this extracts room type and price from the selected room information
            selected_room_type, price_info = selected_room_info.split(' - ')
            price_per_night = float(price_info.split(': $')[1])

            try:
                # Validates that the number of people is an integer
                num_people = int(self.num_people_entry.get())
            except ValueError:
                # Displays an error message if the number of people is not an integer
                messagebox.showerror("Error", "Please enter a valid number for the number of people.")
                return

            try:
                # Validates the customer name
                self.hotel_manager.validator.validate_name_filled(customer_name)

                # Asks for confirmation before booking
                confirmation = messagebox.askyesno("Confirm Booking",
                                                   f"Do you want to book {selected_room_type}"
                                                   f" room?\nPrice per night: ${price_per_night:.2f}"
                                                   f"\n\nRefund Policy:\nYou are eligible for a 70% refund if "
                                                   f"you cancel the reservation before the check-in date.")

                if confirmation:
                    # If user confirms booking, this makes a reservation
                    reference_number, total_price = self.hotel_manager.make_reservation(
                        customer_name,
                        num_people,  # Uses the validated number of people
                        self.check_in_entry.get(),
                        self.check_out_entry.get(),
                        {'room_type': selected_room_type, 'price_per_night': price_per_night}
                    )

                    # Generates receipt message
                    receipt_text = self.generate_receipt_message(
                        reference_number,
                        customer_name,
                        selected_room_type,
                        self.check_in_entry.get(),
                        self.check_out_entry.get(),
                        total_price
                    )

                    # Displays reservation confirmation message
                    messagebox.showinfo("Reservation Confirmation", f"{receipt_text}\n\nThank you for "
                                                                    f"choosing our hotel!")

            except ValueError as ve:
                # Handles invalid name error
                messagebox.showerror("Invalid Name", str(ve))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            # If no room is selected, shows a warning message
            messagebox.showwarning("Selection Required", "Please select a room to book.")

    def cancel_reservation(self):
        # Method to cancel a reservation

        # Asks the user to enter the reference number of the reservation to cancel
        reference_number = simpledialog.askstring("Cancel Reservation",
                                                  "Enter the reference number of the reservation to cancel:")
        if reference_number:
            try:
                # Reads reservation data from the reservation manager
                reservations = self.reservation_manager.read_reservation_data()
                found_reservation = None

                # Searches for the reservation with the given reference number
                for reservation in reservations:
                    if reservation[0] == reference_number:
                        found_reservation = reservation
                        break

                # If the reservation is found
                if found_reservation:
                    (reference_number, customer_name, room_type, check_in_date,
                     check_out_date, total_price) = found_reservation

                    # Generates booking receipt message
                    booking_receipt_message = self.generate_receipt_message(reference_number, customer_name, room_type,
                                                                            check_in_date, check_out_date,
                                                                              float(total_price))
                    # Calculates refund amount
                    refund_amount = self.hotel_manager.calculate_refund(float(total_price))

                    # Asks for confirmation before cancellation
                    confirmation = messagebox.askyesno("Confirm Cancellation",
                                                       f"Are you sure you want to cancel the reservation "
                                                       f"with reference number {reference_number}?\n\nBooking Receipt:\n"
                                                       f"{booking_receipt_message}\n"
                                                       f"Refund Policy:\n"
                                                       f"You are eligible for a 70% refund if you cancel the"
                                                       f" reservation before the check-in date. "
                                                       f"Refund Amount: ${refund_amount:.2f}")

                    if confirmation:
                        # If user confirms cancellation, cancels the reservation
                        if self.hotel_manager.cancel_reservation(reference_number):
                            messagebox.showinfo("Cancellation Successful",
                                                f"Reservation with reference number {reference_number} has "
                                                f"been canceled. You have been refunded ${self.hotel_manager
                                                .calculate_refund(float(total_price)):.2f}"
                                                f"\n\nThank you for using our service!")
                        else:
                            # Shows error message if reservation not found
                            messagebox.showerror("Cancellation Error",
                                                 f"Reservation with reference number {reference_number} "
                                                 f"not found.")
                else:
                    # If no reservation found with the given reference number
                    messagebox.showerror("Reservation Not Found",
                                         f"No reservation found with reference number {reference_number}.")
            except Exception as e:
                # Shows error message if an exception occurs during cancellation
                messagebox.showerror("Cancellation Error", str(e))



root = tk.Tk()
app = HotelManagementApp(root)
root.mainloop()
