"""
Case study: Circular Bus Route Management
Data structure: Circular Doubly Linked List

Each node of the list is a BUS STOP on the route.
 - next -> next stop going CLOCKWISE (outbound)
 - prev -> previous stop, i.e. the next stop going COUNTERCLOCKWISE (return)
 - The last stop points back to the first one (and the first to the last),
   so the route never ends: the bus can always keep going around.
"""

import random


class BusStop:
    """List node: represents a bus stop on the route."""

    def __init__(self, name, neighborhood, time_to_next, waiting_passengers=0):
        self.name = name                              # Stop name
        self.neighborhood = neighborhood              # Neighborhood or area
        self.time_to_next = time_to_next              # Minutes to the 'next' stop
        self.waiting_passengers = waiting_passengers  # People waiting for the bus
        self.prev = None                              # Previous stop
        self.next = None                              # Next stop

    def to_dict(self):
        return {
            "name": self.name,
            "neighborhood": self.neighborhood,
            "time_to_next": self.time_to_next,
            "waiting_passengers": self.waiting_passengers,
            "prev": self.prev.name if self.prev else None,
            "next": self.next.name if self.next else None,
        }


class CircularRoute:
    """Circular doubly linked list that represents the whole bus route."""

    BUS_CAPACITY = 40

    def __init__(self, route_name):
        self.route_name = route_name
        self.head = None              # First stop (route terminal)
        self.size = 0
        # State of the bus driving the route
        self.bus_location = None      # Stop where the bus currently is
        self.direction = "clockwise"  # "clockwise" uses next, "counterclockwise" uses prev
        self.passengers_on_board = 0
        self.history = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def is_empty(self):
        return self.head is None

    def search(self, name):
        """Goes around the list once looking for a stop by name."""
        if self.is_empty():
            return None
        current = self.head
        while True:
            if current.name.lower() == name.lower():
                return current
            current = current.next
            if current == self.head:  # Full lap completed
                return None

    def _log(self, message):
        self.history.insert(0, message)
        self.history = self.history[:15]

    # ------------------------------------------------------------------
    # Insertions
    # ------------------------------------------------------------------
    def insert_at_beginning(self, name, neighborhood, time_to_next, passengers=0):
        """Opens a new stop at the beginning of the route (it becomes the new head)."""
        if self.search(name):
            raise ValueError(f"A stop named '{name}' already exists")
        new_stop = BusStop(name, neighborhood, time_to_next, passengers)
        if self.is_empty():
            self.head = new_stop
            new_stop.next = new_stop
            new_stop.prev = new_stop
            self.bus_location = new_stop
        else:
            last = self.head.prev
            new_stop.next = self.head
            new_stop.prev = last
            self.head.prev = new_stop
            last.next = new_stop
            self.head = new_stop
        self.size += 1
        self._log(f"Stop '{name}' added at the beginning of the route")
        return new_stop

    def insert_at_end(self, name, neighborhood, time_to_next, passengers=0):
        """Opens a new stop at the end of the route (right before returning to head)."""
        if self.search(name):
            raise ValueError(f"A stop named '{name}' already exists")
        new_stop = BusStop(name, neighborhood, time_to_next, passengers)
        if self.is_empty():
            self.head = new_stop
            new_stop.next = new_stop
            new_stop.prev = new_stop
            self.bus_location = new_stop
        else:
            last = self.head.prev
            last.next = new_stop
            new_stop.prev = last
            new_stop.next = self.head
            self.head.prev = new_stop
        self.size += 1
        self._log(f"Stop '{name}' added at the end of the route")
        return new_stop

    def insert_after(self, reference, name, neighborhood, time_to_next, passengers=0):
        """Opens a new stop right after an existing stop."""
        ref_stop = self.search(reference)
        if ref_stop is None:
            raise ValueError(f"Stop '{reference}' does not exist")
        if self.search(name):
            raise ValueError(f"A stop named '{name}' already exists")
        new_stop = BusStop(name, neighborhood, time_to_next, passengers)
        following = ref_stop.next
        new_stop.prev = ref_stop
        new_stop.next = following
        ref_stop.next = new_stop
        following.prev = new_stop
        self.size += 1
        self._log(f"Stop '{name}' added after '{reference}'")
        return new_stop

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------
    def delete(self, name):
        """Closes a stop (roadwork, blocked street, etc.) and reconnects the route."""
        stop = self.search(name)
        if stop is None:
            raise ValueError(f"Stop '{name}' does not exist")

        # Case 1: it is the only stop on the route
        if stop.next == stop:
            self.head = None
            self.bus_location = None
            self.passengers_on_board = 0  # No route left, the bus ends service
        else:
            # If the bus is at that stop, it moves to the next one in its direction
            if self.bus_location == stop:
                self.bus_location = stop.next if self.direction == "clockwise" else stop.prev
            # Reconnect the neighbors so the route stays a closed circle
            stop.prev.next = stop.next
            stop.next.prev = stop.prev
            # Case 2: if it was the head, the head moves to the next stop
            if stop == self.head:
                self.head = stop.next
        stop.next = stop.prev = None
        self.size -= 1
        self._log(f"Stop '{name}' closed and removed from the route")

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------
    def traverse_clockwise(self):
        """Forward traversal using next (one full lap)."""
        result = []
        if self.is_empty():
            return result
        current = self.head
        while True:
            result.append(current)
            current = current.next
            if current == self.head:
                break
        return result

    def traverse_counterclockwise(self):
        """Backward traversal using prev (one full lap)."""
        result = []
        if self.is_empty():
            return result
        current = self.head
        while True:
            result.append(current)
            current = current.prev
            if current == self.head:
                break
        return result

    def full_lap_time(self):
        return sum(stop.time_to_next for stop in self.traverse_clockwise())

    def total_waiting_passengers(self):
        return sum(stop.waiting_passengers for stop in self.traverse_clockwise())

    # ------------------------------------------------------------------
    # Shortest direction between two stops (uses BOTH pointers)
    # ------------------------------------------------------------------
    def shortest_route(self, origin, destination):
        a = self.search(origin)
        b = self.search(destination)
        if a is None or b is None:
            raise ValueError("Origin or destination does not exist on the route")
        if a == b:
            return {"direction": "none", "stops": [a.name], "minutes": 0,
                    "clockwise_minutes": 0, "counterclockwise_minutes": 0}

        # Clockwise: move with next, adding the time of each segment
        cw_path, cw_min, current = [a.name], 0, a
        while current != b:
            cw_min += current.time_to_next
            current = current.next
            cw_path.append(current.name)

        # Counterclockwise: move with prev; the segment X -> X.prev
        # takes X.prev.time_to_next minutes
        ccw_path, ccw_min, current = [a.name], 0, a
        while current != b:
            current = current.prev
            ccw_min += current.time_to_next
            ccw_path.append(current.name)

        if cw_min <= ccw_min:
            return {"direction": "clockwise", "stops": cw_path, "minutes": cw_min,
                    "clockwise_minutes": cw_min, "counterclockwise_minutes": ccw_min}
        return {"direction": "counterclockwise", "stops": ccw_path, "minutes": ccw_min,
                "clockwise_minutes": cw_min, "counterclockwise_minutes": ccw_min}

    # ------------------------------------------------------------------
    # Bus simulation
    # ------------------------------------------------------------------
    def toggle_direction(self):
        self.direction = "counterclockwise" if self.direction == "clockwise" else "clockwise"
        self._log(f"The bus switched to {self.direction} direction")

    def move_bus(self):
        """Moves the bus to the next stop according to its direction (next or prev)."""
        if self.is_empty():
            raise ValueError("The route has no stops")
        if self.direction == "clockwise":
            self.bus_location = self.bus_location.next
        else:
            self.bus_location = self.bus_location.prev
        stop = self.bus_location

        # Some passengers get off and waiting ones get on (limited by capacity)
        got_off = random.randint(0, self.passengers_on_board) if self.passengers_on_board else 0
        self.passengers_on_board -= got_off
        free_seats = self.BUS_CAPACITY - self.passengers_on_board
        got_on = min(free_seats, stop.waiting_passengers)
        self.passengers_on_board += got_on
        stop.waiting_passengers -= got_on

        self._log(f"Bus arrived at '{stop.name}': {got_off} got off, {got_on} got on")
        return {"stop": stop.name, "got_off": got_off, "got_on": got_on}

    def generate_passengers(self):
        """Simulates new people arriving at the stops."""
        for stop in self.traverse_clockwise():
            stop.waiting_passengers += random.randint(0, 6)
        self._log("New passengers arrived at the stops")

    # ------------------------------------------------------------------
    # Full state for the frontend
    # ------------------------------------------------------------------
    def state(self):
        return {
            "route_name": self.route_name,
            "head": self.head.name if self.head else None,
            "size": self.size,
            "stops": [stop.to_dict() for stop in self.traverse_clockwise()],
            "clockwise_traversal": [stop.name for stop in self.traverse_clockwise()],
            "counterclockwise_traversal": [stop.name for stop in self.traverse_counterclockwise()],
            "bus": {
                "location": self.bus_location.name if self.bus_location else None,
                "direction": self.direction,
                "passengers_on_board": self.passengers_on_board,
                "capacity": self.BUS_CAPACITY,
            },
            "lap_time": self.full_lap_time(),
            "total_waiting": self.total_waiting_passengers(),
            "history": self.history,
        }


def create_sample_route():
    route = CircularRoute("Circular Route C1")
    route.insert_at_end("Central Terminal", "Downtown", 6, 8)
    route.insert_at_end("Main Square", "Historic Center", 4, 12)
    route.insert_at_end("General Hospital", "San Rafael", 5, 5)
    route.insert_at_end("University", "Torobajo", 7, 15)
    route.insert_at_end("Shopping Mall", "La Aurora", 5, 9)
    route.insert_at_end("Stadium", "El Recreo", 6, 4)
    route.insert_at_end("Industrial Park", "Las Americas", 8, 3)
    route.history = ["Route created with 7 stops"]
    return route


# Quick console test: python circular_route.py
if __name__ == "__main__":
    route = create_sample_route()
    print("Clockwise:        ", " -> ".join(s.name for s in route.traverse_clockwise()))
    print("Counterclockwise: ", " -> ".join(s.name for s in route.traverse_counterclockwise()))
    print("Full lap time:", route.full_lap_time(), "min")
    print("Shortest Central Terminal -> Stadium:", route.shortest_route("Central Terminal", "Stadium"))
    route.delete("General Hospital")
    print("After closing the Hospital:", " -> ".join(s.name for s in route.traverse_clockwise()))
