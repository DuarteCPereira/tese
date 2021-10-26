import camNozzle
import numpy as np
import socket
import select
import errno
import sys
import time
import pickle
import videoRecord
import detectMarker
import vidProc

from videoRecord import recordVid
#12

def receive_message(HEADER_LENGTH, client_socket):
    a = True
    while a:
        try:
            while a:
                #receive things
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("connection closed by the server")
                    sys.exit()

                username_length = int(username_header.decode("utf-8").strip())
                username = client_socket.recv(username_length).decode("utf-8")

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode("utf-8").strip())
                #message = client_socket.recv(message_length).decode("utf-8")
                message = client_socket.recv(message_length)

                d = pickle.loads(message)
                a = False


        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error', str(e))
                sys.exit()
            continue
        
        except Exception as e:
            print('General error', str(e))
            sys.exit()
            pass
    
    return d

def send_message(HEADER_LENGTH, message, client_socket):

    message_pickle = pickle.dumps(message)
    #message = message.encode("utf-8")
    message_header = f"{len(message_pickle) :< {HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(message_header+message_pickle)

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
        proc = receive_message(HEADER_LENGTH, client_socket)
        if proc == f"Proc1_2":
            #Enviar instruções para o raspberry processar
            d, _, _, _, _, _, _ = camNozzle.movePrintCore(20, 'test.mp4')
            #d = np.asarray([1, 2])
            '''
            m_pickle = pickle.dumps(d)

            time.sleep(2)
            m_pickle_header = f"{len(m_pickle) :< {HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(m_pickle_header + m_pickle)'''
            send_message(HEADER_LENGTH, d, client_socket)
            
        if proc == f"Proc2_2":
            A = receive_message(HEADER_LENGTH, client_socket)
            D = camNozzle.steps_mm_cal_xx(A, 20, 'test.mp4')
            #Send D to RP
            #D = input(" > Insira o parametro D")                                       
            send_message(HEADER_LENGTH, message, client_socket)
            
        if proc == f"Proc3_2":
            A = receive_message(HEADER_LENGTH, client_socket)
            D = camNozzle.steps_mm_cal_yy(A, 20, 'test.mp4')
            #Send D to RP
            #D = input(" > Insira o parametro D")
            message = D
            send_message(HEADER_LENGTH, message, client_socket)
        
        if proc == f"Proc4_2":
            a = True
            b = False
            #Enviar instruções para o raspberry processar
            while a:
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
            message = skew_angle
            send_message(HEADER_LENGTH, message, client_socket)
        if proc == "teste":
            a = True
            b = True
            c = True
            while a:
                #Enviar instruções para o raspberry processar
                dx, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test10.mp4')
                print(dx)
                #d = np.asarray([1, 2])
                print(sidePx, "sidePx para o mov em xx")
                a = False
            while b:
                #Enviar instruções para o raspberry processar
                dy, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test01.mp4')
                print(dy)
                print(sidePx, "sidePx para o mov em yy")
                b = False

            #Saber a quantos pixeis corresponde o movimento de 1mm em ambas as direções (xx e yy) 
            dpx_mm = camNozzle.MmToPx(dx, dy, sidePx, celLen)
            
            while c:
                #Perguntar ao utilizador se a camera já se encontra em cima do QR
                input("Pressione um tecla para continuar.")
                #Enviar instruções para o raspberry detetar o qr code
                videoRecord.recordPic("MarkerDistance.png")


                d_xy_px = detectMarker.detectMark("MarkerDistance.png", "DICT_5X5_100")
                #Converter a distância em pixeis para mm
                d_xy_mm = np.matmul(np.linalg.inv(dpx_mm), np.array(d_xy_px))
                d_xy_mm[0] = -d_xy_mm[0]
                print(d_xy_mm)
                
                if abs(d_xy_mm[0]) <= 0.1 and abs(d_xy_mm[1]) <= 0.1:
                    d_xy_mm[0] = 0
                    d_xy_mm[1] = 0
                    c = False

                #Recolher distẫncia em px para o qr code
                #Enviar para o pc a nova instrução a dar em mm
                print(1)
                send_message(HEADER_LENGTH, d_xy_mm, client_socket)

        if proc == "testeNozzle":
            a = True
            b = True
            c = True
            while a:
                #Enviar instruções para o raspberry processar
                dx, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test10.mp4')
                print(dx)
                #d = np.asarray([1, 2])
                print(sidePx, "sidePx para o mov em xx")
                a = False
            while b:
                #Enviar instruções para o raspberry processar
                dy, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test01.mp4')
                print(dy)
                print(sidePx, "sidePx para o mov em yy")
                b = False

            #Saber a quantos pixeis corresponde o movimento de 1mm em ambas as direções (xx e yy) 
            dpx_mm = camNozzle.MmToPx(dx, dy, sidePx, celLen)
            
            while c:
                #Perguntar ao utilizador se a camera já se encontra em cima do QR
                input("Pressione um tecla para continuar.")
                #Enviar instruções para o raspberry detetar o qr code
                videoRecord.recordPic("circle.png")


                d_xy_px = vidProc.findCircles("circle.png")
                #Converter a distância em pixeis para mm
                d_xy_mm = np.matmul(np.linalg.inv(dpx_mm), np.array(d_xy_px))
                d_xy_mm[0] = -d_xy_mm[0]
                print(d_xy_mm)
                
                if abs(d_xy_mm[0]) <= 0.1 and abs(d_xy_mm[1]) <= 0.1:
                    d_xy_mm[0] = 0
                    d_xy_mm[1] = 0
                    c = False

                #Recolher distẫncia em px para o qr code
                #Enviar para o pc a nova instrução a dar em mm
                print(1)
                send_message(HEADER_LENGTH, d_xy_mm, client_socket)
    '''
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
                    c = True
                    d = True
                    while a:
                        #Enviar instruções para o raspberry processar
                        dx, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test10.mp4')
                        print(dx)
                        #d = np.asarray([1, 2])
                        print(sidePx, "sidePx para o mov em xx")
                        a = False
                    
                    while b:
                        #Enviar instruções para o raspberry processar
                        dy, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test01.mp4')
                        print(dy)
                        print(sidePx, "sidePx para o mov em yy")
                        b = False
                    
                    #Saber a quantos pixeis corresponde o movimento de 1mm em ambas as direções (xx e yy) 
                    dpx_mm = camNozzle.MmToPx(dx, dy, sidePx, celLen)
                    
                    while c:

                        #Perguntar ao utilizador se a camera já se encontra em cima do QR
                        input("Pressione um tecla para continuar.")
                        #Enviar instruções para o raspberry detetar o qr code
                        videoRecord.recordPic("MarkerDistance.png")


                        d_xy_px = detectMarker.detectMark("MarkerDistance.png", "DICT_5X5_100")
                        #Converter a distância em pixeis para mm
                        d_xy_mm = np.matmul(np.linalg.inv(dpx_mm), np.array(d_xy_px))
                        d_xy_mm[0] = -d_xy_mm[0]
                        print(d_xy_mm)
                        
                        if abs(d_xy_mm[0]) <= 0.1 and abs(d_xy_mm[1]) <= 0.1:
                            d_xy_mm[0] = 0
                            d_xy_mm[1] = 0
                            c = False


                        #Recolher distẫncia em px para o qr code
                        #Enviar para o pc a nova instrução a dar em mm
                        
                        m_pickle = pickle.dumps(d_xy_mm)
                        time.sleep(0.5)
                        m_pickle_header = f"{len(m_pickle) :< {HEADER_LENGTH}}".encode("utf-8")
                        client_socket.send(m_pickle_header + m_pickle)

                if message == "testeNozzle":
                    a = True
                    b = True
                    c = True
                    d = True
                    while a:
                        #Enviar instruções para o raspberry processar
                        dx, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test10.mp4')
                        print(dx)
                        #d = np.asarray([1, 2])
                        print(sidePx, "sidePx para o mov em xx")
                        a = False
                    
                    while b:
                        #Enviar instruções para o raspberry processar
                        dy, _, _, _, _, _, sidePx = camNozzle.movePrintCore(5, 'test01.mp4')
                        print(dy)
                        print(sidePx, "sidePx para o mov em yy")
                        b = False
                    
                    #Saber a quantos pixeis corresponde o movimento de 1mm em ambas as direções (xx e yy) 
                    dpx_mm = camNozzle.MmToPx(dx, dy, sidePx, celLen)
                    
                    while c:

                        #Perguntar ao utilizador se a camera já se encontra em cima do QR
                        input("Pressione um tecla para continuar.")
                        #Enviar instruções para o raspberry detetar o qr code
                        videoRecord.recordPic("NozzleCam.png")


                        NozzleCam = vidProc.findCircles("MarkerDistance.png", "DICT_5X5_100")
                        #Converter a distância em pixeis para mm
                        NozzleCam = np.matmul(np.linalg.inv(dpx_mm), np.array(d_xy_px))
                        NozzleCam[0] = -NozzleCam[0]
                        print(NozzleCam)
                        
                        if abs(NozzleCam[0]) <= 0.1 and abs(NozzleCam[1]) <= 0.1:
                            NozzleCam[0] = 0
                            NozzleCam[1] = 0
                            c = False


                        #Recolher distẫncia em px para o qr code
                        #Enviar para o pc a nova instrução a dar em mm
                        
                        m_pickle = pickle.dumps(NozzleCam)
                        time.sleep(0.5)
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
    '''

def main():
    username = "RP2"
    HEADER_LENGTH = 10
    IP = '10.16.233.124'
    PORT = 1234
    message = test_client_func(username, HEADER_LENGTH, IP, PORT)
    print(message)

if __name__ == "__main__":
    main()
