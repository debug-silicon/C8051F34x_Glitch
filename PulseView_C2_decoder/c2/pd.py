import sigrokdecode as srd


def log(s):
	with open('_c2.log', 'a+') as f:
		f.write(s + '\n')


SFR_descr = {
	0xE0: ('ACC', 'Accumulator'),
	0xBC: ('ADC0CF', 'ADC0 Configuration'),
	0xE8: ('ADC0CN', 'ADC0 Control'),
	0xC4: ('ADC0GTH', 'ADC0 Greater-Than Compare High'),
	0xC3: ('ADC0GTL', 'ADC0 Greater-Than Compare Low'),
	0xBE: ('ADC0H', 'ADC0 High'),
	0xBD: ('ADC0L', 'ADC0 Low'),
	0xC6: ('ADC0LTH', 'ADC0 Less-Than Compare Word High'),
	0xC5: ('ADC0LTL', 'ADC0 Less-Than Compare Word Low'),
	0xBA: ('AMX0N', 'AMUX0 Negative Channel Select'),
	0xBB: ('AMX0P', 'AMUX0 Positive Channel Select'),
	0xF0: ('B', 'B Register'),
	0x8E: ('CKCON', 'Clock Control'),
	0xB9: ('CLKMUL', 'Clock Multiplier'),
	0xA9: ('CLKSEL', 'Clock Select'),
	0x9B: ('CPT0CN', 'Comparator0 Control'),
	0x9D: ('CPT0MD', 'Comparator0 Mode Selection'),
	0x9F: ('CPT0MX', 'Comparator0 MUX Selection'),
	0x9A: ('CPT1CN', 'Comparator1 Control'),
	0x9C: ('CPT1MD', 'Comparator1 Mode Selection'),
	0x9E: ('CPT1MX', 'Comparator1 MUX Selection'),
	0x83: ('DPH', 'Data Pointer High'),
	0x82: ('DPL', 'Data Pointer Low'),
	0xE6: ('EIE1', 'Extended Interrupt Enable 1'),
	0xE7: ('EIE2', 'Extended Interrupt Enable 2'),
	0xF6: ('EIP1', 'Extended Interrupt Priority 1'),
	0xF7: ('EIP2', 'Extended Interrupt Priority 2'),
	0xAA: ('EMI0CN', 'External Memory Interface Control'),
	0x85: ('EMI0CF', 'External Memory Interface Configuration'),
	0x84: ('EMI0TC', 'External Memory Interface Timing'),
	0xB7: ('FLKEY', 'Flash Lock and Key'),
	0xB6: ('FLSCL', 'Flash Scale'),
	0xA8: ('IE', 'Interrupt Enable'),
	0xB8: ('IP', 'Interrupt Priority'),
	0xE4: ('IT01CF', 'INT0/INT1 Configuration'),
	0xB3: ('OSCICL', 'Internal Oscillator Calibration'),
	0xB2: ('OSCICN', 'Internal Oscillator Control'),
	0x86: ('OSCLCN', 'Internal Low-Frequency Oscillator Control'),
	0xB1: ('OSCXCN', 'External Oscillator Control'),
	0x80: ('P0', 'Port 0 Latch'),
	0xF1: ('P0MDIN', 'Port 0 Input Mode Configuration'),
	0xA4: ('P0MDOUT', 'Port 0 Output Mode Configuration'),
	0xD4: ('P0SKIP', 'Port 0 Skip'),
	0x90: ('P1', 'Port 1 Latch'),
	0xF2: ('P1MDIN', 'Port 1 Input Mode Configuration'),
	0xA5: ('P1MDOUT', 'Port 1 Output Mode Configuration'),
	0xD5: ('P1SKIP', 'Port 1 Skip'),
	0xA0: ('P2', 'Port 2 Latch'),
	0xF3: ('P2MDIN', 'Port 2 Input Mode Configuration'),
	0xA6: ('P2MDOUT', 'Port 2 Output Mode Configuration'),
	0xD6: ('P2SKIP', 'Port 2 Skip'),
	0xB0: ('P3', 'Port 3 Latch'),
	0xF4: ('P3MDIN', 'Port 3 Input Mode Configuration'),
	0xA7: ('P3MDOUT', 'Port 3 Output Mode Configuration'),
	0xDF: ('P3SKIP', 'Port 3Skip'),
	0xC7: ('P4', 'Port 4 Latch'),
	0xF5: ('P4MDIN', 'Port 4 Input Mode Configuration'),
	0xAE: ('P4MDOUT', 'Port 4 Output Mode Configuration'),
	0xD8: ('PCA0CN', 'PCA Control'),
	0xFC: ('PCA0CPH0', 'PCA Capture 0 High'),
	0xEA: ('PCA0CPH1', 'PCA Capture 1 High'),
	0xEC: ('PCA0CPH2', 'PCA Capture 2 High'),
	0xEE: ('PCA0CPH3', 'PCA Capture 3High'),
	0xFE: ('PCA0CPH4', 'PCA Capture 4 High'),
	0xFB: ('PCA0CPL0', 'PCA Capture 0 Low'),
	0xE9: ('PCA0CPL1', 'PCA Capture 1 Low'),
	0xEB: ('PCA0CPL2', 'PCA Capture 2 Low'),
	0xED: ('PCA0CPL3', 'PCA Capture 3 Low'),
	0xFD: ('PCA0CPL4', 'PCA Capture 4 Low'),
	0xDA: ('PCA0CPM0', 'PCA Module 0 Mode Register'),
	0xDB: ('PCA0CPM1', 'PCA Module 1 Mode Register'),
	0xDC: ('PCA0CPM2', 'PCA Module 2 Mode Register'),
	0xDD: ('PCA0CPM3', 'PCA Module 3 Mode Register'),
	0xDE: ('PCA0CPM4', 'PCA Module 4 Mode Register'),
	0xFA: ('PCA0H', 'PCA Counter High'),
	0xF9: ('PCA0L', 'PCA Counter Low'),
	0xD9: ('PCA0MD', 'PCA Mode'),
	0x87: ('PCON', 'Power Control'),
	0xAF: ('PFE0CN', 'Prefetch Engine Control', {
		'PFEN': (5, 5, {
			0: 'Prefetch engine is disabled',
			1: 'Prefetch engine is enabled',
			}),
		'FLBWE': (0, 0, {
			0: 'Each byte of a software FLASH write is written individually',
			1: 'FLASH bytes are written in groups of two',
			}),
		}),
	0x8F: ('PSCTL', 'Program Store R/W Control', {
		'PSEE': (1, 1, {
			0: 'Flash erasure disabled',
			1: 'Flash erasure enabled',
			}),
		'PSWE': (0, 0, {
			0: 'Writes to Flash disabled',
			1: 'Writes to Flash enabled',
			}),
		}),
	0xD0: ('PSW', 'Program Status Word'),
	0xD1: ('REF0CN', 'Voltage Reference Control'),
	0xC9: ('REG0CN', 'Voltage Regulator Control'),
	0xEF: ('RSTSRC', 'Reset Source Configuration/Status', {
		'USBRSF': (7, 7),
		'FERROR': (6, 6),
		'C0RSEF': (5, 5),
		'SWRSF' : (4, 4),
		'WDTRSF': (3, 3),
		'MCDRSF': (2, 2),
		'PORSF' : (1, 1),
		'PINRSF': (0, 0),
		}),
	0xAC: ('SBCON1', 'UART1 Baud Rate Generator Control'),
	0xB5: ('SBRLH1', 'UART1 Baud Rate Generator High'),
	0xB4: ('SBRLL1', 'UART1 Baud Rate Generator Low'),
	0xD3: ('SBUF1', 'UART1 Data Buffer'),
	0xD2: ('SCON1', 'UART1 Control'),
	0x99: ('SBUF0', 'UART0 Data Buffer'),
	0x98: ('SCON0', 'UART0 Control'),
	0xC1: ('SMB0CF', 'SMBus Configuration'),
	0xC0: ('SMB0CN', 'SMBus Control'),
	0xC2: ('SMB0DAT', 'SMBus Data'),
	0xE5: ('SMOD1', 'UART1 Mode'),
	0x81: ('SP', 'Stack Pointer'),
	0xA1: ('SPI0CFG', 'SPI Configuration'),
	0xA2: ('SPI0CKR', 'SPI Clock Rate Control'),
	0xF8: ('SPI0CN', 'SPI Control'),
	0xA3: ('SPI0DAT', 'SPI Data'),
	0x88: ('TCON', 'Timer/Counter Control'),
	0x8C: ('TH0', 'Timer/Counter 0 High'),
	0x8D: ('TH1', 'Timer/Counter 1 High'),
	0x8A: ('TL0', 'Timer/Counter 0 Low'),
	0x8B: ('TL1', 'Timer/Counter 1 Low'),
	0x89: ('TMOD', 'Timer/Counter Mode'),
	0xC8: ('TMR2CN', 'Timer/Counter 2 Control'),
	0xCD: ('TMR2H', 'Timer/Counter 2 High'),
	0xCC: ('TMR2L', 'Timer/Counter 2 Low'),
	0xCB: ('TMR2RLH', 'Timer/Counter 2 Reload High'),
	0xCA: ('TMR2RLL', 'Timer/Counter 2 Reload Low'),
	0x91: ('TMR3CN', 'Timer/Counter 3Control'),
	0x95: ('TMR3H', 'Timer/Counter 3 High'),
	0x94: ('TMR3L', 'Timer/Counter 3Low'),
	0x93: ('TMR3RLH', 'Timer/Counter 3 Reload High'),
	0x92: ('TMR3RLL', 'Timer/Counter 3 Reload Low'),
	0xFF: ('VDM0CN', 'VDD Monitor Control', {
		'VDMEN'  : (7, 7, {
			0: 'VDD Monitor Disabled',
			1: 'VDD Monitor Enabled',
			}),
		'VDDSTAT': (6, 6, {
			0: 'VDD is below the VDD monitor threshold',
			1: 'VDD is above the VDD monitor threshold',
			}),
		# bits 5-0 not always zero
		}),
	0x96: ('USB0ADR', 'USB0 Indirect Address Register'),
	0x97: ('USB0DAT', 'USB0 Data Register'),
	0xD7: ('USB0XCN', 'USB0 Transceiver Control'),
	0xE1: ('XBR0', 'Port I/O Crossbar Control 0'),
	0xE2: ('XBR1', 'Port I/O Crossbar Control 1'),
	0xE3: ('XBR2', 'Port I/O Crossbar Control 2'),
	# --- Programming Registers ---
	0x00: ('DEVICEID', 'Device ID Register', {
		'ID': (7, 0, {
			0x0F: 'F34x family',
			}),
		}),
	0x01: ('REVID', 'Revision ID Register'),
}


