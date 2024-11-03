
def load_flight_info(system, lines, index):
    # load basic info
    flight_info = lines[index].split()
    flight_id = int(flight_info[0])
    basic_info = flight_info[1:]
    index += 1
    
    # load seat info
    num_seat_class = int(lines[index])
    index += 1
    seat_price = []
    for seat_class in range(num_seat_class):
        last_col, price = map(int, lines[index].split())
        seat_price.append((seat_class+1, last_col, price))
        index += 1

    # add flight into system
    system.add_flight(flight_id, basic_info, seat_price)
    return index


def query_switch(system, query_type, query_info):
    operations = {
        "reserve": system.reserve_seat,
        "cancel": system.cancel_reservation,
        "seat-search": system.seat_search,
        "get-reservations": system.get_reservation,
        "flight-search": system.flight_search
    }
    if query_type in operations:
        return operations[query_type](*query_info)
    else:
        return "Unavailable operation!"

