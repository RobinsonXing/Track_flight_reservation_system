from datetime import datetime

class Flight:
    def __init__(self, basic_info, seat_prices):
        # basic info
        self.departure_airport = int(basic_info[0])
        self.arrival_airport = int(basic_info[1])
        self.departure_time = datetime.strptime(basic_info[2], "%H:%M:%S").time()
        self.arrival_time = datetime.strptime(basic_info[3], "%H:%M:%S").time()

        # seat info
        self.seat_prices = seat_prices
        self.seats_state = {}

    def is_seat_available(self, date, seat_id):
        # print(self.seats_state) # debug
        if date in self.seats_state:
            return False if seat_id in self.seats_state[date] else True
        return True
    
    def check_class_and_price(self, seat_id):
        col = int(''.join(seat_id[:-1]))
        for seat_class, last_col, price in self.seat_prices:
            if col <= last_col:
                return seat_class, price
        return 0, 0
    
    def check_num_available_seats(self, date):
        first_col = 1
        num_available_seats = []
        for seat_class, last_col, price in self.seat_prices:
            count_seat_available = 0
            for col in range(first_col, last_col+1):
                for row in ['A', 'B', 'C', 'D']:
                    if self.is_seat_available(date, seat_id=f"{col}{row}"):
                        count_seat_available += 1
            num_available_seats.append((
                seat_class, count_seat_available, price
            ))
            first_col = last_col + 1
        return num_available_seats

    def reserve(self, date, seat_id):
        if date in self.seats_state:
            self.seats_state[date].append(seat_id)
        else:
            self.seats_state[date] = []
            self.seats_state[date].append(seat_id)
        _, price = self.check_class_and_price(seat_id)
        return price

    def cancel(self, date, seat_id):
        self.seats_state[date].remove(seat_id)