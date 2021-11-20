#!/usr/bin/env python
# Simplest Switchbot Command
# https://gist.github.com/mugifly/77e5ba2a2f1186bb7d494a90d4317695
# Thanks to https://gist.github.com/aerialist/163a5794e95ccd28dc023161324009ed

import sys
import binascii
import logging
from bluepy.btle import Peripheral

if len(sys.argv) != 3:
    print ('[Usage] python %s ff:ff:ff:ff:ff:ff MODE' % sys.argv[0])
    print ('\nMODE: on, off, press')
    print ('\nYou can get a MAC address of Switchbot, with using $ sudo hcitool lescan')
    quit(1)

mac = sys.argv[1]
mode = sys.argv[2]

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='cafe.log', encoding='utf-8', level=logging.DEBUG)
logging.info('Connecting... ' + mac)
print ('Connecting... ' + mac)
p = Peripheral(mac, 'random')
hand_service = p.getServiceByUUID('cba20d00-224d-11e6-9fb8-0002a5d5c51b')
hand = hand_service.getCharacteristics('cba20002-224d-11e6-9fb8-0002a5d5c51b')[0]

if mode == 'on':
    print ('On')
    hand.write(binascii.a2b_hex('570101'))
elif mode == 'off':
    print ('Off')
    hand.write(binascii.a2b_hex('570102'))
elif mode == 'press':
    logging.info('Press')
    print ('Press')
    hand.write(binascii.a2b_hex('570100'))

p.disconnect()
