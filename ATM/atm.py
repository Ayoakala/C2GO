# Wheels are really, really hard to build on Windows, so I got wheels for 2.7:
# https://github.com/NaturalHistoryMuseum/ZBarWin64
# https://github.com/NaturalHistoryMuseum/zbar-python-patched

from __future__ import print_function
import os
import requests
import subprocess
import serial
import time

'''
zbar breaks windows integrated webcams, so the procedure is as follows:
Visit https://www.onlinemictest.com/webcam-test
Open zbar (process should hang), close online cam
With hanged zbar process in background, run this script and it will work every time.
'''

def execute(cmd):
    # GOD BLESS https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def main():
    for path in execute(['C:\\Program Files (x86)\\ZBar\\bin\\zbarcam.exe']):
        p = path
        if p:
            os.system("taskkill /IM zbarcam.exe /F")
            print('DETECTED', p)

            url = "http://c2go-api-dev.us-east-1.elasticbeanstalk.com/api/verify"
            r = requests.post(url, json={'data': p.replace('QR-Code:', '').strip()})
            transaction_amt = r.json()['objectCreated']['amount']
            print('Withdrew ${}'.format(transaction_amt))

            s = serial.Serial('COM13', 9600)
            time.sleep(2)
            s.write('Withdrew $' + str(transaction_amt))

if __name__ == '__main__':
    main()

