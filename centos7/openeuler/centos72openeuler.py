import os
import platform
import subprocess


def run_subprocess(cmd:str):
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


def check_pkg(rpm):
    _, ret = run_subprocess('rpm -q {}'.format(rpm))
    if ret:
        return
    return True


def get_disk_info(string):
    dev_name = ""
    part_num = ""
    length = len(string)
    for c in range(length - 1, -1, -1):
        if not string[c].isdigit():
            if string.find('nvme') != -1:
                dev_name = string[0:c]
                part_num = string[c + 1:length]
            else:
                dev_name = string[0:c + 1]
                part_num = string[c + 1:length]
            break
    return dev_name, part_num


def add_boot_option():
    """
    Current system is uefi, add boot option to boot manager.
    """
    subprocess.run('which efibootmgr > /dev/null 2>&1 || dnf install -y efibootmgr', shell=True)
    disk_name = subprocess.check_output('mount | grep /boot/efi | awk \'{print $1}\'', shell=True)
    disk_name = str(disk_name, 'utf-8')
    disk_name = disk_name.split('\n')[0]
    dev_name, part_num = get_disk_info(disk_name)
    if dev_name == "" or part_num == "":
        # "Parse /boot/efi disk info failed, update boot loader failed.
        return

    cmd = ""
    arch = platform.machine()
    openEuler_path = '/boot/efi/EFI/openEuler'
    if os.path.exists(openEuler_path):
        efi_name = 'openEuler'
    else:
        efi_name = 'uos'
    if arch == "x86_64":
        cmd = 'efibootmgr -c -d ' + dev_name + ' -p ' + part_num + ' -l "/EFI/{}/grubx86.efi" -L "openEuler"'.format(
            efi_name)
    elif arch == "aarch64":
        cmd = 'efibootmgr -c -d ' + dev_name + ' -p ' + part_num + ' -l "/EFI/{}/grubaa64.efi" -L "openEuler"'.format(
            efi_name)
    try:
        run_subprocess(cmd)
    except Exception as e:
        print(e)

def swap_release():
    tmp_dir = '/var/tmp'
    rpme_release = 'rpm -qf /etc/os-release|xargs -i rpm -e --nodeps {}'
    run_subprocess(rpme_release)
    cmd = 'yumdownloader {} --destdir {}'.format(openEuler_release, tmp_dir)
    run_subprocess(cmd)
    run_subprocess('rpm -ivh {}/*.rpm --nodeps --force'.format(tmp_dir))


def conf_grub():
    if os.path.isdir('/sys/firmware/efi'):
        old_kernel = '3.10.0'
        if old_kernel:
            run_subprocess('rpm -e --nodeps kernel-{}'.format(old_kernel))
            run_subprocess('dnf install -y shim')
        openEuler_path = '/boot/efi/EFI/openEuler'
        if not os.path.exists(openEuler_path):
            uos_path = '/boot/efi/EFI/openEuler'
        run_subprocess('grub2-mkconfig -o {}/grub.cfg'.format(openEuler_path))
        add_boot_option()
    else:
        run_subprocess('grub2-mkconfig -o /boot/grub2/grub.cfg')
        try:
            run_subprocess('test -L /boot/grub2/grubenv')
            run_subprocess('mv /boot/grub2/grubenv /boot/grub2/grubenv-bak')
            run_subprocess('cat /boot/grub2/grubenv-bak > /boot/grub2/grubenv')
        except Exception as e:
            print(e)


def system_sync():
    rebuilddb = 'rpm --rebuilddb;dnf clean all'
    run_subprocess(rebuilddb)
    cmd = 'dnf -y distro-sync --allowerasing --skip-broken'
    _, ret = run_subprocess(cmd)
    _, ret = run_subprocess('rpm -q kernel|grep {}'.format('uel20'))
    if ret:
        return False
    return True

def main():
    # 安装基础包
    os.system("yum install -y gdbm-help")

    remove_packages_nodeps = ['gdm', 'centos-logos', 'redhat-logos']
    for i in remove_packages_nodeps:
        nodeps_cmd = 'rpm -q {} && rpm -e --nodeps {}'.format(i, i)
        os.system(nodeps_cmd)

    openEuler_release = 'openEuler-release'
    if not self.check_pkg('rsync'):
        print('please install rsync')
        return
    if check_pkg("yum-utils"):
        print("please install yum-utils")
        return
    if not check_pkg(openEuler_release):
        swap_release()

    conf_grub()
    if system_sync():
        print("System Migration Successful")
    else:
        print("System Migration Failed")

if __name__ == '__main__':
    main()
