__author__ = 'Owner'
import math
cur_num = 0
index = 1
max = 16
get_from = cur_num
while index < max:
    get_from = (cur_num+(2**(index-1))) % 2**max % max
    if not cur_num == get_from:
        print get_from
    index += 1