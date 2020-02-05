from microbit import *
from utime import ticks_diff, ticks_ms
import radio

radio.on()
radio.config(length=100)
print('radio on')

state = 'UNLOCK'
last_lock_ping = ticks_ms()
ping_interval = 1000

while True:
    msg = radio.receive()
    display.show(state[0], wait=False, delay=100)
    
    if msg is not None:
        print(msg)
        display.show(Image.YES, wait=False, delay=100, clear=True)
    
    if button_a.was_pressed():
        if state == 'UNLOCK':
            state = 'LOCK'
            radio.send('LOCK')
        else:
            state = 'UNLOCK'
            radio.send('UNLOCK')

    if ticks_diff(ticks_ms(), last_lock_ping) > ping_interval:
        if state in ('LOCK'):
            radio.send(state)
    
    if button_b.was_pressed():
        print('Reset Message Sent')
        radio.send('RESET')