# pip install pyserial

import time
import struct
import serial


class C2_DBG(object):
	C2_ADDR_FPCTL = 0x02
	C2_ADDR_FPDAT = 0xAD

	FPDAT_POLL_TRY_COUNT         = 20
	FPDAT_POLL_TRY_COUNT_CRC     = 100
	FPDAT_POLL_TRY_COUNT_PAGE_ER = 50
	FPDAT_POLL_TRY_COUNT_DEV_ER  = 6000

	FPDAT_CMD_SINGLE_STEP    = 0x00
	FPDAT_CMD_GET_VERSION    = 0x01
	FPDAT_CMD_GET_DERIVATIVE = 0x02
	FPDAT_CMD_DEVICE_ERASE   = 0x03
	FPDAT_CMD_CRC16_PAGE     = 0x05
	FPDAT_CMD_BLOCK_READ     = 0x06
	FPDAT_CMD_BLOCK_WRITE    = 0x07
	FPDAT_CMD_PAGE_ERASE     = 0x08
	FPDAT_CMD_DIRECT_READ    = 0x09
	FPDAT_CMD_DIRECT_WRITE   = 0x0A
	FPDAT_CMD_INDIRECT_READ  = 0x0B
	FPDAT_CMD_INDIRECT_WRITE = 0x0C
	FPDAT_CMD_XRAM_READ      = 0x0E
	FPDAT_CMD_XRAM_WRITE     = 0x0F

	FPDAT_RESP_OK = 0x0D

	SCRATCH_ADDR_PC = 0x20

	def __init__(self, port_name):
		self.dev = serial.Serial(port_name, timeout=0.1)
		self.debug = False
		self._c2_addr_reg_val = None

	def close(self):
		self.dev.close()

	def _bp_send(self, s):
		if self.debug:
			print('> %s' % s)
		if len(s) < 5:
			s += ' ' * (5 - len(s))
		b = s.encode('ascii') + b'\n'
		assert len(b) == 6
		self.dev.write(b)

	def _bp_recv(self):
		b = self.dev.read_until(expected=b'\r\n')
		s = b.decode('ascii').strip('\r\n')
		if self.debug:
			print('< %s' % s)
		if not s.startswith('OK'):
			raise Exception(s)
		return s[2:].strip(' ')

	def bp_exec_cmd(self, cmd):
		self._bp_send(cmd)
		return self._bp_recv()

	def set_trig(self, count=1):
		assert count < 0x10
		return self.bp_exec_cmd('TRG %X' % count)

	def reset(self):
		self._c2_addr_reg_val = 0x00
		return self.bp_exec_cmd('RST')

	def halt(self):
		self.bp_exec_cmd('HLT')
		# time.sleep(0.001)

	def hack(self):
		self.bp_exec_cmd('HACK')

	def c2_addr_write(self, addr):
		if addr != self._c2_addr_reg_val:
			self._c2_addr_reg_val = addr
			return self.bp_exec_cmd('AW %02X' % addr)

	def c2_addr_read(self):
		return int(self.bp_exec_cmd('AR'), 16)

	def c2_data_write(self, data):
		return self.bp_exec_cmd('DW %02X' % data)

	def c2_data_read(self):
		return int(self.bp_exec_cmd('DR'), 16)

	def c2_reg_write(self, addr, data):
		self.c2_addr_write(addr)
		return self.c2_data_write(data)

	def c2_reg_read(self, addr):
		self.c2_addr_write(addr)
		return self.c2_data_read()

	def c2_block_read(self, addr, size):
		data = b''
		for i in range(size):
			data += bytes([self.c2_reg_read(addr + i)])
		return data

	def fpdat_start_cmd(self):
		self.c2_addr_write(C2_DBG.C2_ADDR_FPDAT)

	def fpdat_check_in_busy_eq0(self):
		return (self.c2_addr_read() & 0x02) == 0

	def fpdat_check_out_ready_eq1(self):
		return (self.c2_addr_read() & 0x01) == 1

	def fpdat_poll_in_busy(self):
		for _ in range(C2_DBG.FPDAT_POLL_TRY_COUNT):
			if self.fpdat_check_in_busy_eq0():
				return
		raise Exception('Timeout: FPDAT in busy')

	def fpdat_poll_out_ready(self):
		for _ in range(C2_DBG.FPDAT_POLL_TRY_COUNT):
			if self.fpdat_check_out_ready_eq1():
				return
		raise Exception('Timeout: FPDAT out ready')

	def fpdat_write_data(self, data):
		self.c2_data_write(data)
		self.fpdat_poll_in_busy()

	def fpdat_read_data(self):
		self.fpdat_poll_out_ready()
		return self.c2_data_read()

	def fpdat_check_resp(self):
		resp = self.fpdat_read_data()
		if resp != C2_DBG.FPDAT_RESP_OK:
			raise Exception('FPDAT: resp = %02X' % resp)

	def pi_init_sequence(self):
		self.reset()
		# time.sleep(0.002)
		self.c2_addr_write(C2_DBG.C2_ADDR_FPCTL)
		self.c2_data_write(0x02)
		self.c2_data_write(0x04)
		self.c2_data_write(0x01)
		time.sleep(0.02)

	def pi_dbg_resume(self):
		self.c2_addr_write(C2_DBG.C2_ADDR_FPCTL)
		self.c2_data_write(0x08)

	def pi_simple_cmd(self, cmd):
		self.fpdat_start_cmd()
		self.fpdat_write_data(cmd)
		self.fpdat_check_resp()
		return self.fpdat_read_data()

	def pi_get_version(self):
		return self.pi_simple_cmd(C2_DBG.FPDAT_CMD_GET_VERSION)

	def pi_get_derivative(self):
		return self.pi_simple_cmd(C2_DBG.FPDAT_CMD_GET_DERIVATIVE)

	def pi_device_erase(self):
		self.fpdat_start_cmd()
		self.fpdat_write_data(C2_DBG.FPDAT_CMD_DEVICE_ERASE)
		self.fpdat_check_resp()

		self.fpdat_write_data(0xDE)
		self.fpdat_write_data(0xAD)
		self.fpdat_write_data(0xA5)

		for _ in range(C2_DBG.FPDAT_POLL_TRY_COUNT_DEV_ER):
			if self.fpdat_check_out_ready_eq1():
				self.fpdat_check_resp()
				return
		raise Exception('Timeout: device erase')

	def pi_send_BLK_addr16_size8(self, addr, size):
		self.fpdat_write_data(addr >> 8)
		self.fpdat_write_data(addr & 0xFF)
		self.fpdat_write_data(0x00 if size == 0x100 else size)

	def pi_send_BLK_addr8_size8(self, addr, size):
		self.fpdat_write_data(addr)
		self.fpdat_write_data(0x00 if size == 0x100 else size)

	def pi_recv_BLK_data(self, size):
		data = b''
		for _ in range(size):
			data += bytes([self.fpdat_read_data()])
		return data

	def pi_send_BLK_data(self, data):
		for b in data:
			self.fpdat_write_data(b)

	def pi_flash_read(self, addr, size):
		assert addr >= 0 and addr < 0x10000
		assert size > 0 and size <= 0x100
		self.fpdat_start_cmd()
		self.fpdat_write_data(C2_DBG.FPDAT_CMD_BLOCK_READ)
		self.fpdat_check_resp()

		self.pi_send_BLK_addr16_size8(addr, size)
		self.fpdat_check_resp()

		return self.pi_recv_BLK_data(size)

	def pi_flash_write(self, addr, data):
		size = len(data)
		assert addr >= 0 and addr < 0x10000
		assert size > 0 and size <= 0x100
		self.fpdat_start_cmd()
		self.fpdat_write_data(C2_DBG.FPDAT_CMD_BLOCK_WRITE)
		self.fpdat_check_resp()

		self.pi_send_BLK_addr16_size8(addr, size)
		self.fpdat_check_resp()

		return self.pi_send_BLK_data(data)

	def pi_page_erase(self, addr):
		page_size = 0x200
		assert addr >= 0 and addr < 0x10000
		assert addr % page_size == 0
		self.fpdat_start_cmd()
		self.fpdat_write_data(C2_DBG.FPDAT_CMD_PAGE_ERASE)
		self.fpdat_check_resp()

		self.fpdat_write_data(addr//page_size)
		self.fpdat_check_resp()

		# send confirm ?
		self.fpdat_write_data(0x00)
		for _ in range(C2_DBG.FPDAT_POLL_TRY_COUNT_PAGE_ER):
			if self.fpdat_check_out_ready_eq1():
				return
		raise Exception('Timeout: page erase')

	def pi_mem_write(self, cmd, addr, data):
		if type(data) == int:
			data = bytes([data])
		size = len(data)
		assert addr >= 0 and addr < 0x100
		assert size > 0 and size <= 0x100
		self.fpdat_start_cmd()
		self.fpdat_write_data(cmd)
		self.fpdat_check_resp()

		self.pi_send_BLK_addr8_size8(addr, size)

		return self.pi_send_BLK_data(data)

	def pi_mem_read(self, cmd, addr, size):
		assert addr >= 0 and addr < 0x100
		assert size > 0 and size <= 0x100
		self.fpdat_start_cmd()
		self.fpdat_write_data(cmd)
		self.fpdat_check_resp()

		self.pi_send_BLK_addr8_size8(addr, size)

		data = self.pi_recv_BLK_data(size)
		return data[0] if len(data) == 1 else data

	def pi_direct_write(self, addr, data):
		return self.pi_mem_write(C2_DBG.FPDAT_CMD_DIRECT_WRITE, addr, data)

	def pi_direct_read(self, addr, size=1):
		return self.pi_mem_read(C2_DBG.FPDAT_CMD_DIRECT_READ, addr, size)

	def pi_indirect_write(self, addr, data):
		return self.pi_mem_write(C2_DBG.FPDAT_CMD_INDIRECT_WRITE, addr, data)

	def pi_indirect_read(self, addr, size=1):
		return self.pi_mem_read(C2_DBG.FPDAT_CMD_INDIRECT_READ, addr, size)

	def pi_crc16_calc(self, addr):
		assert addr >= 0 and addr < 0x10000
		assert addr & 0xFF == 0
		self.fpdat_start_cmd()
		self.fpdat_write_data(C2_DBG.FPDAT_CMD_CRC16_PAGE)
		self.fpdat_check_resp()

		self.fpdat_write_data(addr >> 8)
		for _ in range(C2_DBG.FPDAT_POLL_TRY_COUNT_CRC):
			if self.fpdat_check_out_ready_eq1():
				return (self.c2_data_read() << 8) + self.fpdat_read_data()
		raise Exception('Timeout: CRC16')

	def dbg_get_PC(self):
		return struct.unpack('<H', self.pi_direct_read(C2_DBG.SCRATCH_ADDR_PC, 2))[0]

	def dbg_set_PC(self, new_PC):
		self.pi_direct_write(C2_DBG.SCRATCH_ADDR_PC, struct.pack('<H', new_PC))


def CRC16(data):
	crc = 0
	for b in data:
		crc ^= b << 8
		for _ in range(8):
			if (crc & 0x8000) > 0:
				crc = (crc << 1) ^ 0x1021
			else:
				crc <<= 1
			crc &= 0xFFFF
	return crc


def get_file_content(fname):
	with open(fname, 'rb') as f:
		return f.read()


def save_to_file(fname, data):
	with open(fname, 'wb') as f:
		f.write(data)


def print_hex_dump(data, addr=0):
	for i in range(len(data)):
		if i % 0x10 == 0:
			if i > 0:
				print()
			print('%08X:' % (addr + i), end='')
		print(' %02X' % data[i], end='')
	print()


def read_all_C2_regs(dbg):
	data = b''
	for addr in range(0x100):
		data += bytes([dbg.c2_reg_read(addr)])
	return data


def dump_flash(dbg, start_addr=0, end_addr=0xFC00):
	dbg.pi_init_sequence()
	data = b''
	for addr in range(start_addr, end_addr, 0x100):
		data += dbg.pi_flash_read(addr, 0x100)
	return data


def program_flash(dbg, data):
	def is_chunk_empty(data):
		return data == b'\xFF' * len(data)

	flash_size = 0xFC00
	chunk_size = 0x100
	page_size  = 0x200
	assert len(data) == flash_size

	dbg.pi_init_sequence()
	for page_addr in range(0, flash_size, page_size):
		page_data = data[page_addr:page_addr+page_size]
		if not is_chunk_empty(page_data):
			print('Erase page addr=%04X' % page_addr)
			dbg.pi_page_erase(page_addr)
			for chunk_idx in range(page_size//chunk_size):
				chunk_addr = page_addr + chunk_size * chunk_idx
				chunk_data = data[chunk_addr:chunk_addr+chunk_size]
				if not is_chunk_empty(chunk_data):
					print('Write flash chunk addr=%04X' % chunk_addr)
					dbg.pi_flash_write(chunk_addr, chunk_data)
					assert CRC16(chunk_data) == dbg.pi_crc16_calc(chunk_addr)


def parse_hex_file(fname):
	data = bytearray([0xFF] * 0xFC00)
	ext_addr = 0
	with open(fname, 'r') as f:
		for l in f:
			l = l.strip('\r\n')
			l = l.strip(':')
			b = bytes.fromhex(l)
			f_dlen = b[0]
			f_addr = struct.unpack('>H', b[1:3])[0]
			f_type = b[3]
			f_data = b[4:-1]
			f_chsm = b[-1]
			assert f_dlen == len(f_data)
			assert sum(b) & 0xFF == 0
			if f_type == 0:
				for i in range(len(f_data)):
					n_addr = (ext_addr << 16) + f_addr + i
					n_byte = f_data[i]
					data[n_addr] = n_byte
			elif f_type == 1:
				# end of HEX file
				pass
			elif f_type == 4:
				ext_addr = struct.unpack('>H', f_data)[0]
			else:
				raise Exception('HEX-file: unknown record type')
	return bytes(data)


def erase_device(port_name):
	dbg = C2_DBG(port_name)
	dbg.pi_init_sequence()
	dbg.pi_device_erase()
	dbg.reset()
	print('--- Erase done ---')


def program_hex_file(port_name):
	hex_fname = 'inf_loop_locked.hex'
	dbg = C2_DBG(port_name)
	dbg.pi_init_sequence()
	program_flash(dbg, parse_hex_file(hex_fname))
	dbg.reset()
	print('--- Programming done ---')


def erase_and_program(port_name):
	erase_device(port_name)
	program_hex_file(port_name)
	quit()


def main():
	port_name = 'COM5'
	# erase_and_program(port_name)
	dbg = C2_DBG(port_name)

	dbg.set_trig()
	dbg.reset()

	dbg.c2_reg_write(0xA0, 0x04) # Enable LED without halting core
	dbg.c2_reg_write(0xE2, 0x40) # Enable I/O Crossbar
	dbg.c2_reg_write(0xA6, dbg.c2_reg_read(0xA6)|0x04) # make LED pin output push-pull


if __name__ == '__main__':
	main()
