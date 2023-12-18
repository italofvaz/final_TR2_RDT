import argparse
import RDT


def send_message(rdt, message):
    # Divide a mensagem em pacotes e envia cada um
    for i in range(0, len(message), rdt.window_size):
        packet_data = message[i:i+rdt.window_size]
        rdt.rdt_4_0_send(packet_data)

    # Recebe a resposta completa
    response = ""
    while True:
        part = rdt.rdt_4_0_receive()
        if part:
            response += part
        else:
            break
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quotation client talking to a Pig Latin server.')
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    msg_L = [
        'The art of debugging is figuring out what you really told your program to do rather than what you thought you told it to do. -- Andrew Singer', 
        'The good news about computers is that they do what you tell them to do. The bad news is that they do what you tell them to do. -- Ted Nelson', 
        'It is hardware that makes a machine fast. It is software that makes a fast machine slow. -- Craig Bruce',
        'The art of debugging is figuring out what you really told your program to do rather than what you thought you told it to do. -- Andrew Singer',
        'The computer was born to solve problems that did not exist before. - Bill Gates'
    ]

    rdt = RDT.RDT('client', args.server, args.port)
    try:
        for msg_S in msg_L:
            print('Client sending: ' + msg_S)
            response = send_message(rdt, msg_S)
            print('Client received: ' + response + '\n')
    except (KeyboardInterrupt, SystemExit):
        print("Ending connection...")
    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        print("Ending connection...")
    finally:
        rdt.disconnect()
        print("Connection ended.")
