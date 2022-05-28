#!/usr/bin/env python3

import json
import os
import sys
import asyncio
import websockets
import logging
import sounddevice as sd
import argparse

spk=[-0.470502, 1.516312, 1.498502, -2.308700, 0.052970, -0.393952, -1.250454, -0.840588, -0.349960, 0.644860, 2.139166, -0.227130, 0.225724, -0.086548, 1.123444, 2.513673, 0.234587, 0.524160, 1.005154, -0.663459, -0.099963, 0.675384, 1.306497, 0.347489, -0.415013, 0.445045, -1.184691, -1.413740, 0.005816, 0.871109, -0.984903, 0.679586, -0.428479, 0.031160, 0.876893, -0.644288, 0.051415, -0.913212, 0.710944, 0.007364, -0.612903, -0.152517, 0.131897, 0.567401, -0.515002, 0.910896, -0.049613, -0.064324, 0.006314, -0.861631, 0.490749, -0.607954, -0.412576, -1.137297, -0.613115, -0.440206, 0.339803, 0.897103, 0.492061, -0.013440, -0.082380, 0.255329, -0.070608, -0.907472, 0.816416, 0.184537, -0.367992, -0.254195, -0.345826, 0.889622, -0.040742, -0.450487, 1.855532, -1.261795, -0.123452, 0.772373, 0.055609, -1.057163, -1.177845, -1.895512, -0.137775, 0.965063, 0.812690, -2.242030, 0.029167, 1.672531, 1.290442, 0.002615, 3.614965, 0.239167, 0.297219, -1.146702, 0.930210, -0.325940, 0.244972, -0.527086, 0.131727, -2.038365, 1.295775, 0.924593, 0.287568, -0.333563, 1.739132, -1.200898, -0.761336, 0.308860, -1.395445, 0.190202, -1.031937, 0.040301, -0.126648, -1.699770, 2.041852, -0.333438, -0.766970, -2.121067, 0.223730, -0.067146, -1.001027, -1.985946, -1.634878, -0.443565, 1.534093, 0.513294, -0.016780, -1.310437, -1.418153, 0.591745]
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(indata))

async def run_test():

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 4000, device=args.device, dtype='int16',
                           channels=1, callback=callback) as device:

        async with websockets.connect(args.uri) as websocket:
            await websocket.send('{ "config" : { "sample_rate" : %d } }' % (device.samplerate))

            while True:
                data = await audio_queue.get()
                await websocket.send(data)
                r=(await websocket.recv())
                print(r)

                # print (await websocket.recv())

            await websocket.send('{"eof" : 1}')
            print (await websocket.recv())

async def main():

    global args
    global loop
    global audio_queue

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-l', '--list-devices', action='store_true',
                        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(description="ASR Server",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     parents=[parser])
    parser.add_argument('-u', '--uri', type=str, metavar='URL',
                        help='Server URL', default='ws://localhost:2700')
    parser.add_argument('-d', '--device', type=int_or_str,
                        help='input device (numeric ID or substring)')
    parser.add_argument('-r', '--samplerate', type=int, help='sampling rate', default=16000)
    args = parser.parse_args(remaining)
    loop = asyncio.get_event_loop()
    audio_queue = asyncio.Queue()

    logging.basicConfig(level=logging.INFO)
    await run_test()

if __name__ == '__main__':
    asyncio.run(main())
