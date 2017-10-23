#!/bin/env python

import pyxhook
import multiprocessing
import subprocess
import threading
import time
import logging
from copy import deepcopy
import datetime

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

def action(name):
    """
    Takes a file name for the sound byte and creates a function that plays
    the sound byte when called.
    """
    def temp():
        player = subprocess.Popen(['mplayer', name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
    return temp

actionDict = {'fire': action('gunshot.mp3'),
              'reload': action('reload.mp3'),
              'dryfire': action('dryfire.mp3')
              }

class Firearm:
    """ 
    This thing is going to be our mutable object, that will be passed between
    the concurrency primitives. The time based logic that manipulates this
    will be *external* to this class.
    """

    def __init__(self, actions, clipsize=8):
        self.maxclipsize = clipsize
        self.clipsize = clipsize
        self.action1 = actions['fire']
        self.action2 = actions['reload']
        self.action3 = actions['dryfire']

    def fire(self):
        if self.clipsize > 0:
            self.clipsize -= 1
            self.action1()
        else:
            self.action3()

    def full(self):
        if self.clipsize == self.maxclipsize:
            return True
        else:
            return False
    
    def empty(self):
        if self.clipsize == 0:
            return True
        else:
            return False

    def reload(self):
        if self.clipsize < self.maxclipsize:
            self.action2()
            self.clipsize += 1

# will be reusing a pattern, need deterministic concurrency here
# hence gevent again :)

def rangemaster(que, firearm):
    """
    We need the queue since we will be reactive to it based when stuff is
    able to be pulled out. The contents being pushed out don't really matter.

    What we want:
    1. If there is a period of 3 seconds when no keys are pressed we reload
    2. Else we keep firing while we still have ammo and keep making empty
    clicking noises when we run out. 

    Ok. We will have a global object called lastfired which has an internal
    time stamp from when the gun was last fired (with ammo or dry).

    We get two threads. 1st thread watches for the last fired timestamp and
    if it passed the 3 second threshold it reloads. 2nd thread reads the
    object, fires and updates the timestamp.
    
    One of the threads takes the que up top and reacts to the events as they
    come in.
    """
    
    # initial timestamp
    timestamp = datetime.datetime.now()
    
    def shooting(timestamp):
        while True:
            # fetch from the que, the que acts as a lock on the loop
            que.get()
            firearm.fire()
            timestamp = datetime.datetime.now()

    def reloading(timestamp):
        timedelta = datetime.timedelta(seconds=3) 
        while True:
            # this loop has no locking mechanism, use sleep to lower cpu use
            time.sleep(0.35)
            if firearm.full() != True:
                temp = datetime.datetime.now()
                diff = temp - timestamp
                if diff >= timedelta:
                    firearm.reload()

    shooter = threading.Thread(target=shooting, args=(timestamp,))
    reloader = threading.Thread(target=reloading, args=(timestamp,))
    shooter.start()
    reloader.start()

if __name__ == "__main__":

    # setting up multiprocessing
    m = multiprocessing.Manager()
    keyboardQueue = m.Queue()

    logging.basicConfig(filename='kbevent.log', level=logging.DEBUG)
   
    keyboardFeed = multiprocessing.Process(target=watchKeyboard,
                        args=(keyboardQueue,))

    keyboardFeed.start()

    # setup our firearm
    gun = Firearm(actionDict)
    gun.fire()
    # this thing below will respond to keyboard events
    rangemaster(keyboardQueue, gun)
    # I don't really need all this multiprocessing overhead, fuck w/e
    # fetching events from the keyboardQue, we don't really use it tho

