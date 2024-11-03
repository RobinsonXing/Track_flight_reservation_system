from datetime import datetime, timedelta
from Flight import Flight

# DEFINE LOG INFO
FLIGHT_NOT_FOUND = "flight not found"
TOO_LATE = "too late"
ALREADY_RESERVED = "already reserved"
RESERVATION_NOT_FOUND = "reservation not found"
UNAUTHORIZED_OPERATION = "unauthorized operation"
SUCCESS = "success"
CANCELED = "canceled"

class ReservationSystem:
    def __init__(self):
        self.flights = {}
        self.reservation_hist = []
        self.reservation_count = 0

    def add_flight(self, flight_id, basic_info, seat_prices):
        self.flights[flight_id] = Flight(basic_info, seat_prices)

    def reserve_seat(self, request_datetime_str, user_id, flight_date_str, flight_id, seat_id):
        # check if the flight available
        flight_id = int(flight_id)
        if flight_id not in self.flights:
            return f"reserve: {FLIGHT_NOT_FOUND}"
        
        # reservation unavailable after 2 hours ago before taking off
        flight = self.flights[flight_id]
        request_datetime = datetime.strptime(request_datetime_str, "%Y/%m/%d-%H:%M:%S")
        flight_date = datetime.strptime(flight_date_str, "%Y/%m/%d").date()
        if request_datetime >= datetime.combine(flight_date, flight.departure_time) - timedelta(hours=2):
            return f"reserve: {TOO_LATE}"

        # check if the seat available
        if not flight.is_seat_available(flight_date_str, seat_id):
            return f"reserve: {ALREADY_RESERVED}"

        # check price and reserve the seat
        self.reservation_count += 1
        reservation_id = self.reservation_count
        price = flight.reserve(flight_date_str, seat_id)
        self.reservation_hist.append(
            [reservation_id, user_id, flight_id, flight_date_str, seat_id, price, SUCCESS])
        return f"reserve: {reservation_id} {price}"

    def cancel_reservation(self, request_datetime_str, user_id, reservation_id):
        # check if the reservation exists
        reservation_id = int(reservation_id)
        if reservation_id > self.reservation_count or reservation_id <= 0 or self.reservation_hist[reservation_id - 1][6] != SUCCESS:
            return f"cancel: {RESERVATION_NOT_FOUND}"
        
        # check if the user_id correct
        if user_id != self.reservation_hist[reservation_id - 1][1]:
            return f"cancel: {UNAUTHORIZED_OPERATION}"
        
        # can't be canceled bofore 2 hours later to take off
        flight_id = self.reservation_hist[reservation_id - 1][2]
        flight = self.flights[flight_id]
        flight_date_str = self.reservation_hist[reservation_id - 1][3]
        flight_date = datetime.strptime(flight_date_str, "%Y/%m/%d").date()
        request_time = datetime.strptime(request_datetime_str, "%Y/%m/%d-%H:%M:%S")
        if request_time >= datetime.combine(flight_date, flight.departure_time) - timedelta(hours=2):
            return f"cancel: {TOO_LATE}"

        # cancel
        seat_id = self.reservation_hist[reservation_id - 1][4]
        flight.cancel(flight_date_str, seat_id)
        self.reservation_hist[reservation_id - 1][6] = CANCELED
        return f"cancel: {SUCCESS}"

    def seat_search(self, request_datetime_str, flight_date_str, flight_id):
        # check if the flight exists
        flight_id = int(flight_id)
        if flight_id not in self.flights:
            return f"seat-search: {FLIGHT_NOT_FOUND}"

        # query
        flight = self.flights[flight_id]
        result = "seat-search:\n"
        all_rows = []
        for col in range(1, 21):
            seats = [f"{col}{row}" for row in ['A', 'B', 'C', 'D']]
            seat_class, _ = flight.check_class_and_price(f"{col}A")
            row_result = "".join("X" if not flight.is_seat_available(flight_date_str, seat_id) else str(seat_class) for seat_id in seats)
            all_rows.append(list(row_result))
        # transpose
        transposed_rows = zip(*all_rows)
        for transposed_row in transposed_rows:
            result += "".join(transposed_row) + "\n"
        return result.strip()

    def get_reservation(self, request_datetime_str, user_id):
        # search the reservation history
        query_result = []
        for history in self.reservation_hist:
            if history[1] == user_id and history[6] == SUCCESS:
                reservation_id, _, flight_id, flight_date_str, seat_id, price, _ = history
                flight = self.flights[flight_id]
                flight_date = datetime.strptime(flight_date_str, "%Y/%m/%d").date()
                departure_datetime = datetime.combine(flight_date, flight.departure_time)
                query_result.append([reservation_id, price, flight_id, seat_id, 
                                     departure_datetime, flight.departure_airport, 
                                     flight.arrival_time, flight.arrival_airport]
                                     )

        # sort by departure datetime and reservation ID, translate to log
        if query_result:
            query_result.sort(key=lambda x: (x[4], x[0]))
            result_lines = ["get-reservations: " + str(len(query_result))]
            result_lines.extend([
                f"reservation id: {line[0]}, price: {line[1]}, seat: {line[4].strftime('%Y/%m/%d')} {line[2]} {line[3]}, route: {line[5]} ({line[4].strftime('%H:%M:%S')}) -> {line[7]} ({line[6].strftime('%H:%M:%S')})"
                for line in query_result
            ])
            return "\n".join(result_lines)
        else:
            return "get-reservations: 0"
        
        # print(query_result) # debug
        # return "This function is under maintenance" # debug

    def flight_search(self, request_datetime_str, flight_date_str, departure_airport, arrival_airport):
        # check flights available
        query_result = []
        count_flight_available = 0
        for flight_id, flight in self.flights.items():
            if int(departure_airport) == flight.departure_airport and int(arrival_airport) == flight.arrival_airport:
                count_flight_available += 1
                query_result.append((
                    flight_id, flight.departure_time, flight.arrival_time
                ))
        
        # sort by departure time and fligh_id
        query_result.sort(key=lambda x: (x[1], x[0]))

        # logger
        result = [f"flight-search: {count_flight_available}"]
        for flight_id, departure_time, arrival_time in query_result:
            result.append(f"{flight_id} {str(departure_time)} {str(arrival_time)}")
            flight = self.flights[flight_id]
            num_available_seats = flight.check_num_available_seats(flight_date_str)
            for seat_class, count_seat_available, price in num_available_seats:
                result.append(
                    f"class {seat_class}: {count_seat_available} seats available. price = {price}"
                )
        return "\n".join(result)
        # return "This function is under maintenance"
