#!/usr/bin/env python3

from array import array
from sys import argv, exit, getsizeof
from struct import pack_into, unpack_from

def ceil4(n):
	"""returns the next integer which is a multiple of 4"""
	return (n + 3) & ~3

if len(argv)!=2:
	exit(2)

filename = argv[1]
in_file = open(filename, "rb")
buf	 = in_file.read()
in_file.close()

if filename.lower().endswith(".ttc"):
	filename = filename[:-4]


if buf[:4] != b"ttcf":
	out_filename = "%s.ttf" % filename
	out_file = open(out_filename, "wb")
	out_file.write(buf)

else:
	ttf_count = unpack_from("!L", buf, 0x08)[0]
	ttf_offset_array = unpack_from("!"+ttf_count*"L", buf, 0x0C)
	for i in range(ttf_count):
		table_header_offset = ttf_offset_array[i]
		table_count =  unpack_from("!H", buf, table_header_offset+0x04)[0]
		header_length = 0x0C + table_count * 0x10
		
		table_length = 0
		for j in range(table_count):
			length = unpack_from("!L", buf, table_header_offset+0x0C+0x0C+j*0x10)[0]
			table_length += ceil4(length)
		
		total_length = header_length + table_length
		new_buf = bytearray(total_length)
		header = unpack_from(header_length*"c", buf, table_header_offset)
		pack_into(header_length*"c", new_buf, 0, *header)
		current_offset = header_length
		
		for j in range(table_count):
			offset = unpack_from("!L", buf, table_header_offset+0x0C+0x08+j*0x10)[0]
			length = unpack_from("!L", buf, table_header_offset+0x0C+0x0C+j*0x10)[0]
			pack_into("!L", new_buf, 0x0C+0x08+j*0x10, current_offset)
			current_table = unpack_from(length*"c", buf, offset)
			pack_into(length*"c", new_buf, current_offset, *current_table)
			
			current_offset += ceil4(length)
		
		out_filename = "%s%d.ttf" % (filename, i)
		print(out_filename)
		out_file = open(out_filename, "wb")
		out_file.write(new_buf)
