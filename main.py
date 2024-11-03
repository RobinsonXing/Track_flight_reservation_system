import sys
import util
from System import ReservationSystem

    
def main(lines):

    # initialize sysyem and index
    system = ReservationSystem()
    index = 1

    # load flights into system
    num_flight = int(lines[0])
    for _ in range(num_flight):
        index = util.load_flight_info(system, lines, index)

    # process queries 
    num_query = int(lines[index])
    index += 1
    results = []
    for _ in range(num_query):
        query = lines[index].split()
        # print(query)  # debug
        results.append(
            util.query_switch(system, query_info=query[1:], query_type=''.join(query[0][:-1])))
        index += 1
    if results:
        # print(results)  # debug
        print("\n".join(results))


if __name__ == '__main__':
    lines = []
    for l in sys.stdin:
        lines.append(l.rstrip('\r\n'))
    main(lines)