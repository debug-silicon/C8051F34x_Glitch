#define PIN_C2CK PB3
#define PIN_C2D  PB4
#define PIN_TRIG PB5

#define C2_DEVID 0x00
#define C2_REVID 0x01
#define C2_FPCTL 0x02
#define C2_FPDAT 0xAD

#define TRY_COUNT_WAIT 100

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;


void setup() {
	pinMode(LED_BUILTIN, OUTPUT);
	digitalWrite(LED_BUILTIN, HIGH); // HIGH - LED disabled

	pinMode(PIN_C2CK, INPUT);
	pinMode(PIN_C2D,  INPUT);

	pinMode(PIN_TRIG, OUTPUT);
	digitalWrite(PIN_TRIG, LOW);

	Serial.begin(115200);
	Serial.setTimeout(10);
}


static u8 g_trig_counter = 0;
static u8 g_disable_interrupts = 1;


void enable_C2CK() {
	if (g_disable_interrupts)
		noInterrupts();

	digitalWrite(LED_BUILTIN, LOW);

	digitalWrite(PIN_C2CK, HIGH);
	pinMode(PIN_C2CK, OUTPUT);

	if (g_trig_counter)
		digitalWrite(PIN_TRIG, HIGH);
}


void disable_C2CK() {
	if (g_trig_counter) {
		digitalWrite(PIN_TRIG, LOW);
		g_trig_counter--;
	}

	digitalWrite(PIN_C2CK, HIGH);
	pinMode(PIN_C2CK, INPUT);

	digitalWrite(LED_BUILTIN, HIGH);

	if (g_disable_interrupts)
		interrupts();
}


void enable_C2D() {
	digitalWrite(PIN_C2D, HIGH);
	pinMode(PIN_C2D, OUTPUT);
}


void disable_C2D() {
	digitalWrite(PIN_C2D, HIGH);
	pinMode(PIN_C2D, INPUT);
}


void strobe() {
	digitalWrite(PIN_C2CK, LOW);
	digitalWrite(PIN_C2CK, HIGH);
	digitalWrite(PIN_C2CK, HIGH);
}


void reset() {
	enable_C2CK();
	digitalWrite(PIN_C2CK, LOW);
	delayMicroseconds(25);
	digitalWrite(PIN_C2CK, HIGH);
	disable_C2CK();
	// delayMicroseconds(5);
}


void halt() {
	enable_C2CK();
	strobe();
	disable_C2CK();
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


void do_reset() {
	reset();
	Serial.println("OK");
}


void do_halt() {
	halt();
	Serial.println("OK");
}


void do_addr_write(const char *cmd) {
	u8 addr = (hex2num(cmd[3]) << 4) + hex2num(cmd[4]);
	bool res = addr_write(addr);
	Serial.println(res ? "OK" : "ERR");
}


void do_addr_read() {
	u8 addr;
	bool res = addr_read(&addr);
	if (res) {
		char tmp[0x10];
		snprintf(tmp, sizeof(tmp), "OK %02X", addr);
		Serial.println(tmp);
	} else
		Serial.println("ERR");
}


void do_data_write(const char *cmd) {
	u8 data = (hex2num(cmd[3]) << 4) + hex2num(cmd[4]);
	bool res = data_write(data);
	Serial.println(res ? "OK" : "ERR");
}


void do_data_read() {
	u8 data;
	bool res = data_read(&data);
	if (res) {
		char tmp[0x10];
		snprintf(tmp, sizeof(tmp), "OK %02X", data);
		Serial.println(tmp);
	} else
		Serial.println("ERR");
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


void do_set_trig(const char *cmd) {
	g_trig_counter = hex2num(cmd[4]);
	Serial.println("OK");
}


void do_hack() {
	// Don't trust the name
	// Just a custom command when you need to do something time-dependent
	g_disable_interrupts = 0;
	g_trig_counter = 0;
	noInterrupts();

	reset();
	addr_write(C2_FPCTL);
	data_write(0x02);
	data_write(0x04);
	digitalWrite(PIN_TRIG, HIGH);
	data_write(0x01);
	digitalWrite(PIN_TRIG, LOW);

	interrupts();
	g_disable_interrupts = 1;

	Serial.println("OK");
}


void exec_cmd(const char *cmd) {
	if ((cmd[0] == 'R') && (cmd[1] == 'S') && (cmd[2] == 'T')) {
		do_reset();
	} else if ((cmd[0] == 'H') && (cmd[1] == 'L') && (cmd[2] == 'T')) {
		do_halt();
	} else if ((cmd[0] == 'A') && (cmd[1] == 'W') && (cmd[2] == ' ')) {
		do_addr_write(cmd);
	} else if ((cmd[0] == 'A') && (cmd[1] == 'R')) {
		do_addr_read();
	} else if ((cmd[0] == 'D') && (cmd[1] == 'W') && (cmd[2] == ' ')) {
		do_data_write(cmd);
	} else if ((cmd[0] == 'D') && (cmd[1] == 'R')) {
		do_data_read();
	} else if ((cmd[0] == 'T') && (cmd[1] == 'R') && (cmd[2] == 'G') && (cmd[3] == ' ')) {
		do_set_trig(cmd);
	} else if ((cmd[0] == 'H') && (cmd[1] == 'A') && (cmd[2] == 'C') && (cmd[3] == 'K')) {
		do_hack();
	} else {
		Serial.println("Unknown cmd");
	}
}


void loop() {
	// RST
	// HLT
	// AW AA
	// AR
	// DW DD
	// DR
	// TRG N
	// HACK
	char cmd_buf[6];

	while (Serial.available() > 0) {
		int n = Serial.readBytes(cmd_buf, sizeof(cmd_buf));

		if ((n == sizeof(cmd_buf)) && (cmd_buf[sizeof(cmd_buf)-1] == '\n')) {
			exec_cmd(cmd_buf);
		} else
			Serial.println("Wrong cmd format");
	}
}
