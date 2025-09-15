from .value_objects import Instruction


can_follow_prepull = [
    Instruction.DROP_LOADED,
    Instruction.LIVE_UNLOAD,
]

can_follow_bobtail_to = [
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
]

can_follow_pickup_empty = [
    Instruction.DROP_EMPTY,
    Instruction.LIVE_LOAD,
    Instruction.TERMINATE,
    Instruction.STREET_TURN,
]

can_follow_pickup_loaded = [
    Instruction.DROP_LOADED,
    Instruction.LIVE_UNLOAD,
    Instruction.INGATE,
]

can_follow_drop_loaded = [
    Instruction.BOBTAIL_TO,
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
]

can_follow_drop_empty = [
    Instruction.BOBTAIL_TO,
    Instruction.PICKUP_EMPTY,
    Instruction.PICKUP_LOADED,
]

can_follow_live_load = [
    Instruction.LIVE_LOAD,
    Instruction.INGATE,
]

can_follow_live_unload = [
    Instruction.LIVE_UNLOAD,
    Instruction.TERMINATE,
    Instruction.STREET_TURN,
]
