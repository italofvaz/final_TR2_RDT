import argparse
import RDT
import time


def upperCase(message):
    capitalizedSentence = message.upper()
    return capitalizedSentence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UPPER CASE server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    timeout = 5000  # close connection if no new data within 5 seconds
    time_of_last_data = time.time()

    rdt = RDT.RDT('server', None, args.port)
    try:
        while True:
            full_msg = ''
            while True:
                msg_part = rdt.rdt_4_0_receive()
                if msg_part:
                    full_msg += msg_part
                    time_of_last_data = time.time()
                if time.time() - time_of_last_data > timeout:
                    break

            if full_msg:
                rep_msg_S = upperCase(full_msg)
                print(f'Server: converted {full_msg} to {rep_msg_S}')
                rdt.rdt_4_0_send(rep_msg_S)
            else:
                # Exit the loop if no data is received for the duration of the timeout
                break

    except (KeyboardInterrupt, SystemExit):
        print("Ending connection...")
    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        print("Ending connection...")
    finally:
        rdt.disconnect()
        print("Connection ended.")
