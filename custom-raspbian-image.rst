Create Custom Raspbian Image
================================

Preparing the Image
-------------------------

1. Download and write base image to disk (dd onto disk)

    sudo parted /dev/sda resizepart 2 3000
    sudo resize2fs /dev/sda2

    NOTE: MUST update both the cmdline.txt and the fstab!!!


2. mount the root and boot partitions of the disk

    pi@raspberrypi:/mnt/img_fs $ sudo fdisk -l /mnt/seagate1tb/raspbian/2018-05-15-raspbian-stretch-custom.img

    Disk /mnt/seagate1tb/raspbian/2018-05-15-raspbian-stretch-custom.img: 1.8 GiB, 1862270976 bytes, 3637248 sectors
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disklabel type: dos
    Disk identifier: 0xc7cb7e34

    Device                                                           Boot Start     End Sectors  Size Id Type
    /mnt/seagate1tb/raspbian/2018-05-15-raspbian-stretch-custom.img1       8192   96453   88262 43.1M  c W95 FAT32 (LBA)
    /mnt/seagate1tb/raspbian/2018-05-15-raspbian-stretch-custom.img2      98304 3637247 3538944  1.7G 83 Linux

    sudo mount -o loop,offset=4194304 /mnt/seagate1tb/raspbian/2018-05-15-raspbian-stretch-custom.img /mnt/img_boot
    sudo mount -o loop,offset=50331648 /mnt/seagate1tb/raspbian/2018-05-15-raspbian-stretch-custom.img /mnt/img_fs


3. backup the cmdline.txt file

    sudo cp /mnt/img_boot/cmdline.txt /mnt/img_boot/cmdline.txt.bak


4. disable the auto-expanding of the root partition and filesystem on first boot

    dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=c7cb7e34-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh

    dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=c7cb7e34-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet


5. disable renaming network interfaces

    dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=c7cb7e34-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet

    dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=c7cb7e34-02 rootfstype=ext4 elevator=deadline fsck.repair=yes net.ifnames=0 rootwait quiet


6. enable SSH access and disable password login
https://learnaddict.com/2016/02/23/modifying-a-raspberry-pi-raspbian-image-on-linux/

    sudo touch /mnt/img_boot/ssh
    mkdir -p /mnt/img_fs/home/pi/.ssh

    TODO: disable password login


7. add authorized_keys with host pubkey

    touch /mnt/img_fs/home/pi/.ssh/authorized_keys
    touch /mnt/img_fs/home/pi/.ssh/known_hosts

    nano /mnt/img_fs/home/pi/.ssh/authorized_keys
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDBTmHe6U8hiJY3jf6R8WGs9JbcO8pZuoaPJ//u15OgLcawmkUj2WID/Xpvk6CwAdkZItw+oqQ6jomNkxBdRDxRlaFpCvV8IQ3rk6mcg0ElvmfWxrzE6MLS0f974E+22t95kroJVKkfiXT46WdHHvlhsiIBabTeyGVW25HosyouGjBuSWJOzWiKGzWUtZ699q75lP4BnIXJYXlwjma8IDdwTIqAxpaw0xIeCDegOBCoaoAu2duA8+SeHA9vH17fqba0pgG5udbzSD8i7q6gjzsdBYo/gaRPYwyE2+SXpA9Hb2EK/3i5tMpUWUTFe1DwkGm6pwXVgNBvmGhfUQ5JH/FX kraken@neuroticnerd.com

    # check that the user id of the files are correct
    sudo ls -lan /mnt/img_fs/home/pi
    sudo ls -lan /mnt/img_fs/home/pi/.ssh

    # if not then set them to the correct user id
    sudo chown -R 1000:1000 /mnt/img_fs/home/pi/.ssh


8. change the pi user password

    TODO


9. force HDMI into "monitor" modes

    sudo nano /mnt/img_boot/config.txt

    # force a HDMI mode to get audio
    hdmi_drive=2
    # set monitor mode to DMT
    hdmi_group=2
    # optionally set monitor resolution
    #hdmi_mode=1


10. change default keyboard layout to US

    sudo nano /mnt/img_fs/etc/default/keyboard

    XKBMODEL="pc104"
    XKBLAYOUT="us"


11. place a wpa_supplicant.conf file in the boot partition

    sudo touch /mnt/img_boot/wpa_supplicant.conf

    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=US

    network={
            id_str="home777"
            scan_ssid=1
            ssid="sudo_chmod_777"
            psk=41f98c49bda6def132df6613d174630d94d32d4967cf46bd9ea595a0867fe1c6
            key_mgmt=WPA-PSK
            priority=1
    }

    network={
            id_str="home700"
            scan_ssid=1
            ssid="sudo_chmod_700"
            psk=ea32673bd2cbe19146af29dc312703d1588b5e4ffd6064924293f10ff13350ff
            key_mgmt=WPA-PSK
            priority=2
    }




X. put the partition resizing on first run back in
