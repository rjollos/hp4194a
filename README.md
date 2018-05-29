# Description

This is a Python script for acquiring from the HP4194A impedance analyzer using the [Prologix GPIB-USB Controller](http://prologix.biz/gpib-usb-controller.html). The [PySerial](http://pyserial.readthedocs.io/en/latest/pyserial_api.html) library is used to communicate over the USB link.

The Prologix controller can be purchased from [Sparkfun](https://www.sparkfun.com/products/549).

## Installation

1. Install the [FTDI VCP Driver](http://www.ftdichip.com/Drivers/VCP.htm).
1. Create a Python environment.
    ```
    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install -U pip
    $ pip install -r requirements.txt
    ```

## Tested with

* macOS 10.13.3
* Python 3.6.4
* FTDI USB Serial Driver 2.4.2 (2017-05-02)
* Prologix GPIB-USB Controller version 6.107

## Troubleshooting

On MacOSX, the following error has been seen:

    Traceback (most recent call last):
      File "./hp4194a.py", line 10, in <module>
        import pylab
      File "/Users/rjollos/.pyenv/versions/hp4194a-3.6.5/lib/python3.6/site-packages/pylab.py", line 1, in <module>
        from matplotlib.pylab import *
      File "/Users/rjollos/.pyenv/versions/hp4194a-3.6.5/lib/python3.6/site-packages/matplotlib/pylab.py", line 252, in <module>
        from matplotlib import cbook, mlab, pyplot as plt
      File "/Users/rjollos/.pyenv/versions/hp4194a-3.6.5/lib/python3.6/site-packages/matplotlib/pyplot.py", line 115, in <module>
        _backend_mod, new_figure_manager, draw_if_interactive, _show = pylab_setup()
      File "/Users/rjollos/.pyenv/versions/hp4194a-3.6.5/lib/python3.6/site-packages/matplotlib/backends/__init__.py", line 62, in pylab_setup
        [backend_name], 0)
      File "/Users/rjollos/.pyenv/versions/hp4194a-3.6.5/lib/python3.6/site-packages/matplotlib/backends/backend_macosx.py", line 17, in <module>
        from matplotlib.backends import _macosx
    RuntimeError: Python is not installed as a framework. The Mac OS X 
    backend will not be able to function correctly if Python is not
    installed as a framework. See the Python documentation for more
    information on installing Python as a framework on Mac OS X. Please 
    either reinstall Python as a framework, or try one of the other backends.
    If you are using (Ana)Conda please install python.app and replace the 
    use of 'python' with 'pythonw'. See 'Working with Matplotlib on OSX' in
    the Matplotlib FAQ for more information.

The solution described in [this](https://stackoverflow.com/a/21789908/121694) StackOverflow response has successfully solved the issue.

## TODO

* Add `reset` command: `./hp4194a --reset`
* Read and poll operations sometimes return incorrect data, which has led to insertion of `read` operations to "clear" the buffer.
* Improve error handling. For example, when LOCAL is pressed during acquisiiton.

## References

* [HP4194A Impedance/Gain-Phase Analyzer OperationManual](https://www.dropbox.com/s/0716yvo4kmdzme7/HP_4194A_Operation_Manual.pdf?dl=0)
* [Prologix GPIB-USB Controller Manual](http://prologix.biz/gpib-usb-controller.html)
