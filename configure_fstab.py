#! /usr/bin/env python3
from __future__ import absolute_import, print_function, unicode_literals

import io
import sys
from collections import OrderedDict


def configure_fstab(fstabpath):
    """
    http://ideaheap.com/2013/07/stopping-sd-card-corruption-on-a-raspberry-pi/
    https://raspberrypi.stackexchange.com/questions/169/how-can-i-extend-the-life-of-my-sd-card
    https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=20505
    https://raspberrypi.stackexchange.com/questions/70/how-to-set-up-swap-space/1605#1605
    https://www.zdnet.com/article/raspberry-pi-extending-the-life-of-the-sd-card/
    http://oils-of-life.com/blog/linux/reduce-writes-to-the-raspberry-pi-sd-card/
    https://raspberrypi.stackexchange.com/questions/62533/how-can-i-reduce-the-writing-to-log-files/62536#62536

    https://help.ubuntu.com/community/Fstab

    https://kwilson.io/blog/force-your-raspberry-pi-to-mount-an-external-usb-drive-every-time-it-starts-up/
    https://gist.github.com/etes/aa76a6e9c80579872e5f
    https://wiki.archlinux.org/index.php/fstab#External_devices
    https://raspberrypi.stackexchange.com/questions/66169/auto-mount-usb-stick-on-plug-in-without-uuid
    https://www.linuxquestions.org/questions/linux-server-73/raspberry-pi-move-home-and-var-folders-to-usb-hdd-4175467848/
    http://www.kupply.com/move-your-raspberry-pi-system-to-usb-in-10-steps/
    https://narcisocerezo.wordpress.com/2014/06/25/create-a-robust-raspberry-pi-setup-for-24x7-operation/
    https://svopil.com/extend-life-of-sd-card-by-adding-additional-usb-hdd.php

    https://superuser.com/questions/479379/how-long-can-file-system-writes-be-cached-with-ext4/479384#479384
    https://unix.stackexchange.com/questions/155784/advantages-disadvantages-of-increasing-commit-in-fstab

    > mount man page
    https://linux.die.net/man/8/mount
    """
    max_len_device = 8
    str_device = '# <device>'
    max_len_mount_point = 13
    str_mount_point = '<mount_point>'
    max_len_fstype = 9
    str_fstype = '<fs_type>'
    max_len_options = 9
    str_options = '<options>'
    max_len_dump = 6
    str_dump = '<dump>'
    max_len_pass = 1
    str_pass = '<pass_num>'

    # TODO: detect and modify according to symlinks for /tmp and /run

    expected_mount_points = [
        '/proc',
        '/boot',
        '/',
        '/tmp',
        '/run',
        '/var/log',
        '/var/cache/apt/archives',
    ]
    mount_points_defaults = {
        # TODO: verify that all of the mount options are correct
        '/boot': OrderedDict([
            ('skip', False),
            ('options', 'defaults,noatime,ro'),
        ]),
        '/': OrderedDict([
            ('skip', False),
            ('options', 'defaults,noatime,commit=60'),
        ]),
        '/tmp': OrderedDict([
            ('skip', False),
            ('device', 'tmpfs'),
            ('mount_point', '/tmp'),
            ('fs_type', 'tmpfs'),
            # ('options', 'defaults,nodev,noatime,nosuid,size=200M,mode=1777'),
            # unfortunately, things like pip can use a lot when installing packages
            ('options', 'defaults,nodev,noatime,nosuid,mode=1777'),
            ('dump', '0'),
            ('pass', '0'),
        ]),
        '/run': OrderedDict([
            ('skip', False),
            ('device', 'tmpfs'),
            ('mount_point', '/run'),
            ('fs_type', 'tmpfs'),
            ('options', 'defaults,noatime,nosuid,size=2M,mode=0777'),
            ('dump', '0'),
            ('pass', '0'),
        ]),
        '/var/log': OrderedDict([
            ('skip', False),
            ('device', 'tmpfs'),
            ('mount_point', '/var/log'),
            ('fs_type', 'tmpfs'),
            ('options', 'defaults,noatime,nosuid,size=100M,mode=0755'),
            ('dump', '0'),
            ('pass', '0'),
        ]),
        '/var/cache/apt/archives': OrderedDict([
            ('skip', False),
            ('device', 'tmpfs'),
            ('mount_point', '/var/cache/apt/archives'),
            ('fs_type', 'tmpfs'),
            ('options', 'defaults,noexec,nosuid,nodev,mode=0755'),
            ('dump', '0'),
            ('pass', '0'),
        ]),
        # '/': OrderedDict([
        #     # tmpfs  /var/cache/samba  tmpfs  size=5M,nodev,nosuid  0  0
        #     ('skip', False),
        # ]),
        # '/': OrderedDict([
        #     # tmpfs /var/spool/mqueue tmpfs defaults,noatime,nosuid,mode=0700,gid=12,size=30m 0 0
        #     ('skip', False),
        # ]),
        # '/': OrderedDict([
        #     # /dev/mapper/RootFS-Root /  ext4    noatime,discard,errors=remount-ro 0  1
        #     # /dev/mapper/HomeFS-Home /home  ext4    noatime,discard,defaults     0   2
        #     ('skip', False),
        # ]),
    }

    input_lines = list()
    output_lines = list()

    print('loading fstab file...')
    with io.open(fstabpath, mode='r', encoding='utf8') as fstab:
        for rawline in fstab:
            line = OrderedDict()
            line['raw'] = rawline
            line['line'] = rawline.strip()
            line['skip'] = bool(not line['line'] or line['line'].startswith('#'))
            line['device'] = None
            line['mount_point'] = None
            line['fs_type'] = None
            line['options'] = None
            line['dump'] = None
            line['pass'] = None

            if not line['skip']:
                parts = line['line'].split()
                if len(parts) < 6:
                    line['skip'] = True
                    print('ERROR: invalid line {0}'.format(repr(line['line'])))
                    continue
                if len(parts) > 7:
                    print('WARNING: expected 6 parts, found {0}'.format(len(parts)))
                    print('WARNING: {0}'.format(repr(line['line'])))
                    line['extra'] = parts[6:]

                line['device'] = parts[0]
                line['mount_point'] = parts[1]
                line['fs_type'] = parts[2]
                line['options'] = parts[3]
                line['dump'] = parts[4]
                line['pass'] = parts[5]

                try:
                    expected_mount_points.remove(line['mount_point'])
                except ValueError:
                    pass
            else:
                swap_comment_1 = 'swapfile is not a swap partition'
                swap_comment_2 = 'dphys-swapfile swap[on|off]'
                if swap_comment_1 in line['line'] or swap_comment_2 in line['line']:
                    continue

            input_lines.append(line)

    if not input_lines:
        print('ERROR: no lines read from fstab file!')
        sys.exit(42)

    print('adding missing mount points...')
    # print('{0}'.format(expected_mount_points))
    for missing in expected_mount_points:
        if missing in mount_points_defaults:
            input_lines.append(mount_points_defaults[missing])
        else:
            print('WARNING: no defaults for mount point {0}'.format(missing))

    print('processing fstab entries...')
    for entry in input_lines:
        if entry['skip']:
            continue

        mount_point = entry['mount_point']
        entry_options = entry['options']

        if mount_point == '/proc':
            if int(entry['dump']) != 0:
                print('WARNING: /proc dump = {0} != 0'.format(entry['dump']))
            if int(entry['pass']) != 0:
                print('WARNING: /proc pass = {0} != 0'.format(entry['pass']))

        elif mount_point == '/boot':
            if int(entry['dump']) != 0:
                print('WARNING: /boot dump = {0} != 0'.format(entry['dump']))
            if int(entry['pass']) != 2:
                print('WARNING: /boot pass = {0} != 2'.format(entry['pass']))
            if entry['fs_type'] != 'vfat':
                print('WARNING: /boot expected vfat not {0}'.format(entry['fs_type']))

            if entry_options == 'defaults':
                entry['options'] = mount_points_defaults['/boot']['options']

        elif mount_point == '/':
            if int(entry['dump']) != 0:
                print('WARNING: / dump = {0} != 0'.format(entry['dump']))
            if int(entry['pass']) != 1:
                print('WARNING: / pass = {0} != 1'.format(entry['pass']))
            if entry['fs_type'] != 'ext4':
                print('WARNING: / expected ext4 not {0}'.format(entry['fs_type']))

            if entry_options == 'defaults' or entry_options == 'defaults,noatime':
                entry['options'] = mount_points_defaults['/']['options']

        elif mount_point in mount_points_defaults and entry is mount_points_defaults[mount_point]:
            # don't need to do anything if we're using the defaults object
            # print('DEBUG: same object')
            pass

        elif mount_point in mount_points_defaults:
            mpdata = mount_points_defaults[mount_point]

            if entry['device'] != mpdata['device']:
                print('WARNING: {0} != {1}'.format(entry['device'], mpdata['device']))
            if entry['mount_point'] != mpdata['mount_point']:
                print('WARNING: {0} != {1}'.format(entry['mount_point'], mpdata['mount_point']))
            if entry['fs_type'] != mpdata['fs_type']:
                print('WARNING: {0} != {1}'.format(entry['fs_type'], mpdata['fs_type']))
            if entry['options'] != mpdata['options']:
                print('WARNING: {0} != {1}'.format(entry['options'], mpdata['options']))
                entry['options'] = mpdata['options']
            if entry['dump'] != mpdata['dump']:
                print('WARNING: {0} != {1}'.format(entry['dump'], mpdata['dump']))
                entry['dump'] = mpdata['dump']
            if entry['pass'] != mpdata['pass']:
                print('WARNING: {0} != {1}'.format(entry['pass'], mpdata['pass']))
                entry['pass'] = mpdata['pass']

        else:
            # leave it alone; it was added externally or manually by user
            pass

        max_len_device = max(max_len_device, len(entry['device']))
        max_len_mount_point = max(max_len_mount_point, len(entry['mount_point']))
        max_len_fstype = max(max_len_fstype, len(entry['fs_type']))
        max_len_options = max(max_len_options, len(entry['options']))
        max_len_dump = max(max_len_dump, len(entry['dump']))
        max_len_pass = max(max_len_pass, len(entry['pass']))

    print('assembling output format...')
    max_len_device = max(max_len_device, len(str_device))
    max_len_mount_point = max(max_len_mount_point, len(str_mount_point))
    max_len_fstype = max(max_len_fstype, len(str_fstype))
    max_len_options = max(max_len_options, len(str_options))
    max_len_dump = max(max_len_dump, len(str_dump))
    fstab_template = (
        '{{device:<{0}}}  {{mount_point:<{1}}}  {{fs_type:<{2}}}  '
        '{{options:<{3}}}  {{dump:<{4}}}  {{pass_num:<{5}}}\n'
    ).format(
        max_len_device, max_len_mount_point, max_len_fstype,
        max_len_options, max_len_dump, max_len_pass
    )

    print('ensuring fstab fields header...')
    if str_mount_point not in input_lines[0]['raw'] and str_fstype not in input_lines[0]['raw']:
        print('WARNING: adding fstab fields header')
        output_lines.append(fstab_template.format(
            device=str_device,
            mount_point=str_mount_point,
            fs_type=str_fstype,
            options=str_options,
            dump=str_dump,
            pass_num=str_pass
        ))

    print('generating output fstab...')
    for line in input_lines:
        if line['skip']:
            output_lines.append(line['raw'])
            continue

        output_lines.append(fstab_template.format(
            device=line['device'],
            mount_point=line['mount_point'],
            fs_type=line['fs_type'],
            options=line['options'],
            dump=line['dump'],
            pass_num=line['pass']
        ))

    print('writing output to fstab file...')
    with io.open(fstabpath, mode='w', encoding='utf8') as outputfile:
        for line in output_lines:
            outputfile.write(line)

    print('done.')


if __name__ == '__main__':
    configure_fstab(sys.argv[1])
