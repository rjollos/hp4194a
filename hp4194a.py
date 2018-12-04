#!/usr/bin/env python3
"""Acquisition script for HP4194A Impedance Analyzer"""

import argparse
import configparser
import datetime
import os
import subprocess
import sys

import numpy
import pylab
import pyvisa
import scipy.io as scio
import matplotlib.pyplot as pyplot

DEBUG = False
FILE_EXT = '.mat'


def main(filename):
    """Acquire and plot/save data."""
    r = subprocess.run('git describe --tags --always', shell=True,
                       stdout=subprocess.PIPE)
    program_version = r.stdout.strip().decode()

    def to_tuple(s):
        return [int(float(v)) for v in s.split(',')]

    parser = configparser.ConfigParser()
    parser.read('hp4194a.ini')
    setup_section = parser['setup']
    resource_name = setup_section.get('resource_name')
    gpib_address = int(setup_section.get('gpib_address'))
    sweep_section = parser['sweep']
    start_frequency = int(float(sweep_section.get('start_frequency')))
    stop_frequency = int(float(sweep_section.get('stop_frequency')))
    number_of_points = int(sweep_section.get('number_of_points'))
    number_of_averages = int(sweep_section.get('number_of_averages'))
    display_range_a = to_tuple(sweep_section.get('display_range_a'))
    display_range_b = to_tuple(sweep_section.get('display_range_b'))
    bias_voltage = int(sweep_section.get('bias_voltage'))

    rm = pyvisa.ResourceManager('@py')
    inst = rm.open_resource(resource_name)
    inst.timeout = 10000

    inst.write('++mode 1')  # Configure as controller
    inst.write('++auto 1')  # Configure read-after-write
    inst.write('++addr %d' % gpib_address)
    inst.write('++clr')
    print(inst.query('++ver'))

    inst.write('IMP2')  # R-X
    inst.write('ITM2')  # Integration time medium
    inst.write(f'START={start_frequency}')
    inst.write(f'STOP={stop_frequency}')
    inst.write(f'AMIN={display_range_a[0]}')
    inst.write(f'AMAX={display_range_a[1]}')
    inst.write(f'BMIN={display_range_b[0]}')
    inst.write(f'BMAX={display_range_b[1]}')
    inst.write(f'NOP={number_of_points}')
    inst.write(f'NOA={number_of_averages}')
    inst.write('SHT1')  # Short compensation on
    inst.write('OPN1')  # Open compenstaion on
    inst.write(f'BIAS={bias_voltage}')

    inst.write('RQS2')
    inst.write('SWM2')  # Single sweep
    inst.write('SWTRG')  # Trigger acquisition
    inst.write('CMT"Acquiring sweep"')

    sweep_finished = False
    print("Acquiring sweep")
    while not sweep_finished:
        polled = inst.query('++spoll')
        if polled:
            try:
                status_byte = int(polled)
            except (ValueError, IndexError):
                print("Serial poll returned unexpected value: {}"
                      .format(polled))
                break
            if DEBUG:
                print("{:08b}".format(status_byte))
            sweep_finished = not status_byte & 0x01
    print("Acquisition complete")
    inst.write('DCOFF')  # Bias off

    a = inst.query_ascii_values('A?', container=numpy.array)
    b = inst.query_ascii_values('B?', container=numpy.array)

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
            'acqProgramVersion': program_version,
            'biasVoltage': bias_voltage,
            'numberOfAverages': number_of_averages,
            'Frequency': (start_frequency, stop_frequency),
            'ChannelA': a,
            'ChannelB': b,
        })
        # Strip .mat when printing
        inst.write(f'CMT"Saved as {os.path.basename(filename[:-4])}"')
        print(f"Data saved to {filename}")

        t = pylab.linspace(start_frequency, stop_frequency,
                           number_of_points)
        plotyy(t, a, b, display_range_a, display_range_b)
    else:
        print("No data saved")

    inst.close()
    rm.close()


def plotyy(t, y1, y2, y1lim, y2lim):
    """Plot data with two y-axes."""
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


def parse_args():
    """Parse command line arguments."""
    default = default_filename()
    parser = argparse.ArgumentParser(description='HP4194A acquisition script')
    parser.add_argument('filename', nargs='?')
    args = parser.parse_args()
    if args.filename:
        filename = args.filename
    else:
        filename = input(f"Enter a filepath or press [ENTER] to accept the "
                         f"default ({default}.mat):") or default
    if not filename.endswith(FILE_EXT):
        filename += FILE_EXT
    if os.path.exists(filename):
        resp = input(f"File {filename} exists. Are you sure you want "
                     f"to overwrite it (y/n)?")
        if resp.lower() != 'y':
            sys.exit(0)
    return filename


if __name__ == '__main__':
    main(parse_args())
