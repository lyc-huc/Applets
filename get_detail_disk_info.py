# -*-coding:utf-8-*-
import binascii
import re

"""
device_type={'type_guid':'',' lba_start','lba_end':'','partition_mbyte'}
"""
DISK_IS_GPT = 0
DISK_IS_MBR = 1
PARTITION_TABLE_SECTOR = 32
ONE_SECTOR_BYTES = 512


def check_gpt_or_mbr(device):
    """
    this is device is gpt or mbr
    :param device: mount device
    :return:0 is gpt，1 is mbr
    """
    with open(device, 'rb') as disk:
        disk_type = disk.read(ONE_SECTOR_BYTES)[450]
        if disk_type == 238:  # ee的十进制为238
            return DISK_IS_GPT
        else:
            return DISK_IS_MBR


def sort_out_partition_item_guid(guid_str):
    """
    this is calc guid
    :param guid_str:guid_str is hex str
    :return: update_guid
    """
    test = str(guid_str)
    guid = "".join([i for index, i in enumerate(test) if index != 0]).replace('\'', '')
    footer = guid[-12:]
    intermediate1 = guid[-16:-12]
    intermediate0 = guid[12:16]  # d211
    result = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", guid[:12]).split(' ')
    result1 = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", intermediate0).split(' ')
    intermediate0 = "".join(result1[::-1])  # 11d2
    header = "".join(result[:4][::-1])
    intermediate = "".join(result[4:][::-1])
    update_guid = header + '-' + intermediate + '-' + intermediate0 + '-' + intermediate1 + '-' + footer
    return update_guid


def split_first_sector(b_stream, device_type):
    step = 128 if device_type == DISK_IS_GPT else 16
    for _i in range(0, len(b_stream), step):
        yield b_stream[_i:_i + step]


def partition_info_gpt(disk, device_type):
    device_info = []  # Used to store disk information
    for i in range(PARTITION_TABLE_SECTOR):  # Iterate through the sectors of 32 partition table entries
        byte_stream = disk.read(ONE_SECTOR_BYTES)
        if i > 1 and int(binascii.b2a_hex(byte_stream), 16) != 0:
            for partition in split_first_sector(byte_stream, device_type):
                check = binascii.b2a_hex(partition)
                partition_info = {}  # Used to store partition information
                if int(check, 16) != 0:
                    partition_info['type_guid'] = sort_out_partition_item_guid(
                        binascii.b2a_hex(partition[0:16]))
                    partition_info['lba_start'] = int.from_bytes(partition[32:40], 'little')
                    partition_info['lba_end'] = int.from_bytes(partition[40:48], 'little')
                    partition_mbyte = (partition_info['lba_end'] - partition_info[
                        'lba_start'] + 1) * ONE_SECTOR_BYTES // (
                                              1024 * 1024)
                    partition_info['partition_mbyte'] = partition_mbyte
                    device_info.append(partition_info)
    return device_info


def partition_info_mbr(disk, device_type):
    device_info = []
    header_bytes = disk.read(ONE_SECTOR_BYTES)
    partition_info = header_bytes[446:510]
    for partition in split_first_sector(partition_info, device_type):
        check = binascii.b2a_hex(partition)
        partition_info = {}
        check_activity = hex(partition[0])
        if int(check,16) != 0:  # Check if the partition table entry is a meaningful partition table entry and is the active partition

            partition_info['check_activity'] = check_activity
            partition_info['check_main'] = hex(partition[4])
            partition_info['lba_start'] = int.from_bytes(partition[8:12], 'little')
            sum_sector = int.from_bytes(partition[12:16], 'little')
            partition_info['lba_end'] = sum_sector + partition_info['lba_start']
            partition_info['partition_mbyte'] = (partition_info['lba_end'] - partition_info[
                'lba_start'] + 1) * ONE_SECTOR_BYTES // (1024 * 1024)
            device_info.append(partition_info)
    return device_info


def from_sector_partition_item(device):
    """
    statistics disk information
    :param device:mount device
    :return:device_info
    """
    device_type = check_gpt_or_mbr(device)

    with open(device, 'rb') as disk:
        if device_type == DISK_IS_GPT:  # Gpt partition when equal to 0
            return partition_info_gpt(disk, device_type), device_type
        else:
            result = [i for i in partition_info_mbr(disk, device_type) if i['check_activity'] == '0x80']
            return result, device_type


if __name__ == "__main__":
    # gpt_or_mbr=0 is gpt or gpt_or_mbr=mbr
    disk_info, gpt_or_mbr = from_sector_partition_item('\\\\.\\PHYSICALDRIVE0')
    for i in disk_info:
        print(i)
    print(gpt_or_mbr)