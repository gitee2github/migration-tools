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


def check_pkg(self, rpm):
    _, ret = run_subprocess('rpm -q {}'.format(rpm))
    if ret:
        return
    return True


def swap_release(self):
    openEuler_release = 'openEuler-release'
    tmp_dir = '/var/tmp'
    rpme_release = 'rpm -qf /etc/os-release|xargs -i rpm -e --nodeps {}'
    run_subprocess(rpme_release)
    cmd = 'yumdownloader {} --destdir {}'.format(openEuler_release, tmp_dir)
    run_subprocess(cmd)
    run_subprocess('rpm -ivh {}/*.rpm --nodeps --force'.format(tmp_dir))


def system_sync():
    rebuilddb = 'rpm --rebuilddb;dnf clean all'
    run_subprocess(rebuilddb)
    cmd = 'dnf -y distro-sync --allowerasing --skip-broken'
    _, ret = run_subprocess(cmd)
    if ret:
        return False
    return True

def main():
    system_cross_sync()

if __name__ == '__main__':
    main()
