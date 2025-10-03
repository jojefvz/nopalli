from .value_objects import Instruction


can_follow_fetch_chassis = [
    Instruction.PREPULL,
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED
]

can_follow_prepull = [
    Instruction.YARD_PULL
    ]

can_follow_bobtail_to = [
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED
]

can_follow_pickup_empty = [
    Instruction.YARD_PULL,
    Instruction.LIVE_LOAD,
    Instruction.DROP_EMPTY,
    Instruction.TERMINATE_EMPTY,
    Instruction.STREET_TURN
]

can_follow_pickup_loaded = [
    Instruction.DROP_LOADED,
    Instruction.LIVE_UNLOAD,
    Instruction.YARD_PULL,
    Instruction.INGATE
]

can_follow_drop_empty = [
    Instruction.BOBTAIL_TO,
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
]

can_follow_drop_loaded = [
    Instruction.BOBTAIL_TO,
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
]

can_follow_live_load = [
    Instruction.LIVE_LOAD,
    Instruction.DROP_LOADED,
    Instruction.YARD_PULL,
    Instruction.INGATE,
]

can_follow_live_unload = [
    Instruction.LIVE_UNLOAD,
    Instruction.DROP_EMPTY,
    Instruction.TERMINATE_EMPTY,
    Instruction.YARD_PULL,
    Instruction.STREET_TURN,
]

can_follow_yard_pull = [
    Instruction.LIVE_LOAD,
    Instruction.LIVE_UNLOAD,
    Instruction.DROP_EMPTY,
    Instruction.DROP_LOADED,
    Instruction.TERMINATE_EMPTY,
    Instruction.INGATE,
    Instruction.STREET_TURN,
]

can_follow_terminate_empty = [
    Instruction.TERMINATE_CHASSIS
]

can_follow_ingate = [
    Instruction.TERMINATE_CHASSIS
]

_STARTABLE = [
    Instruction.FETCH_CHASSIS,
    Instruction.BOBTAIL_TO,
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
    Instruction.PREPULL,
]

_ALLOWED_FOLLOWS = {
    Instruction.FETCH_CHASSIS: can_follow_fetch_chassis,
    Instruction.PREPULL: can_follow_prepull,
    Instruction.BOBTAIL_TO: can_follow_bobtail_to,
    Instruction.PICKUP_EMPTY: can_follow_pickup_empty,
    Instruction.PICKUP_LOADED: can_follow_pickup_loaded,
    Instruction.DROP_EMPTY: can_follow_drop_empty,
    Instruction.DROP_LOADED: can_follow_drop_loaded,
    Instruction.LIVE_UNLOAD: can_follow_live_unload,
    Instruction.LIVE_LOAD: can_follow_live_load,
    Instruction.YARD_PULL: can_follow_yard_pull,
    Instruction.TERMINATE_EMPTY: can_follow_terminate_empty,
    Instruction.INGATE: can_follow_ingate,
    Instruction.STREET_TURN: [],          # nothing should follow
    Instruction.TERMINATE_CHASSIS: [],    # nothing should follow
}

_ENDABLE = [
    Instruction.BOBTAIL_TO,
    Instruction.TERMINATE_EMPTY,
    Instruction.INGATE,
    Instruction.TERMINATE_CHASSIS,
    Instruction.STREET_TURN,
]

_ALLOWED_REPEAT = [
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
    Instruction.DROP_EMPTY,
    Instruction.DROP_LOADED,
    Instruction.LIVE_UNLOAD,
    Instruction.LIVE_LOAD,
    Instruction.TERMINATE_EMPTY,
    Instruction.INGATE,
    Instruction.YARD_PULL,
    Instruction.STREET_TURN,
]