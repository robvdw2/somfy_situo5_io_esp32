import machine
import utime
import network
import socket
import config

# Initiate output Pin objects with pull down resistor and high
button_up = machine.Pin(config.BUTTON_UP_PIN, machine.Pin.OUT, machine.Pin.PULL_DOWN, value=1)
button_my = machine.Pin(config.BUTTON_MY_PIN, machine.Pin.OUT, machine.Pin.PULL_DOWN, value=1)
button_down = machine.Pin(config.BUTTON_DOWN_PIN, machine.Pin.OUT, machine.Pin.PULL_DOWN, value=1)
button_select = machine.Pin(config.BUTTON_SELECT_PIN, machine.Pin.OUT, machine.Pin.PULL_DOWN, value=1)

# Initiate LED input pins as ADC
# Measures max 12 bit value = 4096 when LED off (3V), around 1560 when LED on
# use 4000 as threshold
ADC_THRESHOLD = 4000
led1 = machine.ADC(machine.Pin(config.LED1_PIN))
led1.atten(machine.ADC.ATTN_11DB)
led2 = machine.ADC(machine.Pin(config.LED2_PIN))
led2.atten(machine.ADC.ATTN_11DB)
led3 = machine.ADC(machine.Pin(config.LED3_PIN))
led3.atten(machine.ADC.ATTN_11DB)
led4 = machine.ADC(machine.Pin(config.LED4_PIN))
led4.atten(machine.ADC.ATTN_11DB)

# set up network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
if not wifi.isconnected():
    wifi.connect(config.WIFI_SSID, config.WIFI_PWD)
    while not wifi.isconnected():
        machine.idle()
print('network config:', wifi.ifconfig())


def pushchannel():
    """Push the Select button and read the active channel"""
    button_select.off()
    utime.sleep_ms(config.BUTTON_MS)
    button_select.on()
    utime.sleep_ms(100)
    v1 = led1.read()
    v2 = led2.read()
    v3 = led3.read()
    v4 = led4.read()
    if v1 < ADC_THRESHOLD and v2 < ADC_THRESHOLD and v3 < ADC_THRESHOLD and v4 < ADC_THRESHOLD:
        channel = 5
    elif v1 < ADC_THRESHOLD:
        channel = 1
    elif v2 < ADC_THRESHOLD:
        channel = 2
    elif v3 < ADC_THRESHOLD:
        channel = 3
    elif v4 < ADC_THRESHOLD:
        channel = 4
    else:
        channel = 0
    return channel


def switchchannel(c):
    """Push channel select button until desired state is reached"""
    while pushchannel() != c:
        machine.idle()
    return c


def pushbutton(button):
    """Push button for 50 milliseconds (default) by pulling to ground"""
    button.off()
    utime.sleep_ms(config.BUTTON_MS)
    button.on()


def execute(channel, button):
    """Execute button on channel"""
    global active_channel
    if channel != active_channel:
        active_channel = switchchannel(channel)
    pushbutton(button)
    return True


def page(actionstr=""):
    """HTML page"""
    global active_channel
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Window shutters</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="icon" href="data:,">
            <style>
                html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
                h1{color: #0c008f; padding: 2vh;}
                p{font-size: 1.5rem;}
                .button{display: inline-block; background-color: #448800; border: none; border-radius: 8px; color: white; padding: 8px 20px; text-decoration: none; font-size: 20px; margin: 2px; cursor: pointer;}
                .button2{background-color: #3333ff;}
                .button3{background-color: #aa3300;}
                .channel{display: inline; background-color: #bbbbbb; border: none; border-radius: 8px; color: black; padding: 8px 20px; text-decoration: none; font-size: 20px; margin: 1px;}
            </style>
        </head>
        <body>
            <h1>Window shutters</h1>
            <table border="0" align="center">
                <tr>
                    <td><button class="channel">""" + config.CHANNEL_NAMES[1] + """</button></td>
                    <td><a href="/1/up"><button class="button">Up</button></td>
                    <td><a href="/1/my"><button class="button button2">My</button></td>
                    <td><a href="/1/down"><button class="button button3">Down</button></td>
                </tr>
                <tr>
                    <td><button class="channel">""" + config.CHANNEL_NAMES[2] + """</button></td>
                    <td><a href="/2/up"><button class="button">Up</button></td>
                    <td><a href="/2/my"><button class="button button2">My</button></td>
                    <td><a href="/2/down"><button class="button button3">Down</button></td>
                </tr>
                <tr>
                    <td><button class="channel">""" + config.CHANNEL_NAMES[3] + """</button></td>
                    <td><a href="/3/up"><button class="button">Up</button></td>
                    <td><a href="/3/my"><button class="button button2">My</button></td>
                    <td><a href="/3/down"><button class="button button3">Down</button></td>
                </tr>
                <tr>
                    <td><button class="channel">""" + config.CHANNEL_NAMES[4] + """</button></td>
                    <td><a href="/4/up"><button class="button">Up</button></td>
                    <td><a href="/4/my"><button class="button button2">My</button></td>
                    <td><a href="/4/down"><button class="button button3">Down</button></td>
                </tr>
                <tr>
                    <td><button class="channel">""" + config.CHANNEL_NAMES[5] + """</button></td>
                    <td><a href="/5/up"><button class="button">Up</button></td>
                    <td><a href="/5/my"><button class="button button2">My</button></td>
                    <td><a href="/5/down"><button class="button button3">Down</button></td>
                </tr>
            </table>
            <p>Currently active channel: """ + config.CHANNEL_NAMES[active_channel] + """</p>""" + actionstr + """
            </body></html>"""
    return html


# Create socket for webserver on port 80
s = socket.socket()
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s.bind(addr)
s.listen(4)

active_channel = 0
while True:
    """Main loop"""
    # Check if active channel is known, if not detect channel
    if active_channel == 0:
        active_channel = pushchannel()

    # Accept GET requests on http://ip.address/channel/button. channel 1-5 and button up|my|down
    conn, addr = s.accept()
    request = conn.recv(1024)
    request = str(request)
    url_start = request.find('GET ') + 5
    url_end = request.find(' HTTP')
    url = request[url_start:url_end].split('/', 1)
    if len(url) == 2:
        try:
            req_channel = int(url[0])
        except ValueError:
            req_channel = 0

        req_button = url[1].lower()
        if 1 <= req_channel <= 5:
            executed = False
            if req_button == "up":
                executed = execute(req_channel, button_up)
            elif req_button == "my":
                executed = execute(req_channel, button_my)
            elif req_button == "down":
                executed = execute(req_channel, button_down)

            if executed is True:
                response = page("\n\t\t<p style=\"color:green;\">Action <b>" + req_button +
                                "</b> executed on channel <b>" + config.CHANNEL_NAMES[req_channel] + "</b></p>\n")
            else:
                response = page("\n\t\t<p style=\"color:red;\">Invalid button (up|my|down)</p>\n")
        else:
            response = page("\n\t\t<p style=\"color:red;\">Invalid channel (1-5)</p>\n")
    else:
        response = page()

    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.send(response)
    conn.close()
