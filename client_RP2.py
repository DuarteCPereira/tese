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
    celLen = 2

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

                if message == f"Proc1_2":
                    #Enviar instruções para o raspberry processar
                    d, _, _, _, _, _, _ = camNozzle.movePrintCore(20, 'test.mp4')
                    #d = np.asarray([1, 2])
                    m_pickle = pickle.dumps(d)

                    time.sleep(2)
                    m_pickle_header = f"{len(m_pickle) :< {HEADER_LENGTH}}".encode("utf-8")
                    client_socket.send(m_pickle_header + m_pickle)

                elif message == f"Proc2_2":
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


                    D = camNozzle.steps_mm_cal_xx(A, 20, 'test.mp4')
                    #Send D to RP
                    #D = input(" > Insira o parametro D")
                    message = f"{D}"
                    message = message.encode("utf-8")
                    message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                    client_socket.send(message_header + message)
                    
                elif message == f"Proc3_2":
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


                    D = camNozzle.steps_mm_cal_xx(A, 20, 'test.mp4')
                    #Send D to RP
                    #D = input(" > Insira o parametro D")
                    message = f"{D}"
                    message = message.encode("utf-8")
                    message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                    client_socket.send(message_header + message)

                if message == f"Proc4_2":
                    a = True
                    b = True
                    while a:
                        #Enviar instruções para o raspberry processar
                        dx, _, _, _, _, _, _ = camNozzle.movePrintCore(20, 'test.mp4')
                        print(dx)
                        #d = np.asarray([1, 2])
                        a = False
                    
                    while b:
                        #Enviar instruções para o raspberry processar
                        dy, _, _, _, _, _, _ = camNozzle.movePrintCore(20, 'test.mp4')
                        print(dy)
                        b = False
                    
                    skew_angle, _, _ = camNozzle.getSkewCoefxy(dx, dy)

                    message = f"{skew_angle}"
                    message = message.encode("utf-8")
                    message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                    client_socket.send(message_header + message)
                    
                if message == "teste":
                    a = True
                    b = True
                    while a:
                        #Enviar instruções para o raspberry processar
                        dx, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test.mp4')
                        print(dx)
                        #d = np.asarray([1, 2])
                        print(sidePx, "sidePx para o mov em xx")
                        a = False
                    
                    while b:
                        #Enviar instruções para o raspberry processar
                        dy, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test.mp4')
                        print(dy)
                        print(sidePx, "sidePx para o mov em yy")
                        b = False
                    
                    #Saber a quantos pixeis corresponde o movimento de 1mm em ambas as direções (xx e yy) 
                    dpx_mm = camNozzle.MmToPx(dx, dy, sidePx, celLen)

                    #Enviar instruções para o raspberry detetar o qr code
                    #detectmarker
                    
                    #Recolher distẫncia em px para o qr code
                    #Enviar para o pc a nova instrução a dar em mm
                    
                    m_pickle = pickle.dumps(d)
                    time.sleep(2)
                    m_pickle_header = f"{len(m_pickle) :< {HEADER_LENGTH}}".encode("utf-8")
                    client_socket.send(m_pickle_header + m_pickle)
                
          

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
    username = "RP2"
    HEADER_LENGTH = 10
    IP = '10.16.232.63'
    PORT = 1234
    message = test_client_func(username, HEADER_LENGTH, IP, PORT)
    print(message)

if __name__ == "__main__":
    main()