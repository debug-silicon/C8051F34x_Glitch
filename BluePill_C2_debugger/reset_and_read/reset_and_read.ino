#define PIN_C2CK PB3
#define PIN_C2D  PB4
#define PIN_TRIG PB5

#define C2_DEVID 0x00
#define C2_REVID 0x01
#define C2_FPCTL 0x02
#define C2_FPDAT 0xAD

#define PI_GET_VERSION    0x01
#define PI_GET_DERIVATIVE 0x02
#define PI_DEVICE_ERASE   0x03
#define PI_BLOCK_READ     0x06
#define PI_BLOCK_WRITE    0x07
#define PI_PAGE_ERASE     0x08
#define PI_DIRECT_READ    0x09
#define PI_DIRECT_WRITE   0x0A
#define PI_INDIRECT_READ  0x0B
#define PI_INDIRECT_WRITE 0x0C

#define TRY_COUNT_WAIT 100
#define TRY_COUNT_FPDAT_POLL 20


typedef unsigned char  u8;
typedef unsigned short u16;
typedef unsigned int   u32;


void setup() {
	pinMode(LED_BUILTIN, OUTPUT);
	digitalWrite(LED_BUILTIN, HIGH);

	pinMode(PIN_C2CK, INPUT);
	pinMode(PIN_C2D, INPUT);

	pinMode(PIN_TRIG, OUTPUT);
	digitalWrite(PIN_TRIG, LOW);

	Serial.setTimeout(10);
}


void enable_C2CK() {
	digitalWrite(PIN_C2CK, HIGH);
	pinMode(PIN_C2CK, OUTPUT);
}


void disable_C2CK() {
	digitalWrite(PIN_C2CK, HIGH);
	pinMode(PIN_C2CK, INPUT);
}


void enable_C2D() {
	digitalWrite(PIN_C2D, HIGH);
	pinMode(PIN_C2D, OUTPUT);
}


void disable_C2D() {
	digitalWrite(PIN_C2D, HIGH);
	pinMode(PIN_C2D, INPUT);
}


void reset() {
	enable_C2CK();
	digitalWrite(PIN_C2CK, LOW);
	delayMicroseconds(25);
	digitalWrite(PIN_C2CK, HIGH);
	disable_C2CK();
	delayMicroseconds(5);
}


void strobe() {
	digitalWrite(PIN_C2CK, LOW);
	digitalWrite(PIN_C2CK, HIGH);
	digitalWrite(PIN_C2CK, HIGH); // just for delay
}


void send_INS(u8 ins) {
	digitalWrite(PIN_C2D, (ins & 0x01) ? HIGH : LOW);
	strobe();
	digitalWrite(PIN_C2D, (ins & 0x02) ? HIGH : LOW);
	strobe();
}


void send_LENGTH(u8 len) {
	digitalWrite(PIN_C2D, (len & 0x01) ? HIGH : LOW);
	strobe();
	digitalWrite(PIN_C2D, (len & 0x02) ? HIGH : LOW);
	strobe();
}


bool addr_write(u8 addr) {
	enable_C2CK();
	
	// START field
	strobe();
	enable_C2D();

	// INS field
	send_INS(0x03);

	// ADDRESS field
	for(u8 i = 0; i < 8; ++i) {
		digitalWrite(PIN_C2D, (addr & 0x01) ? HIGH : LOW);
		strobe();
		addr >>= 1;
	}
	disable_C2D();

	// STOP field
	strobe();
	disable_C2CK();
	return true;
}


bool addr_read(u8 *dst) {
	enable_C2CK();
	
	// START field
	strobe();
	enable_C2D();

	// INS field
	send_INS(0x02);

	disable_C2D();
	strobe();

	// ADDRESS field
	u8 addr = 0;
	for(u8 i = 0; i < 8; ++i) {
		addr >>= 1;
		if (digitalRead(PIN_C2D) == HIGH)
			addr |= 0x80;
		strobe();
	}
	*dst = addr;

	// STOP field
	disable_C2CK();
	return true;
}


bool data_write(u8 data) {
	enable_C2CK();
	
	// START field
	strobe();
	enable_C2D();

	// INS field
	send_INS(0x01);

	// LENGTH field
	send_LENGTH(0x00); // 1 byte

	// DATA field
	for(u8 i = 0; i < 8; ++i) {
		digitalWrite(PIN_C2D, (data & 0x01) ? HIGH : LOW);
		strobe();
		data = data >> 1;
	}

	// WAIT field
	disable_C2D();
	strobe();
	u32 try_count = 0;
	while (digitalRead(PIN_C2D) == LOW) {
		if (try_count++ >= TRY_COUNT_WAIT) {
			disable_C2CK();
			return false;
		}
		strobe();
	}

	// STOP field
	strobe();
	disable_C2CK();
	return true;
}


