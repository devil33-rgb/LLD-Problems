# -------------------- USER --------------------
class User:
    """
    Represents a customer using the vehicle rental system.

    Attributes:
        username (str): Unique identifier for the user.
        location (str): Default location of the user.
    """

    def __init__(self, username, location):
        self.username = username
        self.location = location


# -------------------- VEHICLE --------------------
class Vehicle:
    """
    Represents a vehicle that can be booked and rented.

    Attributes:
        vehicle_name (str): Type of vehicle (e.g., Car, Bike).
        plate_number (str): Unique registration number.
        vehicle_location (str): Location where the vehicle is available.
        vehicleisavailable (bool): Availability status of vehicle.
    """

    def __init__(self, vehicle_name, plate_number, vehicle_location):
        self.vehicle_name = vehicle_name
        self.plate_number = plate_number
        self.vehicle_location = vehicle_location
        self.vehicleisavailable = True  # True → available, False → rented

    def __repr__(self):
        """Human-readable representation of the vehicle."""
        status = "Available" if self.vehicleisavailable else "Rented"
        return f"{self.vehicle_name} ({self.plate_number}) - {status}"


# -------------------- BOOKING --------------------
class Booking:
    """
    Represents a booking record created when a user reserves a vehicle.

    Lifecycle of a booking:
        BOOKED → RENTED → COMPLETED

    Class Attributes:
        booking_counter (int): Auto-incrementing ID generator.

    Instance Attributes:
        booking_id (int): Unique identifier of booking.
        username (str): User who created booking.
        vehicle_name (str): Vehicle type booked.
        plate_number (str): Specific vehicle assigned.
        location (str): Location of booking.
        status (str): Current booking state.
    """

    booking_counter = 1

    def __init__(self, user, vehicle):
        self.booking_id = Booking.booking_counter
        Booking.booking_counter += 1

        self.username = user.username
        self.vehicle_name = vehicle.vehicle_name
        self.plate_number = vehicle.plate_number
        self.location = vehicle.vehicle_location
        self.status = "BOOKED"

    def __repr__(self):
        """Readable booking summary."""
        return f"BookingID:{self.booking_id} | {self.vehicle_name} | {self.status}"


# -------------------- VEHICLE MANAGER --------------------
class VehicleManager:
    """
    Responsible for storing and retrieving vehicles by location.

    Data Structure:
        vehicle_loc_hashmap:
            key   → location
            value → list of Vehicle objects at that location
    """

    def __init__(self):
        self.vehicle_loc_hashmap = {}

    def addvehicle(self, vehicle):
        """
        Adds a vehicle to the system grouped by location.

        Args:
            vehicle (Vehicle): Vehicle object to add.

        Returns:
            bool: True after successful insertion.
        """
        self.vehicle_loc_hashmap.setdefault(vehicle.vehicle_location, []).append(vehicle)
        return True

    def getVehicles(self, location):
        """
        Retrieves all vehicles available at a given location.

        Args:
            location (str): Location to search.

        Returns:
            list[Vehicle]: List of vehicles at location.
        """
        return self.vehicle_loc_hashmap.get(location, [])


# -------------------- BOOK / RENT MANAGER --------------------
class VehicleBookRentManager:
    """
    Core service handling:
        • booking creation
        • vehicle rental
        • vehicle return
        • booking record storage

    Attributes:
        vehicle_manager (VehicleManager): Handles vehicle storage.
        booking_records (dict): Maps booking_id → Booking object.
    """

    def __init__(self):
        self.vehicle_manager = VehicleManager()
        self.booking_records = {}

    def createBooking(self, user, vehicle_name, location):
        """
        Creates a booking if an available vehicle is found.

        Steps:
            1. Search vehicles by location
            2. Find matching available vehicle
            3. Create booking record

        Returns:
            int | None: Booking ID if successful, else None.
        """
        for vehicle in self.vehicle_manager.getVehicles(location):
            if vehicle.vehicle_name == vehicle_name and vehicle.vehicleisavailable:
                booking = Booking(user, vehicle)
                self.booking_records[booking.booking_id] = booking
                return booking.booking_id
        return None

    def rentVehicle(self, booking_id):
        """
        Converts a BOOKED vehicle into RENTED state.

        Returns:
            bool: True if rental successful.
        """
        booking = self.booking_records.get(booking_id)
        if not booking or booking.status != "BOOKED":
            return False

        for vehicle in self.vehicle_manager.getVehicles(booking.location):
            if vehicle.plate_number == booking.plate_number and vehicle.vehicleisavailable:
                vehicle.vehicleisavailable = False
                booking.status = "RENTED"
                return True
        return False

    def returnVehicle(self, booking_id):
        """
        Marks vehicle as returned and completes booking.

        Returns:
            bool: True if return successful.
        """
        booking = self.booking_records.get(booking_id)
        if not booking or booking.status != "RENTED":
            return False

        for vehicle in self.vehicle_manager.getVehicles(booking.location):
            if vehicle.plate_number == booking.plate_number:
                vehicle.vehicleisavailable = True
                booking.status = "COMPLETED"
                return True
        return False

    def showBookings(self):
        """Returns all booking records."""
        return list(self.booking_records.values())


# -------------------- USER VEHICLE MANAGER --------------------
class UserVehicleManager:
    """
    Acts as the user-facing interface layer.

    Responsibilities:
        • connect user actions with booking system
        • maintain user → booking mapping
    """

    def __init__(self):
        self.vehicle_book_rent_manager = VehicleBookRentManager()
        self.user_bookings = {}

    def Userbookvehicle(self, user, vehicle_name, location):
        """
        Allows user to book a vehicle.

        Returns:
            int | None: Booking ID if successful.
        """
        booking_id = self.vehicle_book_rent_manager.createBooking(user, vehicle_name, location)
        if booking_id:
            self.user_bookings.setdefault(user.username, []).append(booking_id)
            print(f"Vehicle booked successfully. Booking ID: {booking_id}")
            return booking_id
        print("Booking failed")
        return None

    def UserrentVehicle(self, booking_id):
        """Allows user to rent previously booked vehicle."""
        if self.vehicle_book_rent_manager.rentVehicle(booking_id):
            print("Vehicle rented successfully")
            return True
        print("Rent failed")
        return False

    def UserreturnVehcile(self, booking_id):
        """Allows user to return rented vehicle."""
        if self.vehicle_book_rent_manager.returnVehicle(booking_id):
            print("Vehicle returned successfully")
            return True
        print("Return failed")
        return False


# -------------------- DEMO EXECUTION --------------------

# Create user
user = User("prateek", "Bangalore")

# Create manager
user_manager = UserVehicleManager()
vehicle_manager = user_manager.vehicle_book_rent_manager.vehicle_manager

# Add vehicles
vehicle_manager.addvehicle(Vehicle("Car", "KA01", "Bangalore"))
vehicle_manager.addvehicle(Vehicle("Bike", "KA02", "Bangalore"))

# Book vehicle
booking_id = user_manager.Userbookvehicle(user, "Car", "Bangalore")

# Rent vehicle
user_manager.UserrentVehicle(booking_id)

# Return vehicle
user_manager.UserreturnVehcile(booking_id)

# Show all bookings
print(user_manager.vehicle_book_rent_manager.showBookings())
