#!/bin/python3
# -*- coding: utf-8 -*-

####
# Program: hex2bin
# Author: Orange233
# Date: 2023 Jul 14th
####

# !WIP: 可以增加追加写入结果。
# !WIP: 增加选项，设置程序仅识别大写字母，并启用非安全检查模式来加快解码速度。

import os
import sys

def __proc_direct(origin: str) -> tuple[str, str]:
	return origin, None

hex_proc_functions = {
	'direct': __proc_direct
}

def __drop_warn(warn: str) -> None:
	pass

def __hex_to_halfbyte(hex: str) -> int:
	hex = ord(hex)
	if ord('0') <= hex and hex <= ord('9'):
		return hex - ord('0')
	elif ord('A') <= hex and hex <= ord('F'):
		return hex - ord('A') + 10
	elif ord('a') <= hex and hex <= ord('f'):
		return hex - ord('a') + 10

def __hex_to_byte(high: str, low: str) -> int:
	r = (__hex_to_halfbyte(high) << 4) | __hex_to_halfbyte(low)
	return r

def __decode(hex_str: str, warn_func) -> tuple[bytes, str]:
	if len(hex_str) % 2 == 1:
		warn_func('Numbers are not paired. Automatically supplded a 0 as low bit.')
		hex_str += '0'

	r = bytearray()
	i = 0
	while i < len(hex_str):
		high = hex_str[i]
		low = hex_str[i + 1]

		byte = __hex_to_byte(high, low)
		r.append(byte)

		i = i + 2
	return bytes(r)

def decode_main(hex_str: str, mode: str, warn_func) -> tuple[bytes, str]:
	if warn_func is None:
		warn_func = __drop_warn

	# 先重新组合字符串
	mode = mode.lower()
	if mode not in hex_proc_functions:
		return None, 'Mode "' + mode + '" not found.'
	hex_str, err = hex_proc_functions[mode](hex_str)
	if err is not None:
		return None, err

	#解码
	r = __decode(hex_str, warn_func)
	return r, None

def __print_warn(warn: str) -> None:
	print(warn)


def __save(result: bytes, output_path: str) -> None:
	# [head:1]
	# -> is_exists:
	#    *y -> ask_overwrite:
	#          *y -> goto save.
	#          *N -> [ask:2]
	#                -> ask_continue_save:
	#                   *Y -> ask_new_path:
	#                         -> goto head.
	#                   *n -> done.
	#    *n -> [save:3]
	#          -> try_open_file:
	#             *err -> goto ask.
	#             *ok -> save:
	#                    -> done.
	# [done:0]

	flag = 1
	while flag > 0:
		if flag == 1: #[head]
			if os.path.exists(output_path): #is_exists
				# *y:
				# ask_overwrite:
				input_str = input('Output file has been exists. Do you want to overwrite it? [yes/No] ')
				input_str = input_str.lower()

				if input_str not in ['yes', 'y']:
					# *N:
					flag = 2 #goto ask.
				else:
					# *y:
					flag = 3 #goto save.
			else:
				# *n:
				flag = 3 #goto save.
		
		elif flag == 2: #[ask]
			# ask_continue_save:
			input_str = input('Do you want to continue saving (use other path to save the result)? [Yes/no] ')
			input_str = input_str.lower()

			if input_str not in ['no', 'n']:
				# *Y:
				# ask_new_path:
				output_path = input('Path to save: ')
				flag = 1 #goto head.
			else: 
				# *n:
				flag = 0 #done.

		elif flag == 3: #[save]
			# try_open_file:
			file = None
			try:
				file = open(output_path, 'wb')
			except Exception as e:
				print(e)
			
			if file is None:
				# *err:
				flag = 2 #goto ask.
			else:
				# *ok:
				# save:

				file.write(result)
				file.close()

				print('Saved to "' + output_path + '".')

				flag = 0 #done.
		else:
			# unknown:
			try:
				raise Exception('Unknown error.')
			except Exception as e:
				print(e)
			flag = 2 #goto ask.

if __name__ == '__main__':
	# `python hex2bin.py out.bin direct "a1" `

	__hex_str = sys.argv[3]
	__mode = sys.argv[2]
	__output_path = sys.argv[1]

	__result, __err = decode_main(__hex_str, __mode, __print_warn)

	if __err is not None:
		print('Error: ' + __err)
		os._exit(-1)
	
	__save(__result, __output_path)

	os._exit(0)