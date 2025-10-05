state = "idle"

if state == "idle":
    state = "start"

elif state == "start":
    state = "processing"

elif state == "processing":
    state = "done"

elif state == "done":
    state = "idle"

else:
    state = "error"

