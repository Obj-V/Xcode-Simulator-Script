import subprocess
import json
import sys
import os
import threading
import time

simulators = [
    ('iOS 9.1',  'iPhone 4s'),
    ('iOS 10.2',  'iPhone 5'),
    ('iOS 10.2',  'iPhone 6'),
    ('iOS 10.2',  'iPhone 6 Plus'),
    ('iOS 10.2',  'iPad Air'),
]

DEVELOPER_DIR = "/Applications/Xcode.app/Contents/Developer"
SIMULATOR_PATH = "{}/Applications/Simulator.app".format(DEVELOPER_DIR)
def get_sim(simulator):
    available_sim = json.loads(subprocess.check_output(['xcrun', 'simctl', 'list', '--json']))  
    version, device = simulator
    return filter(lambda d: d['name'] == device, available_sim['devices'][version])[0] 

def get_sim_udid(simulator):
    return get_sim(simulator)['udid']

def get_sim_state(simulator):
    return get_sim(simulator)['state']


CONFIGURATION = "Debug"
PROJECT = "Dance"
BUNDLE_ID = "enterprise.pennypop.dance"

xcodebuild_cmd = [
    "xcodebuild", 
    "-project", "PennyPop.xcodeproj", 
    "-configuration", CONFIGURATION, 
    "-target", PROJECT,
    "-scheme", "DanceDebug", 
    "-derivedDataPath", 
    "build"
]

BUILD_PATH = 'build/Build/Products/{}-iphonesimulator/{}.app'.format(CONFIGURATION, PROJECT)


def compile():
    for sim in simulators:
        xcodebuild_cmd.extend(['-destination', 'id={}'.format(get_sim_udid(sim))])
    
    
    p = subprocess.Popen(xcodebuild_cmd, stdout=subprocess.PIPE, bufsize=1)
    for line in iter(p.stdout.readline, ""):
        sys.stdout.write(line)
    p.stdout.close()
    return_code = p.wait()


compile()

def launch_sim(sim):
    udid = get_sim_udid(sim)
    version, device = sim

    print "[{}-{}] Opening Simulator {}".format(version, device, udid)
    if os.system("ps aux | grep {} | grep {} | grep -v grep".format(udid, SIMULATOR_PATH)) != 0:
        os.system("open {} -n --args -CurrentDeviceUDID {}".format(SIMULATOR_PATH, udid))
    
    for _ in xrange(180):
        print "[{}-{}] {}".format(version, device, get_sim_state(sim))
        if get_sim_state(sim) == 'Booted':
            break
        time.sleep(1)
        
    print "[{}-{}] Terminating {}".format(version, device, BUNDLE_ID)
    os.system('xcrun simctl terminate "{}" {}'.format(device, BUNDLE_ID))

    print "[{}-{}] Installing {}".format(version, device, BUILD_PATH)
    os.system('xcrun simctl install "{}" {}'.format(device, BUILD_PATH))

    print "[{}-{}] Launching {}".format(version, device, BUNDLE_ID)
    os.system('xcrun simctl launch "{}" {}'.format(device, BUNDLE_ID))
    

threads = []
for sim in simulators:
    t = threading.Thread(target=launch_sim, args=(sim,))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

