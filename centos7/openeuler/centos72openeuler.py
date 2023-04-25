import os
import subprocess

def run_subprocess(cmd=""):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        shell=True
    )
    output = ""
    try:
        for line in iter(process.stdout.readline, b""):
            output += line.decode()
            print(line.decode())
    except:
        pass
    process.communicate()
    return_code = process.poll()
    return output, return_code

def system_sync():
    rebuilddb = 'rpm --rebuilddb;dnf clean all'
    os.system(rebuilddb)
    cmd = 'dnf -y distro-sync --allowerasing --skip-broken'
    os.system(cmd)

def main():
    system_cross_sync()

if __name__ == '__main__':
    main()