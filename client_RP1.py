import camNozzle
import numpy as np
import socket
import select
import errno
import sys
import time
import pickle


def test_client_func(username, HEADER_LENGTH, IP, PORT):
    #my_username = input("Username: ")
    my_username = username
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    username = my_username.encode("utf-8")
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(username_header + username)


    #Esperar por uma mensage com o processo
    while True:
        
        try:
            while True:
                #receive things
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("connection closed by the server")
                    sys.exit()

                username_length = int(username_header.decode("utf-8").strip())
                username = client_socket.recv(username_length).decode("utf-8")

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode("utf-8").strip())
                message = client_socket.recv(message_length).decode("utf-8")

                if message == f"Proc1":
                    #Enviar instruções para o raspberry processar
                    d, _, _, _, _, _ = camNozzle.movePrintCore(20, 'test.mp4')
                    #d = np.asarray([1, 2])
                    m_pickle = pickle.dumps(d)

                    time.sleep(5)
                    m_pickle_header = f"{len(m_pickle) :< {HEADER_LENGTH}}".encode("utf-8")
                    client_socket.send(m_pickle_header + m_pickle)

                elif message == f"Proc2":
                    #Receive parameter A
                    while True:
                        try:
                            username_header = client_socket.recv(HEADER_LENGTH)
                            if not len(username_header):
                                print("connection closed by the server")
                                sys.exit()

                            username_length = int(username_header.decode("utf-8").strip())
                            username = client_socket.recv(username_length).decode("utf-8")

                            message_header = client_socket.recv(HEADER_LENGTH)
                            message_length = int(message_header.decode("utf-8").strip())
                            message = client_socket.recv(message_length).decode("utf-8")
                            if message:
                                A = float(message)
                                if A:
                                    break
                        except IOError as e:
                            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                                print('Reading error', str(e))
                                sys.exit()
                            continue

                        
                        except Exception as e:
                            print('General error', str(e))
                            sys.exit()
                            pass


                    #D = camNozzle.steps_mm_cal_xx(A, 20)
                    #Send D to RP
                    D = input(" > Insira o parametro D")
                    message = f"{D}"
                    message = message.encode("utf-8")
                    message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                    client_socket.send(message_header + message)
          

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error', str(e))
                sys.exit()
            continue

        
        except Exception as e:
            print('General error', str(e))
            sys.exit()
            pass
    return message_received

def main():
    username = "RP1"
    HEADER_LENGTH = 10
    IP = '10.16.232.157'
    PORT = 1234
    message = test_client_func(username, HEADER_LENGTH, IP, PORT)
    print(message)

if __name__ == "__main__":
    main()
