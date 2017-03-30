import subprocess
import json
import sys
import os
import threading
import time

BUNDLE_ID = "enterprise.pennypop.dance"

def terminateAll():
    simulators = json.loads(subprocess.check_output(['xcrun', 'simctl', 'list', '--json']))
    devices = simulators['devices']
    for version in devices:
        for sim in devices[version]:
            print sim 
            if sim['state'] == 'Booted':
                os.system('xcrun simctl terminate "{}" {}'.format(sim['udid'], BUNDLE_ID))            
            
terminateAll()

