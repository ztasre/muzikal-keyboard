
Uses pyxhook to make sounds as you type. This is the bare minimum to get it
running. Using gunshot sounds for the prototype.

* Future extensions

Make modules for different categories of sounds. 

1) piano (define keymapping, and bind different sounds to different keys)
2) guns (shell dropping, reloading, etc all based on typing speed) 

For the guns, there seems to be a error with how datetime is shared between
the thread. Look into later.

rewrite pyxhook to behave like inotify, maybe?
