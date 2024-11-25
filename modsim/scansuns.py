"""
Scan SunSpec device and make mbmap xml file

Made by Jake Lee (leejaku@gmail.com)
"""
import sys
from optparse import OptionParser
import logging
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
from modbus_tk.exceptions import ModbusError

# log = modbus_tk.utils.create_logger("console")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)  # 로그 레벨 설정
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 콘솔 출력 핸들러의 레벨 설정

# 포매터 설정
formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(formatter)
log.addHandler(console_handler)


class SunsScanner:
    def __init__(self, opts):
        self.options = opts

    def scan(self):
        if self.options.mode == 'tcp':
            self.scan_tcp()
        else:
            log.warning("Only tcp mode is implemented")
            return

    def scan_tcp(self):
        try:
            log.info(f"Connect to {self.options.ip}:{self.options.port}")
            master = modbus_tcp.TcpMaster(host=self.options.ip, port=self.options.port, timeout_in_sec=3.0)
            # master.open()
            log.info("connected")

            start: int = self.find_sunspec_start(master)
            if start < 0:
                return
            self.scan_sunspec(master, start+2)
        except Exception as e:
            log.error(e)

    def find_sunspec_start(self, master):
        # check "SunS"
        result = master.execute(self.options.addr, cst.READ_HOLDING_REGISTERS, 40000, 2)
        if self.is_sunspec_start(result):
            log.info("SunSpec start in 40000")
            return 40000

        result = master.execute(self.options.addr, cst.READ_HOLDING_REGISTERS, 50000, 2)
        if self.is_sunspec_start(result):
            log.info("SunSpec start in 50000")
            return 50000

        result = master.execute(self.options.addr, cst.READ_HOLDING_REGISTERS, 0, 2)
        if self.is_sunspec_start(result):
            log.info("SunSpec start in 0")
            return 0

        log.error("SunSpec start cannot be found")
        return -1

    @staticmethod
    def is_sunspec_start(data):
        return data[0] == 21365 and data[1] == 28243

    def scan_sunspec(self, master, start):
        while True:
            result = master.execute(self.options.addr, cst.READ_HOLDING_REGISTERS, start, 2)
            model = result[0]
            length = result[1]
            log.info(f"- Model: {model}, Len: {length}")
            if model == 65535:
                break
            start += result[1]+2


if __name__ == "__main__":
    usage = 'usage: %prog [options] map_file'
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--serial',
                      default='COM1',
                      help='Serial port [default: COM1]')
    parser.add_option('-b', '--baud',
                      default=9600,
                      help='Baud Rate [default: 9600]')
    parser.add_option('-m', '--mode',
                      default='tcp',
                      help='mode: rtu, tcp [default: tcp]')
    parser.add_option('-i', '--ip',
                      default='127.0.0.1',
                      help='Ip Address: xxx.xxx.xxx.xxx [default: 127.0.0.1]')
    parser.add_option('-p', '--port', type='int',
                      default=502,
                      help='IP port [default: 502]')
    parser.add_option('-a', '--addr', type='int',
                      default=1,
                      help='slave addr [default: 1]')
    parser.add_option('-v', '--verbose', type='int',
                      default=0,
                      help='verbose: 0 or 1 [default: 0]')

    options, args = parser.parse_args()

    if len(args) != 1:
        print(parser.print_help())
        sys.exit(1)

    scanner = SunsScanner(options)
    scanner.scan()
