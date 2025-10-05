state = "STATE_DISARMED"
arming_timer = 0
trigger_timer = 0

def arm_button_pressed():
  pass

if state == "STATE_DISARMED" and arm_button_pressed():
    state = "STATE_ARMING"
    arming_timer = current_time()

elif state == "STATE_ARMING":
    if cancel_button_pressed():
        state = "STATE_DISARMED"
    elif current_time() - arming_timer > 10:
        state = "STATE_ARMED"

elif state == "STATE_ARMED":
    if disarm_button_pressed():
        state = "STATE_DISARMED"
    elif motion_detected():
        state = "STATE_TRIGGERED"
        trigger_timer = current_time()

elif state == "STATE_TRIGGERED":
    if disarm_button_pressed():
        state = "STATE_DISARMED"
    elif current_time() - trigger_timer > 30:
        state = "STATE_ALERT"

elif state == "STATE_ALERT":
    if alert_acknowledged():
        state = "STATE_RESETTING"

elif state == "STATE_RESETTING":
    if reset_complete():
        state = "STATE_DISARMED"

