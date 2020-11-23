# Rename this file to config.py and change wifi information, input and output pin numbers
from micropython import const

# Wifi network information
WIFI_SSID = "SSID"
WIFI_PWD = "password"

# Define the pins for the four remote buttons (up, "My", down, select)
BUTTON_UP_PIN = const(16)
BUTTON_MY_PIN = const(17)
BUTTON_DOWN_PIN = const(18)
BUTTON_SELECT_PIN = const(19)

# Define the pins for the 4 channel LED's to monitor (from top to bottom)
LED1_PIN = const(35)
LED2_PIN = const(34)
LED3_PIN = const(39)
LED4_PIN = const(36)

# Length of time to press button (ms)
BUTTON_MS = const(50)

# Optional: give different names to channels 1 - 5, leave numbers for the cleanest UI
# CHANNEL_NAMES = ["None", "Bathroom", "Hallway", "Living Room", "Downstairs", "All"]
CHANNEL_NAMES = ["0", "1", "2", "3", "4", "5"]