bool data_read(u8 *dst) {
	enable_C2CK();
	
	// START field
	strobe();
	enable_C2D();

	// INS field
	send_INS(0x00);

	// LENGTH field
	send_LENGTH(0x00); // 1 byte

	disable_C2D();
	strobe();

	// WAIT field
	u32 try_count = 0;
	while (digitalRead(PIN_C2D) == LOW) {
		if (try_count++ >= TRY_COUNT_WAIT) {
			disable_C2CK();
			return false;
		}
		strobe();
	}
	strobe(); // last WAIT strobe

	// DATA field
	u8 data = 0;
	for(u8 i = 0; i < 8; ++i) {
		data >>= 1;
		if (digitalRead(PIN_C2D) == HIGH)
			data |= 0x80;
		strobe();
	}
	*dst = data;

	// STOP field
	disable_C2CK();
	return true;
}


bool fpdat_poll_in_busy() {
	u8 status = 0;
	for (u32 try_count = 0; try_count < TRY_COUNT_FPDAT_POLL; ++try_count) {
		if (!addr_read(&status))
			return false;
		if ((status & 0x02) == 0)
			return true;
	}
	return false;
}


bool fpdat_poll_out_ready() {
	u8 status = 0;
	for (u32 try_count = 0; try_count < TRY_COUNT_FPDAT_POLL; ++try_count) {
		if (!addr_read(&status))
			return false;
		if (status & 0x01)
			return true;
	}
	return false;
}


bool fpdat_write_data(u8 data) {
	if (data_write(data))
		if (fpdat_poll_in_busy())
			return true;
	return false;
}


// 0x03 error - locked Flash
static u8 g_last_error = 0;

bool fpdat_check_resp() {
	if (fpdat_poll_out_ready())
		if (data_read(&g_last_error))
			return (g_last_error == 0x0D);
	return false;
}


bool fpdat_read_data(u8 *dst) {
	if (fpdat_poll_out_ready())
		if (data_read(dst))
			return true;
	return false;
}


bool pi_write_sfr(u8 addr, u8 data) {
	if (addr_write(addr))
		if (data_write(data))
			return true;
	return false;
}


bool pi_read_sfr(u8 addr, u8 *dst) {
	if (addr_write(addr))
		if (data_read(dst))
			return true;
	return false;
}


u8 pi_exec_simple_cmd(u8 cmd, u8 *resp) {
	if (addr_write(C2_FPDAT))
		if (fpdat_write_data(cmd))
			if (fpdat_check_resp())
				if (fpdat_read_data(resp))
					return true;
	return false;
}


bool pi_block_read(u16 addr, u8 *dst, u8 len) {
	if (!addr_write(C2_FPDAT))
		return false;

	if (!fpdat_write_data(PI_BLOCK_READ))
		return false;
	if (!fpdat_check_resp())
		return false;

	if (!fpdat_write_data(addr >> 8))
		return false;
	if (!fpdat_write_data(addr & 0xFF))
		return false;
	if (!fpdat_write_data(len))
		return false;
	if (!fpdat_check_resp())
		return false;

	while(len--)
		if (!fpdat_read_data(dst++))
			return false;
	return true;
}

// ++++++++++++ TRIG ++++++++++++++++

void strobe_trig() {
	digitalWrite(PIN_TRIG, HIGH);
	digitalWrite(PIN_C2CK, LOW);
	digitalWrite(PIN_C2CK, HIGH);
	digitalWrite(PIN_C2CK, HIGH);
	digitalWrite(PIN_TRIG, LOW);
}


bool data_write_WAIT_trig(u8 data) {
	enable_C2CK();
	
	// START field
	strobe();
	enable_C2D();

	// INS field
	send_INS(0x01);

	// LENGTH field
	send_LENGTH(0x00);

	// DATA field
	for(u8 i = 0; i < 8; ++i) {
		digitalWrite(PIN_C2D, (data & 0x01) ? HIGH : LOW);
		strobe();
		data = data >> 1;
	}

	// WAIT field
	disable_C2D();
	strobe_trig(); // bus switch here

	// to not interfere with glitch on oscillogram
	delayMicroseconds(20);

	u32 try_count = 0;
	while (digitalRead(PIN_C2D) == LOW) {
		if (try_count++ >= TRY_COUNT_WAIT) {
			disable_C2CK();
			return false;
		}
		strobe();
	}

	// STOP field
	strobe();
	disable_C2CK();
	return true;
}


