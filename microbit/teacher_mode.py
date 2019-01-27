from microbit import *
import radio

radio.on()
radio.config(length=100)
print('radio on')

state = 'UNLOCK'

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
    
    if button_b.was_pressed():
        radio.send('RESET')