import Network
import argparse
import time
from time import sleep
import hashlib

debug = True
# default = False


def debug_log(message):
    if debug:
        print(message)


class Packet:
    seq_num_S_length = 10
    length_S_length = 10
    checksum_length = 32

    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S

    @classmethod
    def from_byte_S(cls, byte_S):
        if cls.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')

        # extract the fields
        seq_num = int(byte_S[cls.length_S_length: cls.length_S_length + cls.seq_num_S_length])
        msg_S = byte_S[cls.length_S_length + cls.seq_num_S_length + cls.checksum_length:]
        return cls(seq_num, msg_S)

    def get_byte_S(self):
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(
            self.length_S_length)
        checksum = hashlib.md5((length_S + seq_num_S + self.msg_S).encode('utf-8')).hexdigest()
        return length_S + seq_num_S + checksum + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        # extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length: Packet.seq_num_S_length + Packet.seq_num_S_length]
        checksum_S = byte_S[
                     Packet.seq_num_S_length + Packet.seq_num_S_length: Packet.seq_num_S_length + Packet.length_S_length + Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length + Packet.seq_num_S_length + Packet.checksum_length:]

        checksum = hashlib.md5((length_S + seq_num_S + msg_S).encode('utf-8')).hexdigest()
        return checksum_S != checksum

    def is_ack_pack(self):
        return self.msg_S in ['ACK', 'NAK']


class RDT:
    seq_num = 0
    byte_buffer = ''
    timeout = 3

    def __init__(self, role_S, server_S, port, window_size=4):
        self.network = Network.NetworkLayer(role_S, server_S, port)
        self.window_size = window_size  # Definindo o tamanho da janela para Go-Back-N

    def disconnect(self):
        self.network.disconnect()

    def rdt_4_0_send(self, msg_S):
        window = []
        base = self.seq_num
        next_seq_num = self.seq_num
        window_size = self.window_size

        # Enviar todos os pacotes da mensagem
        while base < len(msg_S):
            while next_seq_num < base + window_size and next_seq_num < len(msg_S):
                packet_data = msg_S[next_seq_num - base] if next_seq_num - base < len(msg_S) else ''
                packet = Packet(next_seq_num, packet_data)
                self.network.udt_send(packet.get_byte_S())
                window.append(packet)
                next_seq_num += 1

            # Verificar ACKs
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                response = self.network.udt_receive()
                if response:
                    ack_packet = Packet.from_byte_S(response)
                    if not Packet.corrupt(response) and ack_packet.msg_S == "ACK":
                        # Mover a base da janela para o próximo pacote não reconhecido
                        base = ack_packet.seq_num + 1
                        window = [pkt for pkt in window if pkt.seq_num >= base]
                        break

            # Retransmitir pacotes se o temporizador expirar
            if time.time() - start_time >= self.timeout:
                for packet in window:
                    self.network.udt_send(packet.get_byte_S())
                start_time = time.time()  # Reiniciar o temporizador

            if base >= len(msg_S):
                break  # Terminar se todos os pacotes forem reconhecidos

    def rdt_4_0_receive(self):
        ret_S = None
        while True:
            byte_S = self.network.udt_receive()
            if not byte_S:
                break  # Sair do loop se não houver mais dados para receber

            self.byte_buffer += byte_S

            # Continuar extraindo pacotes enquanto houver dados disponíveis
            while len(self.byte_buffer) >= Packet.length_S_length:
                length = int(self.byte_buffer[:Packet.length_S_length])
                if len(self.byte_buffer) < length:
                    break  # Não tem bytes suficientes para ler o pacote inteiro

                packet = self.byte_buffer[:length]
                self.byte_buffer = self.byte_buffer[length:]

                if Packet.corrupt(packet):
                    debug_log("RECEIVER: Corrupt packet, ignoring.")
                    continue  # Ignorar pacotes corrompidos

                p = Packet.from_byte_S(packet)
                if p.seq_num == self.seq_num:
                    debug_log('RECEIVER: Received expected packet.')
                    ret_S = p.msg_S if ret_S is None else ret_S + p.msg_S
                    ack_packet = Packet(self.seq_num, "ACK")
                    self.network.udt_send(ack_packet.get_byte_S())
                    self.seq_num += 1
                else:
                    debug_log('RECEIVER: Out-of-order packet received, ignoring.')

        return ret_S  # Retorna a mensagem acumulada após processar todos os pacotes



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_4_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_4_0_receive())
        rdt.disconnect()
    else:
        sleep(1)
        print(rdt.rdt_4_0_receive())
        rdt.rdt_4_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
