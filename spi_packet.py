import csv
import sys

# Update the constants below to fit your trace's column titles.
MOSI = " MOSI"
MISO = " MISO"
SCK = " Clock"
CS = " CS"
TIME = "Time[s]"

# Change the constants below to reflect the command structure of your SPI
# protocol. The definitions below are for the S25FL216K flash memory. Its
# datasheet is here: http://www.cypress.com/file/197346/download
# They are only used in print_packet though so you can skip them entirely if you
# want to do it all yourself.
COMMANDS = {
  0x06: "WRITE_ENABLE",
  0x04: "WRITE_DISABLE",
  0x05: "READ_STATUS_REGISTER",
  0x01: "WRITE_STATUS_REGISTER",
  0x03: "READ_DATA",
  0x0B: "FAST_READ",
  0x3B: "FAST_READ_DUAL",
  0x02: "PAGE_PROGRAM",
  0xD8: "BLOCK_ERASE",
  0x20: "SECTOR_ERASE",
  0xC7: "CHIP_ERASE",
  0x60: "CHIP_ERASE",
  0xB9: "POWER_DOWN",
  0xAB: "DEVICE_ID",
  0x90: "MANUFACTURER_ID",
  0x9F: "JEDEC_ID"
}

IGNORE_COMMANDS = [
  "READ_STATUS_REGISTER",
  "WRITE_ENABLE"
]

# Change this method to change the print out of every packet.
def print_packet(packet):
  if not packet:
    return
  command = COMMANDS[packet["MOSI"][0]]
  if command in IGNORE_COMMANDS:
    return
  command = command.ljust(len("READ_STATUS_REGISTER"))
  print(packet["time"],
        command,
        "Master", " ".join(['%02x'%x for x in packet["MOSI"][:8]]),
        "Slave", " ".join(['%02x'%x for x in packet["MISO"][:8]]),
        packet["bits"], "total bits")

# The code below is agnostic to the protocol being implemented over SPI. Its
# only mode 0 though. So if yours is a different mode then you'll need to update
# it.
with open(sys.argv[1], "r") as f:
  reader = csv.DictReader(f)
  i = 0
  packet = {}
  last_clock = 1
  for row in reader:
    # Uncomment this if you want to just print the start.
    # if i > 700:
    #   break
    # Uncomment this to see every raw row interlaced with packet output.
    #print("\t" + str(row))
    cs = int(row[CS])
    clock = int(row[SCK])
    if cs == 0:
      if not packet:
        packet["time"] = row[TIME].strip()
        packet["MOSI"] = []
        packet["MISO"] = []
        packet["bits"] = 0
      if clock == 1 and last_clock == 0:
        mosi_bit = int(row[MOSI].strip())
        miso_bit = int(row[MISO].strip())
        if packet["bits"] % 8 == 0:
          packet["MOSI"].append(mosi_bit)
          packet["MISO"].append(miso_bit)
        else:
          packet["MOSI"][-1] = 2 * packet["MOSI"][-1] + mosi_bit
          packet["MISO"][-1] = 2 * packet["MISO"][-1] + miso_bit
        packet["bits"] += 1
    elif cs == 1:
      if packet and packet["MOSI"]:
        print_packet(packet)
      packet = {}
    last_clock = clock
    i += 1
  print_packet(packet)
