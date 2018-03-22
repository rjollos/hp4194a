#!/usr/bin/env python

import argparse
import configparser
import datetime
import os
import sys
import time

import pylab
import scipy.io as scio
import serial
import matplotlib.pyplot as pyplot

debug = False
fileext = '.mat'


def main(filename):

    def to_tuple(s):
        return [int(float(v)) for v in s.split(',')]

    parser = configparser.ConfigParser()
    parser.read('hp4194a.ini')
    setup_section = parser['setup']
    port = setup_section.get('port')
    gpib_address = int(setup_section.get('gpib_address'))
    sweep_section = parser['sweep']
    start_frequency = int(float(sweep_section.get('start_frequency')))
    stop_frequency = int(float(sweep_section.get('stop_frequency')))
    number_of_points = int(sweep_section.get('number_of_points'))
    number_of_averages = int(sweep_section.get('number_of_averages'))
    display_range_a = to_tuple(sweep_section.get('display_range_a'))
    display_range_b = to_tuple(sweep_section.get('display_range_b'))
    bias_voltage = int(sweep_section.get('bias_voltage'))

    with serial.Serial(port, timeout=0.5) as sp:
        def write(cmd):
            sp.write(bytes(cmd + '\r\n', 'utf-8'))

        def read(nb=None):
            if nb:
                buf = sp.read(nb).strip()
            else:
                buf = sp.readline().strip()
            return buf.decode('utf-8')

        def read_data():
            buf = sp.readline().strip()
            return [float(v.strip()) for v in buf.split(b',') if v]

        def serial_poll():
            write('++spoll')
            time.sleep(0.25)
            return sp.readline().strip()

        write('++mode 1')  # Configure as controller
        write('++auto 1')  # Configure read-after-write
        write('++addr %d' % gpib_address)
        write('++clr')
        sp.reset_input_buffer()
        read()  # Clears the buffer
        write('++ver')
        print(read())

        write('IMP2')  # R-X
        write('ITM2')  # Integration time medium
        write(f'START={start_frequency}')
        write(f'STOP={stop_frequency}')
        write(f'AMIN={display_range_a[0]}')
        write(f'AMAX={display_range_a[1]}')
        write(f'BMIN={display_range_b[0]}')
        write(f'BMAX={display_range_b[1]}')
        write(f'NOP={number_of_points}')
        write(f'NOA={number_of_averages}')
        write('SHT1')  # Short compensation on
        write('OPN1')  # Open compenstaion on
        write(f'BIAS={bias_voltage}')

        write('RQS2')
        write('SWM2')  # Single sweep
        write('SWTRG')  # Trigger acquisition
        write('CMT"Acquiring sweep"')

        sweep_finished = False
        print("Acquiring sweep")
        sp.reset_input_buffer()
        read()  # Clears the buffer
        while not sweep_finished:
            polled = serial_poll()
            if polled:
                try:
                    status_byte = int(polled)
                except (ValueError, IndexError):
                    print("Serial poll returned unexpected value: {}"
                          .format(polled))
                    break
                if debug:
                    print("{:08b}".format(status_byte))
                sweep_finished = not(status_byte & 0x01)
        print("Acquisition complete")
        write('DCOFF')  # Bias off

        if sweep_finished:
            sp.reset_input_buffer()
            write('A?')
            a = read_data()
            write('B?')
            b = read_data()

            save = True
            if len(a) != number_of_points:
                print("Number of points transfered from Channel A: %d")
                save = False
            if len(b) != number_of_points:
                print("Number of points transfered from Channel B: %d")
                save = False
            if save:
                scio.savemat(filename, {
                    'time': datetime.datetime.now().isoformat(),
                    'biasVoltage': bias_voltage,
                    'numberOfAverages': number_of_averages,
                    'Frequency': (start_frequency, stop_frequency),
                    'ChannelA': a,
                    'ChannelB': b,
                })
                # Strip .mat when printing
                write(f'CMT"Saved as {os.path.basename(filename[:-4])}"')
                print(f"Data saved to {filename}")

                t = pylab.linspace(start_frequency, stop_frequency,
                                   number_of_points)
                plotyy(t, a, b, display_range_a, display_range_b)
            else:
                print("No data saved")


def plotyy(t, y1, y2, y1lim, y2lim):
    t /= 1e3  # Hz -> kHz
    fig, ax1 = pyplot.subplots()
    color = 'tab:orange'
    ax1.set_xlabel('Frequency [kHz]')
    ax1.set_ylabel('R', color=color)
    ax1.set_xlim(t[0], t[-1])
    ax1.set_ylim(y1lim)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.plot(t, y1, color=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('X', color=color)
    ax2.set_xlim(t[0], t[-1])
    ax2.set_ylim(y2lim)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.plot(t, y2, color=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    pyplot.show()
    return fig, ax1, ax2


def default_filename():
    """Create ISO8601 timestamp as default filename

    The format is: YYYYMMDDTHHMMSS
    """
    now = datetime.datetime.now().isoformat()
    return now.replace('-', '').replace(':', '').split('.')[0]


if __name__ == '__main__':
    default = default_filename()
    parser = argparse.ArgumentParser(description='HP4194A acquisition script')
    parser.add_argument('filename', nargs='?')
    args = parser.parse_args()
    if args.filename:
        filename = args.filename
    else:
        filename = input(f"Enter a filepath or press [ENTER] to accept the "
                         f"default ({default}.mat):") or default
    if not filename.endswith(fileext):
        filename += fileext
    if os.path.exists(filename):
        resp = input(f"File {filename} exists. Are you sure you want "
                     f"to overwrite it (y/n)?")
        if resp.lower() != 'y':
            sys.exit(0)
    main(filename)