bool fpdat_write_data_trig(u8 data) {
	if (data_write_WAIT_trig(data))
		if (fpdat_poll_in_busy())
			return true;
	return false;
}


bool pi_block_read_trig(u16 addr, u8 *dst, u8 len) {
	if (!addr_write(C2_FPDAT))
		return false;

	if (!fpdat_write_data(PI_BLOCK_READ)) // glitch here
		return false;
	if (!fpdat_check_resp())
		return false;

	if (!fpdat_write_data(addr >> 8))
		return false;
	if (!fpdat_write_data(addr & 0xFF))
		return false;
	if (!fpdat_write_data_trig(len)) // or glitch here
		return false;
	if (!fpdat_check_resp())
		return false;

	int rd_len = (len == 0x00) ? 0x100 : len;
	while(rd_len--)
		if (!fpdat_read_data(dst++))
			return false;
	return true;
}

// ++++++++++++++ MAIN ++++++++++++++++++

static u32 g_total_counter = 0;
static u16 g_read_addr     = 0xFBFF;
static u8  g_read_len      = 0x01;
static u8  g_read_buf[0x100];

void do_reset_and_flash_read() {
	noInterrupts();

	reset();
	delayMicroseconds(100);

	// PI Initialization Sequence
	addr_write(C2_FPCTL);
	delayMicroseconds(100);
	data_write(0x02);
	delayMicroseconds(100);
	data_write(0x04);
	delayMicroseconds(100);
	data_write(0x01);

	// AN127 says that the delay should be 20ms
	// but 2ms works fine, SPA shows that PI already inited
	delayMicroseconds(2000); 

	g_last_error = 0xFF; // 0xFF error - timeout
	bool read_res = pi_block_read_trig(g_read_addr, g_read_buf, g_read_len);

	interrupts();

	char tmp[0x40];
	if (read_res) {
		snprintf(tmp, sizeof(tmp), "[%04X] = ", g_read_addr);
		Serial.print(tmp);

		int rd_len = (g_read_len == 0x00) ? 0x100 : g_read_len;
		for (int i = 0; i < rd_len; ++i) {
			snprintf(tmp, sizeof(tmp), "%02X", g_read_buf[i]);
			Serial.print(tmp);
		}
		
		snprintf(tmp, sizeof(tmp), "; TC = %08X", g_total_counter++);
		Serial.println(tmp);
	} else {
		snprintf(tmp, sizeof(tmp), "[!] read block error %02X; TC = %08X", g_last_error, g_total_counter++);
		Serial.println(tmp);
	}
}


u8 hex2num(char ch) {
	u8 r = 0;
	if ((ch >= '0') && (ch <= '9'))
		r = (u8)(ch - '0');
	if ((ch >= 'a') && (ch <= 'f'))
		r = (u8)(ch - 'a' + 10);
	if ((ch >= 'A') && (ch <= 'F'))
		r = (u8)(ch - 'A' + 10);
	return r;
}


void parse_read_cmd(char *s) {
	g_read_addr = (hex2num(s[0]) << 12) + (hex2num(s[1]) << 8) + (hex2num(s[2]) << 4) + hex2num(s[3]);
	g_read_len  = (hex2num(s[5]) << 4) + hex2num(s[6]);

	char tmp[0x20];
	snprintf(tmp, sizeof(tmp), "addr = %04X; len = %02X", g_read_addr, g_read_len);
	Serial.println(tmp);
}


void parse_cmd(char *buf) {
	switch (buf[0]) {
		case 'R':
		case 'r':
			parse_read_cmd(buf + 2);
			break;
		default:
			Serial.println("Unknown cmd");
			break;
	}
}


void loop() {
	// "R FBFF 01\n" - cmd format, only sets addr and size values for next attempts
	// the real attempt only happens after single '\n' character
	char tmp[10];

	while (Serial.available() > 0) {
		char new_char = Serial.read();

		if (new_char == '\n') {
			do_reset_and_flash_read();
		} else {
			tmp[0] = new_char;
			int n = Serial.readBytes(tmp+1, sizeof(tmp)-1);

			if ((n == sizeof(tmp)-1) && (tmp[sizeof(tmp)-1] == '\n') && (tmp[1] == ' ') && (tmp[6] == ' ')) {
				parse_cmd(tmp);
			} else {
				Serial.println("Wrong cmd format");
			}
		}
	}
}
