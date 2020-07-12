import micropython
import gc

def connect():
    # Display memory available at startup.
    gc.collect()
    micropython.mem_info()

    from wifi_setup.wifi_setup import WiFiSetup

    # You should give every device a unique name (to use as its access point name).
    ws = WiFiSetup("ding-5cd80b3")
    sta = ws.connect_or_setup()
    del ws
    print("WiFi is setup")

    # Display memory available once the WiFi setup process is complete.
    gc.collect()
    micropython.mem_info()
