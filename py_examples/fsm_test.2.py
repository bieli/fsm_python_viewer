STATE_IDLE = 0
STATE_FILLING = 1
STATE_WASHING = 2
STATE_RINSING = 3
STATE_SPINNING = 4
STATE_COMPLETE = 5
STATE_ERROR = 6


state = "STATE_IDLE"

if state == "STATE_IDLE":
    state = "STATE_FILLING"

elif state == "STATE_FILLING":
    state = "STATE_WASHING"

elif state == "STATE_WASHING":
    state = "STATE_RINSING"

elif state == "STATE_RINSING":
    state = "STATE_SPINNING"

elif state == "STATE_SPINNING":
    state = "STATE_COMPLETE"

elif state == "STATE_COMPLETE":
    state = "STATE_IDLE"

elif error_detected():
    state = "STATE_ERROR"

