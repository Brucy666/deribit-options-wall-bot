def get_major_call_put_walls(wall_memory, current_price):
    largest_call = None
    largest_put = None

    for wall in wall_memory.values():
        strike = wall["strike"]
        oi = wall["oi"]
        wall_type = wall["type"]

        if wall_type == "C" and strike > current_price:
            if not largest_call or oi > largest_call["oi"]:
                largest_call = wall

        elif wall_type == "P" and strike < current_price:
            if not largest_put or oi > largest_put["oi"]:
                largest_put = wall

    return {
        "call": largest_call,
        "put": largest_put
    }
