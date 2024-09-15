import time

def sync_time(server_time):
    current_time = time.time()
    offset = server_time - current_time
    return offset

def adjust_for_offset(offset):
    # Delay the playback based on offset
    time.sleep(max(0, offset))
