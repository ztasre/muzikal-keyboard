#!/bin/env python

import pyxhook
import multiprocessing
import subprocess
import time
import logging
from copy import deepcopy

def watchKeyboard(que):
    #This function is called every time a key is presssed
    def kbevent(event):
        # stick the logged event into the outbound que
        logging.info(str(event))
        que.put(deepcopy(event))
        # no terminating condition for the hook   
    #Create hookmanager
    hookman = pyxhook.HookManager()
    #Define our callback to fire when a key is pressed down
    hookman.KeyDown = kbevent
    #Hook the keyboard
    hookman.HookKeyboard()
    #Start our listener
    hookman.start()

    while True:
        time.sleep(0.2)

def actionResponse():
    player = subprocess.Popen(['mplayer', 'gunshot.mp3'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

if __name__ == "__main__":

    # setting up multiprocessing
    m = multiprocessing.Manager()
    keyboardQueue = m.Queue()

    logging.basicConfig(filename='kbevent.log', level=logging.DEBUG)
   
    keyboardFeed = multiprocessing.Process(target=watchKeyboard,
                        args=(keyboardQueue,))
    keyboardFeed.start()
    
    while True:
        # fetching events from the keyboardQue  
        keyboardQueue.get()
        actionResponse()        




