STATE_ARMING = "ARMING"
STATE_ACTIVE = "ACTIVE"

if state == STATE_ARMING:
    if check_sensors():
        state = STATE_ACTIVE

