# 🚌 Circular Bus Route — Circular Doubly Linked List

Data Structures workshop: a real-life case study implemented in **Python** with a **web frontend**.

## Case study

A transport company runs a **circular bus route** that goes through several stops in the city.
The route never ends: after the last stop the bus returns to the first one, and it can be driven
**clockwise (outbound)** or **counterclockwise (return)**. That is exactly a circular doubly linked list.

| List concept | In the case study |
|---|---|
| Node | `BusStop` |
| `next` | Next stop going clockwise |
| `prev` | Next stop going counterclockwise |
| `head` | Route terminal (Central Terminal) |
| Last node → first node | The bus finishes the lap and returns to the terminal |
| Insert | Open a new stop |
| Delete | Close a stop (roadwork, blocked street) |
| Traverse | The bus moves stop by stop |

### Data stored in each `BusStop` node
- `name`: stop name
- `neighborhood`: area of the city
- `time_to_next`: minutes to the `next` stop
- `waiting_passengers`: people waiting for the bus
- `prev` and `next`: pointers to the neighboring stops

## Files
```
bus_route/
├── circular_route.py   ← BusStop (node) and CircularRoute (circular doubly linked list)
├── app.py              ← Flask server (API connecting the list to the web page)
└── templates/
    └── index.html      ← Frontend: route map, forms and memory view
```

## How to run
1. Install Flask (only once):
   ```
   pip install flask
   ```
2. Go into the folder and run:
   ```
   python app.py
   ```
3. Open in the browser: **http://127.0.0.1:5000**

To test only the list in the console: `python circular_route.py`

## Implemented operations
| Method | What it does |
|---|---|
| `insert_at_beginning()` | Adds a stop and makes it the new head |
| `insert_at_end()` | Adds a stop right before returning to the head |
| `insert_after()` | Adds a stop between two existing ones |
| `delete()` | Closes a stop and reconnects its neighbors' `prev`/`next` |
| `search()` | Finds a stop by going around the list once |
| `traverse_clockwise()` | Traverses using `next` |
| `traverse_counterclockwise()` | Traverses using `prev` |
| `shortest_route()` | Compares both directions and picks the faster one |
| `move_bus()` | Moves the bus with `next` or `prev`; passengers get on and off |
| `toggle_direction()` | Switches between clockwise and counterclockwise |
| `full_lap_time()` | Adds up the minutes of every segment |

## Key points for the presentation
1. **Why it is circular:** the route has no end; a traversal stops when it gets back to `head`, not when it finds `None`.
2. **Why it is doubly linked:** the bus can go both ways. Without `prev`, going "backwards" would require almost a full lap.
3. **Advantage in action:** `shortest_route()` uses both pointers to compare directions (e.g. Central Terminal → Stadium: 27 min clockwise vs 14 min counterclockwise).
4. **Deletion:** closing a stop does `stop.prev.next = stop.next` and `stop.next.prev = stop.prev`. Three cases are handled: only node, head node and middle node. If the bus was at that stop, it moves on to the next one.
5. **Improvement over the class code:** traversals use `self.head` (the slide code used the global variable `my_list.head`).
