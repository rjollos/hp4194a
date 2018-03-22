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

## TODO
* Add `reset` command: `./hp4194a --reset`
* Read and poll operations sometimes return incorrect data, which has led to insertion of `read` operations to "clear" the buffer.
* Improve error handling. For example, when LOCAL is pressed during acquisiiton.

## References
* [HP4194A Impedance/Gain-Phase Analyzer OperationManual](https://www.dropbox.com/s/0716yvo4kmdzme7/HP_4194A_Operation_Manual.pdf?dl=0)
* [Prologix GPIB-USB Controller Manual](http://prologix.biz/gpib-usb-controller.html)