INS_DATA_READ  = 0b00
INS_DATA_WRITE = 0b01
INS_ADDR_READ  = 0b10
INS_ADDR_WRITE = 0b11

# --------------------------------------------------

class C2Cmd(object):
	def __init__(self, ts, name, val=None, vlen=0):
		super(C2Cmd, self).__init__()
		self.ts   = ts # [tstart, tend]
		self.name = name
		self.val  = val
		self.vlen = vlen

	def format_c2cmd_val(self):
		return '' if self.val == None else Decoder.format_data_with_len(self.val, self.vlen)

	def __str__(self):
		sv = self.format_c2cmd_val()
		sv = ' ' + sv if sv else ''
		return '%d:\t%s %s' % (self.ts[0], self.name, sv)


class HighLvlCmd(object):
	def __init__(self, ts, name, desc=None):
		super(HighLvlCmd, self).__init__()
		self.ts   = ts # [tstart, tend]
		self.name = name
		self.desc = desc

	def __str__(self):
		s = '' if self.desc == None else ';\t%s' % self.desc
		return '%d:\t%s%s' % (self.ts[0], self.name, s)


class Ann:
	BITS, START, INS, ADDRESS, LENGTH, DATA, WAIT, STOP, C2CMD, HLCMD = range(10)


class Decoder(srd.Decoder):
	api_version = 3
	id = 'C2'
	name = 'C2'
	longname = 'SiLabs C2'
	desc = 'SiLabs C2 debug protocol.'
	license = 'gplv2+'
	inputs = ['logic']
	outputs = []
	tags = ['Debug/trace']
	channels = (
		{'id': 'c2ck', 'name': 'D0', 'desc': 'C2 clock'},
		{'id': 'c2d', 'name': 'D1', 'desc': 'C2 Data'}
	)
	annotations = (
		('bit'   , 'Bit'),
		('start' , 'Start'),
		('ins'   , 'Instruction'),
		('addr'  , 'Address'),
		('length', 'Length'),
		('data'  , 'Data'),
		('wait'  , 'Wait'),
		('stop'  , 'Stop'),
		('c2cmd' , 'Command'),
		('hlcmd' , 'High level cmd'),
	)
	annotation_rows = (
		('bits', 'Bits', (Ann.BITS,)),
		('fields', 'Fields', (Ann.START, Ann.INS, Ann.ADDRESS, Ann.LENGTH, Ann.DATA, Ann.WAIT, Ann.STOP,)),
		('cmds', 'Commands', (Ann.C2CMD,)),
		('notes', 'Notes', (Ann.HLCMD,)),
	)

	def __init__(self):
		self.reset()

	def reset(self):
		self.samplerate = -1
		self.stb_pool = []

	def metadata(self, key, value):
		if key == srd.SRD_CONF_SAMPLERATE:
			self.samplerate = value

	def start(self):
		self.out_ann = self.register(srd.OUTPUT_ANN)

	# --------------------------------------------------

	def extract_bits(x, bit_num_high, bit_num_low):
		r = x >> bit_num_low
		r &= (1 << (bit_num_high - bit_num_low + 1)) - 1
		return r

	def format_data_with_len(data_val, len_val):
		s = '%%0%dX' % ((len_val + 1) * 2)
		return s % data_val

	def calc_stb_val(stb, edge):
		return stb[1][0] if edge == 'f' else stb[1][1]

	def calc_stbs_val(stbs, edge):
		s = ''.join([str(Decoder.calc_stb_val(stb, edge)) for stb in stbs])
		return int(s[::-1], 2)

	def conv_stbs_2_ts(stbs):
		return [stbs[0][0][0], stbs[-1][0][1]]

	def conv_c2cmds_2_ts(c2cmds):
		return [c2cmds[0].ts[0], c2cmds[-1].ts[1]]

	def get_SFR_descr(addr, c2cmd_name, val, vlen=0):
		assert vlen == 0, 'SRF description can be done only for 1 byte'
		arr  = '->' if c2cmd_name == 'DR' else '<-'
		if not addr in SFR_descr:
			desc = '[%02X] %s %02X' % (addr, arr, val)
		else:
			ll   = SFR_descr[addr]
			desc = '["%s"] %s %02X' % (ll[0], arr, val)
			if len(ll) == 3:
				l = []
				for fn, ft in ll[2].items():
					if len(ft) == 2:
						s = '%s=%X' % (fn, Decoder.extract_bits(val, ft[0], ft[1]))
					elif len(ft) == 3:
						v = Decoder.extract_bits(val, ft[0], ft[1])
						if v in ft[2]:
							s = '%s="%s"' % (fn, ft[2][v])
						else:
							s = '%s=%X' % (fn, v)
					else:
						assert False
					l.append(s)
				desc += ';\t' + ' '.join(l)
		return desc

	# --------------------------------------------------

	def stb_len(self, stb):
		ts = stb[0]
		return (ts[1] - ts[0]) / self.samplerate

	def is_usual_stb(self, stb):
		return self.stb_len(stb) > 20e-9 and self.stb_len(stb) < 5000e-9 # 20 ns - 5us

	def is_reset_stb(self, stb):
		return self.stb_len(stb) > 20e-6 # > 20 us

	def is_halt_stb(self, stb):
		next_stb = self.get_stb()
		ts_diff = (next_stb[0][0] - stb[0][0]) / self.samplerate
		self.push_to_stb_pool(next_stb)
		return ts_diff > 1e-3 # ms


	def get_stb(self):
		if len(self.stb_pool) > 0:
			stb = self.stb_pool[0]
			self.stb_pool = self.stb_pool[1:]
		else:
			(_, f_c2d) = self.wait({0: 'f'})
			f_ts = self.samplenum
			(_, r_c2d) = self.wait({0: 'r'})
			r_ts = self.samplenum
			stb = ((f_ts, r_ts), (f_c2d, r_c2d))
			assert self.is_usual_stb(stb) or self.is_reset_stb(stb), 'Wrong negative pulse width'
		return stb

	def push_to_stb_pool(self, stb):
		self.stb_pool.append(stb)

	def get_stbs(self, N):
		return [self.get_stb() for _ in range(N)]

	def get_stbs_until(self, edge, val):
		r = []
		while True:
			stb = self.get_stb()
			r.append(stb)
			if Decoder.calc_stb_val(stb, edge) == val:
				break
		return r

	def putx_ts(self, ts, desc):
		self.put(ts[0], ts[1], self.out_ann, desc)

	def putx_stb(self, stb, desc):
		self.putx_ts(stb[0], desc)

	def putx_stbs(self, stbs, desc):
		self.putx_ts(Decoder.conv_stbs_2_ts(stbs), desc)

	def putx_stbs_bits(self, stbs, edge):
		for stb in stbs:
			v = str(Decoder.calc_stb_val(stb, edge))
			self.putx_stb(stb, [Ann.BITS, [v]])

	def handle_instruction(self):
		ins_stbs = self.get_stbs(2)
		ins_val  = Decoder.calc_stbs_val(ins_stbs, 'r')
		self.putx_stbs_bits(ins_stbs, 'r')
		self.putx_stbs(ins_stbs, [Ann.INS, [str(ins_val)]])
		return ins_stbs, ins_val

	def handle_length(self):
		len_stbs = self.get_stbs(2)
		len_val  = Decoder.calc_stbs_val(len_stbs, 'r')
		self.putx_stbs_bits(len_stbs, 'r')
		self.putx_stbs(len_stbs, [Ann.LENGTH, [str(len_val)]])
		return len_stbs, len_val

	def handle_address(self, edge):
		addr_stbs = self.get_stbs(8)
		addr_val  = Decoder.calc_stbs_val(addr_stbs, edge)
		self.putx_stbs_bits(addr_stbs, edge)
		self.putx_stbs(addr_stbs, [Ann.ADDRESS, ['%02X' % addr_val]])
		return addr_stbs, addr_val

	def handle_data(self, len_val, edge):
		data_stbs = self.get_stbs((len_val + 1) * 8)
		data_val  = Decoder.calc_stbs_val(data_stbs, edge)
		self.putx_stbs_bits(data_stbs, edge)
		self.putx_stbs(data_stbs, [Ann.DATA, [Decoder.format_data_with_len(data_val, len_val)]])
		return data_stbs, data_val

	def handle_wait(self):
		wait_stbs = self.get_stbs_until('f', 1)
		self.putx_stbs_bits(wait_stbs, 'f')
		self.putx_stbs(wait_stbs, [Ann.WAIT, ['WAIT', 'W']])
		return wait_stbs

	def handle_reset(self, reset_stb):
		return C2Cmd(Decoder.conv_stbs_2_ts([reset_stb]), 'RST')

	def handle_halt(self, halt_stb):
		return C2Cmd(Decoder.conv_stbs_2_ts([halt_stb]), 'HLT')

	def handle_addr_read(self, prev_stbs):
		# handle high-z bus switch
		self.get_stb()

		# handle address write field
		addr_stbs, addr_val = self.handle_address('f')

		return C2Cmd(Decoder.conv_stbs_2_ts(prev_stbs + addr_stbs), 'AR', addr_val)

	def handle_addr_write(self, prev_stbs):
		# handle address write field
		_, addr_val = self.handle_address('r')

		# handle high-z stop
		stop_stb = self.get_stb()
		self.putx_stb(stop_stb, [Ann.STOP, ['STOP', 'P']])

		return C2Cmd(Decoder.conv_stbs_2_ts(prev_stbs + [stop_stb]), 'AW', addr_val)

	def handle_data_read(self, prev_stbs):
		# handle length field
		_, len_val = self.handle_length()

		# handle high-z bus switch
		self.get_stb()

		# handle wait cycle
		wait_stbs = self.handle_wait()

		# handle data field
		data_stbs, data_val = self.handle_data(len_val, 'f')

		assert len_val == 0, 'Need test' # 1 byte
		return C2Cmd(Decoder.conv_stbs_2_ts(prev_stbs + data_stbs), 'DR', data_val, len_val)

	def handle_data_write(self, prev_stbs):
		# handle length field
		_, len_val = self.handle_length()

		# handle data field
		_, data_val = self.handle_data(len_val, 'r')

		# handle high-z bus switch
		self.get_stb()

		# handle wait cycle
		wait_stbs = self.handle_wait()

		assert len_val == 0, 'Need test' # 1 byte
		return C2Cmd(Decoder.conv_stbs_2_ts(prev_stbs + wait_stbs), 'DW', data_val, len_val)

	def handle_frame(self, start_stb):
		C2_ins_handlers = {
			INS_ADDR_READ : self.handle_addr_read,
			INS_ADDR_WRITE: self.handle_addr_write,
			INS_DATA_READ : self.handle_data_read,
			INS_DATA_WRITE: self.handle_data_write,
		}

		# handle start
		self.putx_stb(start_stb, [Ann.START, ['START', 'S']])

		# handle instruction field
		ins_stbs, ins_val = self.handle_instruction()
		prev_stbs = [start_stb] + ins_stbs

		# handle different commands
		if ins_val in C2_ins_handlers:
			return C2_ins_handlers[ins_val](prev_stbs)
		else:
			raise Exception('Should not be here')

	def putx_c2cmd(self, c2cmd):
		full_c2cmd_name = {
			'RST': 'Reset',
			'AR' : 'Address read',
			'AW' : 'Address write',
			'DR' : 'Data read',
			'DW' : 'Data write',
			'HLT': 'Debug halt',
		}

		sv = c2cmd.format_c2cmd_val()
		sv = ' ' + sv if sv else ''
		sh = c2cmd.name + sv
		sl = full_c2cmd_name[c2cmd.name] + sv
		self.putx_ts(c2cmd.ts, [Ann.C2CMD, [sl, sh]])

	def get_c2cmd(self):
		stb = self.get_stb()

		# TODO: handle reset strobe in middle C2 command
		if self.is_reset_stb(stb):
			c2cmd = self.handle_reset(stb)
		elif self.is_halt_stb(stb):
			c2cmd = self.handle_halt(stb)
		elif self.is_usual_stb(stb):
			c2cmd = self.handle_frame(stb)
		else:
			raise Exception('Should not be here')

		self.putx_c2cmd(c2cmd)
		return c2cmd

	def apply_c2cmd(self, c2cmd):
		if c2cmd.name == 'RST':
			self.c2_addr = 0x00
		elif c2cmd.name == 'AW':
			self.c2_addr = c2cmd.val
		elif c2cmd.name == 'AR':
			self.c2_in_busy   = Decoder.extract_bits(c2cmd.val, 1, 1)
			self.c2_out_ready = Decoder.extract_bits(c2cmd.val, 0, 0)
		else:
			pass

	def get_next_c2_RST_or_DATA_cmd(self):
		while True:
			c2cmd = self.get_c2cmd()
			self.apply_c2cmd(c2cmd)
			if c2cmd.name in ['DR', 'DW', 'RST', 'HLT']:
				return c2cmd

	def get_next_c2_DATA_cmd(self):
		while True:
			c2cmd = self.get_c2cmd()
			self.apply_c2cmd(c2cmd)
			if c2cmd.name in ['DR', 'DW']:
				return c2cmd

	def get_next_c2_DW_cmd(self):
		c2cmd = self.get_next_c2_DATA_cmd()
		assert c2cmd.name == 'DW', 'Should be C2 Data Write command'
		return c2cmd

	def get_next_c2_DR_cmd(self):
		c2cmd = self.get_next_c2_DATA_cmd()
		assert c2cmd.name == 'DR', 'Should be C2 Data Read command'
		return c2cmd

	def putx_hlcmd(self, hlcmd):
		if hlcmd.name in ['DATA_READ', 'DATA_WRITE']:
			sh = hlcmd.desc
			sl = hlcmd.desc
		else:
			sh = hlcmd.name
			sl = '%s: %s' % (hlcmd.name, hlcmd.desc) if hlcmd.desc else sh
		self.putx_ts(hlcmd.ts, [Ann.HLCMD, [sl, sh]])

	def handle_HL_data_cmd(self, addr, c2cmd):
		desc = Decoder.get_SFR_descr(addr, c2cmd.name, c2cmd.val, c2cmd.vlen)
		name = 'DATA_READ' if c2cmd.name == 'DR' else 'DATA_WRITE'
		return HighLvlCmd(c2cmd.ts, name, desc)

	def handle_FPCTL_cmd(self, cmd):
		FPCTL_cmd_names = {
			0x00: 'RUN_NORMAL',
			0x01: 'PI_ACTIVATE',
			0x02: 'HALT_ALL',
			0x04: 'HALT_CORE', # but run SFR bus
			0x08: 'RUN_with_HLT',
		}

		if cmd.name == 'DW' and cmd.val in FPCTL_cmd_names:
			return HighLvlCmd(cmd.ts, FPCTL_cmd_names[cmd.val])
		else:
			return self.handle_HL_data_cmd(0x02, cmd)

	def handle_FPDAT_resp(self, hlcmd):
		resp = self.get_next_c2_DR_cmd()
		hlcmd.ts[1] = resp.ts[1] # patch end time
		if resp.val != 0x0D: # not OK
			desc = 'ERR=%02X' % resp.val
			hlcmd.desc  = hlcmd.desc + ' ' + desc if hlcmd.desc != None else desc
			return False
		return True

	def handle_FPDAT_single_step(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'DBG_STEP')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		return hlcmd

	def handle_FPDAT_get_version(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'GET_VERSION')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		ver = self.get_next_c2_DR_cmd()
		hlcmd.ts[1] = ver.ts[1]
		hlcmd.desc  = '%02X' % ver.val
		return hlcmd

	def handle_FPDAT_get_derivative(self, cmd):
		DERIVATIVE_names = {
			0x7D: 'C8051F340',
		}

		hlcmd = HighLvlCmd(cmd.ts, 'GET_DERIVATIVE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		ver = self.get_next_c2_DR_cmd()
		hlcmd.ts[1] = ver.ts[1]
		if ver.val in DERIVATIVE_names:
			hlcmd.desc = '%02X="%s"' % (ver.val, DERIVATIVE_names[ver.val])
		else:
			hlcmd.desc = '%02X' % ver.val
		return hlcmd

	def handle_FPDAT_device_erase(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'DEVICE_ERASE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		arm1 = self.get_next_c2_DW_cmd()
		assert arm1.val == 0xDE, 'Wrong arming sequence'
		arm2 = self.get_next_c2_DW_cmd()
		assert arm2.val == 0xAD, 'Wrong arming sequence'
		arm3 = self.get_next_c2_DW_cmd()
		assert arm3.val == 0xA5, 'Wrong arming sequence'

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		return hlcmd

	def handle_FPDAT_crc16_page(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'CRC16_PAGE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		page = self.get_next_c2_DW_cmd()
		crch = self.get_next_c2_DR_cmd()
		crcl = self.get_next_c2_DR_cmd()

		hlcmd.ts[1] = crch.ts[1]
		hlcmd.desc  = 'addr=%02X00 crc=%02X%02X' % (page.val, crch.val, crcl.val)

		return hlcmd

	def handle_FPDAT_BLK_addr_size(self, hlcmd):
		addr_h = self.get_next_c2_DW_cmd()
		addr_l = self.get_next_c2_DW_cmd()
		size_c = self.get_next_c2_DW_cmd()

		addr = (addr_h.val << 8) + addr_l.val
		size = 0x100 if size_c.val == 0x00 else size_c.val
		desc = 'addr=%04X size=%02X' % (addr, size)

		hlcmd.ts[1] = size_c.ts[1]
		hlcmd.desc  = hlcmd.desc + ' ' + desc if hlcmd.desc != None else desc

		return addr, size

	def handle_FPDAT_BKL_data_resp(self, hlcmd, size):
		data = b''

		for _ in range(size):
			resp = self.get_next_c2_DR_cmd()
			data += bytes([resp.val])

		s = ''.join(['%02X' % x for x in data])
		desc = 'data=%s' % s

		hlcmd.ts[1] = resp.ts[1]
		hlcmd.desc  = hlcmd.desc + ' ' + desc if hlcmd.desc != None else desc

		return data

	def handle_FPDAT_BKL_data_send(self, hlcmd, size):
		data = b''

		for _ in range(size):
			resp = self.get_next_c2_DW_cmd()
			data += bytes([resp.val])

		s = ''.join(['%02X' % x for x in data])
		desc = 'data=%s' % s

		hlcmd.ts[1] = resp.ts[1]
		hlcmd.desc  = hlcmd.desc + ' ' + desc if hlcmd.desc != None else desc

		return data

	def handle_FPDAT_block_read(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'BLOCK_READ')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		_, size = self.handle_FPDAT_BLK_addr_size(hlcmd)

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		self.handle_FPDAT_BKL_data_resp(hlcmd, size)

		return hlcmd

	def handle_FPDAT_block_write(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'BLOCK_WRITE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		_, size = self.handle_FPDAT_BLK_addr_size(hlcmd)

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		self.handle_FPDAT_BKL_data_send(hlcmd, size)

		return hlcmd

	def handle_FPDAT_page_erase(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'PAGE_ERASE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		page = self.get_next_c2_DW_cmd()
		hlcmd.desc = 'page=%02X' % page.val

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		conf = self.get_next_c2_DW_cmd() # Confirm ?
		assert conf.val == 0x00

		hlcmd.ts[1] = conf.ts[1]

		return hlcmd

	def handle_FPDAT_direct_read(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'DIRECT_READ')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		addr = self.get_next_c2_DW_cmd()
		size = self.get_next_c2_DW_cmd()

		if size.val == 0x01:
			data = self.get_next_c2_DR_cmd()
			hlcmd.ts[1] = data.ts[1]
			hlcmd.desc = Decoder.get_SFR_descr(addr.val, 'DR', data.val)
		else:
			hlcmd.desc = 'addr=%02X size=%02X' % (addr.val, size.val)
			self.handle_FPDAT_BKL_data_resp(hlcmd, size.val)

		return hlcmd

	def handle_FPDAT_direct_write(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'DIRECT_WRITE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		addr = self.get_next_c2_DW_cmd()
		size = self.get_next_c2_DW_cmd()
		assert size.val == 0x01 # TODO: handle other sizes
		data = self.get_next_c2_DW_cmd()
		
		hlcmd.ts[1] = data.ts[1]
		hlcmd.desc = Decoder.get_SFR_descr(addr.val, 'DW', data.val)

		return hlcmd

	def handle_FPDAT_indirect_read(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'INDIRECT_READ')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		addr = self.get_next_c2_DW_cmd()
		size = self.get_next_c2_DW_cmd()

		if size.val == 0x01:
			data = self.get_next_c2_DR_cmd()
			hlcmd.ts[1] = data.ts[1]
			hlcmd.desc = '[%02X] -> %02X' % (addr.val, data.val)
			# hlcmd.desc = Decoder.get_SFR_descr(addr.val, 'DR', data.val)
		else:
			hlcmd.desc = 'addr=%02X size=%02X' % (addr.val, size.val)
			self.handle_FPDAT_BKL_data_resp(hlcmd, size.val)

		return hlcmd

	def handle_FPDAT_indirect_write(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'INDIRECT_WRITE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		addr = self.get_next_c2_DW_cmd()
		size = self.get_next_c2_DW_cmd()
		assert size.val == 0x01 # TODO: handle other sizes
		data = self.get_next_c2_DW_cmd()

		hlcmd.ts[1] = data.ts[1]
		hlcmd.desc = '[%02X] <- %02X' % (addr.val, data.val)
		return hlcmd

	def handle_FPDAT_XRAM_read(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'XRAM_READ')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		_, size = self.handle_FPDAT_BLK_addr_size(hlcmd)

		self.handle_FPDAT_BKL_data_resp(hlcmd, size)

		return hlcmd

	def handle_FPDAT_XRAM_write(self, cmd):
		hlcmd = HighLvlCmd(cmd.ts, 'XRAM_WRITE')

		if not self.handle_FPDAT_resp(hlcmd):
			return hlcmd

		_, size = self.handle_FPDAT_BLK_addr_size(hlcmd)

		self.handle_FPDAT_BKL_data_send(hlcmd, size)

		return hlcmd

	def handle_FPDAT_cmd(self, cmd):
		FPDAT_cmd_handlers = {
			0x00: self.handle_FPDAT_single_step,
			0x01: self.handle_FPDAT_get_version,
			0x02: self.handle_FPDAT_get_derivative,
			0x03: self.handle_FPDAT_device_erase,
			0x05: self.handle_FPDAT_crc16_page,
			0x06: self.handle_FPDAT_block_read,
			0x07: self.handle_FPDAT_block_write,
			0x08: self.handle_FPDAT_page_erase,
			0x09: self.handle_FPDAT_direct_read,
			0x0A: self.handle_FPDAT_direct_write,
			0x0B: self.handle_FPDAT_indirect_read,
			0x0C: self.handle_FPDAT_indirect_write,
			0x0E: self.handle_FPDAT_XRAM_read,
			0x0F: self.handle_FPDAT_XRAM_write,
		}

		if cmd.name == 'DW' and cmd.val in FPDAT_cmd_handlers:
			return FPDAT_cmd_handlers[cmd.val](cmd)
		else:
			return self.handle_HL_data_cmd(0xAD, cmd)

	def get_hlcmd(self):
		PI_regs_handlers = {
			0x02: self.handle_FPCTL_cmd,
			0xAD: self.handle_FPDAT_cmd,
		}

		cmd  = self.get_next_c2_RST_or_DATA_cmd()

		if cmd.name == 'RST':
			hlcmd = HighLvlCmd(cmd.ts, 'RESET')
		elif cmd.name == 'HLT':
			hlcmd = HighLvlCmd(cmd.ts, 'DBG_HALT')
		else:
			addr = self.c2_addr
			if addr in PI_regs_handlers:
				hlcmd = PI_regs_handlers[addr](cmd)
			else:
				hlcmd = self.handle_HL_data_cmd(addr, cmd)

		self.putx_hlcmd(hlcmd)
		return hlcmd

	def decode(self):
		if self.samplerate <= 0:
			raise Exception('C2 is time dependent protocol')

		# TODO:
		# 1. High level parser as option
		while True:
			# cmd = self.get_c2cmd() # Parse only low-level C2 instructions
			cmd = self.get_hlcmd() # Parse high-level PI commands and low-level C2 instructions
			# log(str(cmd)) # Write to file if you want
