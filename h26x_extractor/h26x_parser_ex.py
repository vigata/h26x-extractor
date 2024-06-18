import argparse
import sys
from h26x_extractor.h26x_parser import H26xParser

# def do_something(bytes):
#     pass
#     # do something with the NALU bytes

# H26xParser.set_callback("nalu", do_something)
# H26xParser.parse()

''' expanded command line for h26x_parser.py
    Does not read the file as a whole, but reads it in chunks

'''

def parse_args():
    parser = argparse.ArgumentParser(description="Parse h26x streams")
    parser.add_argument("-v","--verbose", action="store_true", default=False, help="Set verbose")
    parser.add_argument("input_file",  help="Input file(s)")
    return parser.parse_args(), parser


def main():
    args, parser = parse_args()
    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    def find_start_codes(data):
        start_positions = []
        """
        Generator to find start codes and yield their positions in the data.
        Start codes are either 0x000001 or 0x00000001.
        """
        i = 0
        while i < len(data) - 3:
            if data[i] == 0x00 and data[i + 1] == 0x00:
                if data[i + 2] == 0x01:
                    start_positions.append(i)
                    i += 3
                elif i < len(data) - 4 and data[i + 2] == 0x00 and data[i + 3] == 0x01:
                    start_positions.append(i) 
                    i += 4
                else:
                    i += 2
            else:
                i += 1
        return start_positions

    def extract_nal_units_from_file(file_path):
        """
        Extract NAL units from a file containing RBSP data and handle data across buffer boundaries.
        """
        buffer_size = 4096
        nal_units = []
        pending_data = b''

        parser = H26xParser(None, True, byte_stream=None)
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(buffer_size)
                if not data:
                    break
                # Prepend pending data from previous buffer read
                data = pending_data + data

                # Find start codes in the current buffer
                start_positions = find_start_codes(data)

                # Check if we should preserve some data for the next buffer
                if start_positions:
                    last_start = start_positions[-1]
                    pending_data = data[last_start:]
                    data = data[:last_start]
                else:
                    pending_data = data
                    continue

                # Extract NAL units from this buffer slice
                for i in range(len(start_positions) - 1):
                    start = start_positions[i]
                    end = start_positions[i + 1]
                    nal_units.append(data[start:end])
                    parser.parse(byte_stream=data[start:end])

            # Handle the last NAL unit
            if pending_data:
                last_positions = find_start_codes(pending_data)
                if last_positions:
                    for i in range(len(last_positions) - 1):
                        start = last_positions[i]
                        end = last_positions[i + 1]
                        nal_units.append(pending_data[start:end])
                    # Append the last fragment
                    nal_units.append(pending_data[last_positions[-1]:])

        return nal_units

    # Example usage
    nal_units = extract_nal_units_from_file(args.input_file)

    # for idx, nal in enumerate(nal_units):
    #     print(f"NAL Unit {idx + 1}: {nal.hex()}")







