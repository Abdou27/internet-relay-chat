import subprocess
import threading
import time


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def server():
    for line in execute(["python", "Server.py", "65432"]):
        print(line, end="")


def client(name):
    print("Here")
    for line in execute(["python", "client.py", name, "65432"]):
        print(line, end="")


threading.Thread(target=server).start()
time.sleep(1)
threading.Thread(target=client, args=("Rahim",)).start()
time.sleep(1)
threading.Thread(target=client, args=("Maha",)).start()
