from printers import Printer
from modules import Head
import socket
import select
import errno
import sys
import time
import pickle
import numpy as np

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

def give_instruction(string, head_number):
    if head_number == 1:
        h2.add_instruction_to_queue(string+"\n")
        h2.send_next_instruction(show=True)
        message = h2.read_serial_message(show=True)
        while True:
            if "ok" in message:
                break
            else:
                time.sleep(0.1)
                message = h2.read_serial_message(show=True)
    if head_number == 2:
        h1.add_instruction_to_queue(string+"\n")
        h1.send_next_instruction(show=True)
        message = h1.read_serial_message(show=True)
        while True:
            if "ok" in message:
                break
            else:
                time.sleep(0.1)
                message = h1.read_serial_message(show=True)
    return None

def return_steps_x(head_number):
    if head_number == 1:
        h2.add_instruction_to_queue("M92")
        h2.send_next_instruction(show=True)
        while True:
            message = h2.read_serial_message(show=True)
            if "M92" in message:
                index_x = message.find("X")
                steps_x = float(message[index_x+1:index_x+7])
                print(steps_x)
            elif "ok" in message:
                break
    if head_number == 2:
        h1.add_instruction_to_queue("M92")
        h1.send_next_instruction(show=True)
        while True:
            message = h1.read_serial_message(show=True)
            if "M92" in message:
                index_x = message.find("X")
                steps_x = float(message[index_x+1:index_x+7])
                print(steps_x)
            elif "ok" in message:
                break
    print(message)
    return steps_x

def return_steps_y(head_number):
    if head_number == 1:
        h2.add_instruction_to_queue("M92")
        h2.send_next_instruction(show=True)
        while True:
            message = h2.read_serial_message(show=True)
            if "M92" in message:
                index_y = message.find("Y")
                steps_y = float(message[index_y+1:index_y+7])
                print(steps_y)
            elif "ok" in message:
                break
        print(message)
    if head_number == 2:
        h1.add_instruction_to_queue("M92")
        h1.send_next_instruction(show=True)
        while True:
            message = h1.read_serial_message(show=True)
            if "M92" in message:
                index_y = message.find("Y")
                steps_y = float(message[index_y+1:index_y+7])
                print(steps_y)
            elif "ok" in message:
                break
        print(message)
    return steps_y

def test_client_func(username, HEADER_LENGTH, IP, PORT):
    #my_username = input("Username: ")
    my_username = username
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    username = my_username.encode("utf-8")
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(username_header + username)
    b =True


    while True:
        a = True
        b = True
        c = True
        #h2.flush_start_messages(show=False)
        message = h2.read_serial_message(show=True)
        print(f"Choose a calibration option paired with '_headNumber':")
        print(f"1 - Measure distance.")
        print(f"2 - Calibrate steps/mm on xx direction.")
        print(f"3 - Calibrate steps/mm on yy direction.")
        print(f"4 - Apply skew compensation.")
        print(f"teste_relativo - Teste da calibra????o relativa.")
        print(f"teste_relativo_1 - Teste da calibra????o relativa.")
        print(f"testeNozzle - Encontrar o vector nozzle-camera.")
        process = input(f"{my_username} > ")

        #Processar as a????es necess??rias para cada processo
        """Cabe??a 2"""
        #Medir dist??ncia
        if process == "1_RP1":
            message = f"Proc1_1"
            send_message(HEADER_LENGTH, message, client_socket)
            #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
            give_instruction("G91", 1)
            time.sleep(3)

            give_instruction("G0 X10 F100", 1)

            d = receive_message(HEADER_LENGTH, client_socket)
            #d = pickle.loads(message)
            print(f"{username} > {d}")
            print(f"O vector recebido foi: {d} ")


        #Calibrar E-Steps
        if process == "2_RP1":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503
            while a:
                b = True
                message = f"Proc2_1"
                send_message(HEADER_LENGTH, message, client_socket)
                time.sleep(1)

                #Send A to RP
                A = return_steps_x(1)
                message = A
                send_message(HEADER_LENGTH, message, client_socket)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 X10 F100", 1)

                while b:
                    D = receive_message(HEADER_LENGTH, client_socket)
                    if abs(D - A) == 0:
                        a = False
                        b = False
                        print(D)

                    elif abs(D - A) > 0:
                        print("Parametro nao esta afinado")
                        print("Novo parametro ser?? atualizado")
                        give_instruction(f"M92 X{D}", 1)
                        give_instruction(f"M500", 1)
                        give_instruction(f"M501", 1)
                        b = False

        #Calibrar E-Steps
        if process == "3_RP1":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503
            while a:
                b = True
                message = f"Proc3_1"
                send_message(HEADER_LENGTH, message, client_socket)
                time.sleep(1)

                #Send A to RP
                A = return_steps_y(1)
                message = A
                send_message(HEADER_LENGTH, message, client_socket)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 Y10 F100", 1)

                while b:
                    D = receive_message(HEADER_LENGTH, client_socket)
                    if abs(D - A) == 0:
                        a = False
                        b = False
                        print(D)

                    elif abs(D - A) > 0:
                        print("Parametro nao esta afinado")
                        print("Novo parametro ser?? atualizado")
                        give_instruction(f"M92 Y{D}", 1)
                        give_instruction(f"M500", 1)
                        give_instruction(f"M501", 1)
                        b = False
        
        if process == "4_RP1":
            message = f"Proc_4_1"
            send_message(HEADER_LENGTH, message, client_socket)
            give_instruction("G91", 1)
            time.sleep(5)
            give_instruction("G0 X10 F100", 1)
            
            time.sleep(20)
            give_instruction("G0 Y10 F100", 1)

            #Receive Skew Angle
            skew_angle = receive_message(HEADER_LENGTH, client_socket)
            print(f"{username} > {skew_angle}")
            print(f"O ??ngulo entre os vetores deslocamento xx e yy: {skew_angle} ")

        '''
        #Medir dist??ncia
        if process == "1_RP1":
            message = f"Proc1_1"
            send_message(HEADER_LENGTH, message, client_socket)
            #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
            give_instruction("G91", 1)
            time.sleep(5)

            give_instruction("G0 X10 F100", 1)

            d = receive_message(HEADER_LENGTH, client_socket)
            d = pickle.loads(message)
            print(f"{username} > {d}")
            print(f"O vector recebido foi: {d} ")
            if message_length > 0:
                a = False

        #Calibrar E-Steps
        if process == "2_RP1":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503

            while c:
                a = True
                message = f"Proc2_1"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header+message)
                time.sleep(1)

                #Send A to RP
                A = return_steps_x(1)
                message = f"{A}"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 X10 F100", 1)


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
                            message = client_socket.recv(message_length).decode("utf-8")
                            D = float(message)


                            if abs(D - A) == 0:
                                c = False
                                a = False
                                print(D)
                                break
                            elif abs(D - A) > 0:
                                print("Parametro nao esta afinado")
                                print("Novo parametro ser?? atualizado")
                                give_instruction(f"M92 X{D}", 1)
                                give_instruction(f"M500", 1)
                                give_instruction(f"M501", 1)
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

        if process == "3_RP1":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503

            while c:
                a = True
                message = f"Proc3_1"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header+message)
                time.sleep(1)

                #Send A to RP
                A = return_steps_y(1)
                message = f"{A}"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 Y10 F100", 1)


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
                            message = client_socket.recv(message_length).decode("utf-8")
                            D = float(message)


                            if abs(D - A) < 0.5:
                                c = False
                                a = False
                                print(D)
                                break
                            elif abs(D - A) > 0.5:
                                print("Parametro nao esta afinado")
                                print("Novo parametro ser?? atualizado")
                                give_instruction(f"M92 Y{D}", 1)
                                give_instruction(f"M500", 1)
                                give_instruction(f"M501", 1)
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

        if process == "4_RP1":
            message = f"Proc4_1"
            message = message.encode("utf-8")
            message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(message_header+message)
            #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
            give_instruction("G91", 1)
            time.sleep(5)

            give_instruction("G0 X10 F100", 1)
            
            time.sleep(20)
            give_instruction("G0 Y10 F100", 1)

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

                        skew_angle = float(message)
                        #skew_angle = pickle.loads(message)
                        print(f"{username} > {skew_angle}")
                        print(f"O ??ngulo entre os vetores deslocamento xx e yy: {d} ")
                        if message_length > 0:
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
        '''

        if process == "teste_relativo":
            a = True
            c = True
            while a:
                message = f"teste"
                send_message(HEADER_LENGTH, message, client_socket)
                time.sleep(1)
                give_instruction("G90", 1)
                give_instruction("G0 X1 F100", 1)
                
                time.sleep(10)
                give_instruction("G0 Y1 F100", 1)

                #Enviar a instru????o para a cabe??a 1 se mover para a estimativa inicial
                time.sleep(9)

                initial_estimate = np.array([float(55), float(28)])
                instruction = np.copy(initial_estimate)
                give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)

                while c:
                    d = receive_message(HEADER_LENGTH, client_socket)
                    if d[0] != 0 and d[1] != 0:
                        instruction += d
                        give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)
                    else:
                        a = False
                        c = False

        if process == "teste_relativo_1":
            a = True
            c = True
            while a:
                message = f"teste_1"
                send_message(HEADER_LENGTH, message, client_socket)
                time.sleep(1)
                give_instruction("G90", 1)
                give_instruction("G0 X1 F100", 1)
                give_instruction("G90", 2)
                give_instruction("G0 X1 F100", 2)
                
                time.sleep(10)
                give_instruction("G0 Y1 F100", 1)
                give_instruction("G0 Y1 F100", 2)

                #Enviar a instru????o para a cabe??a 1 se mover para a estimativa inicial
                time.sleep(9)

                initial_estimate_1 = np.array([float(55), float(28)])
                #initial_estimate_2 = np.array([float(55), float(28)])
                instruction = np.copy(initial_estimate)
                instruction_1 = np.copy(initial_estimate_1)
                give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)


                while c:

                    d1 = receive_message(HEADER_LENGTH, client_socket)

                    if d1[0] != 0 and d1[1] != 0:
                        instruction += d1
                        give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)
                        #Adicionar instru????es para que a cabe??a 1 volte e esperar um pouco

                    else:
                        a = False
                        c = False
                #Enviar uma mensagem para o RP2 (que est?? a espera) para come??ar gravar

                give_instruction(f"G0 X{instruction_1[0]} Y{instruction_1[1]} F600",2)
                c = True
                while c:

                    d2 = receive_message(HEADER_LENGTH, client_socket)

                    if d2[0] != 0 and d2[1] != 0:
                        instruction_1 += d2
                        give_instruction(f"G0 X{instruction_1[0]} Y{instruction_1[1]} F600", 2)
                    else:
                        a = False
                        c = False
        '''
        if process == "teste_relativo":

            while c:
                a = True
                message = f"teste"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header+message)
                time.sleep(1)

                give_instruction("G90", 1)
                give_instruction("G0 X1 F100", 1)
                
                time.sleep(10)
                give_instruction("G0 Y1 F100", 1)

                #Enviar a instru????o para a cabe??a 1 se mover para a estimativa inicial
                time.sleep(9)

                initial_estimate = np.array([float(52), float(25)])
                instruction = np.copy(initial_estimate)
                give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)

                while a:
                    
                    try:
                        while a:
                            #receber a dist??ncia que deve andar a cabe??a
                            username_header = client_socket.recv(HEADER_LENGTH)
                            if not len(username_header):
                                print("connection closed by the server")
                                sys.exit()

                            username_length = int(username_header.decode("utf-8").strip())
                            username = client_socket.recv(username_length).decode("utf-8")

                            message_header = client_socket.recv(HEADER_LENGTH)
                            message_length = int(message_header.decode("utf-8").strip())
                            message = client_socket.recv(message_length)
                            d = pickle.loads(message)

                            if d[0] != 0 and d[1] != 0:
                                instruction += d
                                give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)
                            else:
                                a = False
                                c = False



                    except IOError as e:
                        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                            print('Reading error', str(e))
                            sys.exit()
                        continue

                    except Exception as e:
                        print('General error', str(e))
                        sys.exit()
                        pass

            print(f"The vector between the origin and the QR code is: {instruction}.")
        '''
        if process == "testeNozzle":
            a = True
            c = True
            while a:
                message = f"testeNozzle"
                send_message(HEADER_LENGTH, message, client_socket)
                time.sleep(1)
                give_instruction("G90", 1)
                give_instruction("G0 X1 F100", 1)

                time.sleep(10)
                give_instruction("G0 Y1 F100", 1)

                #Enviar a instru????o para a cabe??a 1 se mover para a estimativa inicial
                time.sleep(9)

                initial_estimate = np.array([float(18), float(13)])
                instruction = np.copy(initial_estimate)
                give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)

                while c:
                    d = receive_message(HEADER_LENGTH, client_socket)
                    if d[0] != 0 and d[1] != 0:
                        instruction += d
                        give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)
                    else:
                        a = False
                        c = False
            print(f"The vector between the Nozzle and the camera center is: {instruction}.")
        '''
        if process == "testeNozzle":

            while c:
                a = True
                message = f"testeNozzle"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header+message)
                time.sleep(1)

                give_instruction("G90", 1)
                give_instruction("G0 X1 F100", 1)
                
                time.sleep(10)
                give_instruction("G0 Y1 F100", 1)

                #Enviar a instru????o para a cabe??a 1 se mover para a estimativa inicial
                time.sleep(9)

                initial_estimate = np.array([float(52), float(25)])
                instruction = np.copy(initial_estimate)
                give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)

                while a:
                    
                    try:
                        while a:
                            #receber a dist??ncia que deve andar a cabe??a
                            username_header = client_socket.recv(HEADER_LENGTH)
                            if not len(username_header):
                                print("connection closed by the server")
                                sys.exit()

                            username_length = int(username_header.decode("utf-8").strip())
                            username = client_socket.recv(username_length).decode("utf-8")

                            message_header = client_socket.recv(HEADER_LENGTH)
                            message_length = int(message_header.decode("utf-8").strip())
                            message = client_socket.recv(message_length)
                            d = pickle.loads(message)

                            if d[0] != 0 and d[1] != 0:
                                instruction += d
                                give_instruction(f"G0 X{instruction[0]} Y{instruction[1]} F600", 1)
                            else:
                                a = False
                                c = False



                    except IOError as e:
                        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                            print('Reading error', str(e))
                            sys.exit()
                        continue

                    except Exception as e:
                        print('General error', str(e))
                        sys.exit()
                        pass
            
            print(f"The vector between the origin and the QR code is: {instruction}.")
        '''
        
        """Cabe??a 2"""
        #Medir dist??ncia
        if process == "1_RP2":
            message = f"Proc1_2"
            send_message(HEADER_LENGTH, message, client_socket)
            #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
            give_instruction("G91", 1)
            time.sleep(3)

            give_instruction("G0 X10 F100", 1)

            d = receive_message(HEADER_LENGTH, client_socket)
            #d = pickle.loads(message)
            print(f"{username} > {d}")
            print(f"O vector recebido foi: {d} ")
            a = False

        #Calibrar E-Steps
        if process == "2_RP2":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503
            while a:
                b = True
                message = f"Proc2_2"
                send_message(HEADER_LENGTH, message, client_socket)
                time.sleep(1)

                #Send A to RP
                A = return_steps_x(1)
                message = A
                send_message(HEADER_LENGTH, message, client_socket)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 X10 F100", 1)

                while b:
                    D = receive_message(HEADER_LENGTH, client_socket)
                    if abs(D - A) == 0:
                        a = False
                        b = False
                        print(D)

                    elif abs(D - A) > 0:
                        print("Parametro nao esta afinado")
                        print("Novo parametro ser?? atualizado")
                        give_instruction(f"M92 X{D}", 1)
                        give_instruction(f"M500", 1)
                        give_instruction(f"M501", 1)
                        b = False

        #Calibrar E-Steps
        if process == "3_RP2":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503
            while a:
                b = True
                message = f"Proc3_2"
                send_message(HEADER_LENGTH, message, client_socket)
                time.sleep(1)

                #Send A to RP
                A = return_steps_y(1)
                message = A
                send_message(HEADER_LENGTH, message, client_socket)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 Y10 F100", 1)

                while b:
                    D = receive_message(HEADER_LENGTH, client_socket)
                    if abs(D - A) == 0:
                        a = False
                        b = False
                        print(D)

                    elif abs(D - A) > 0:
                        print("Parametro nao esta afinado")
                        print("Novo parametro ser?? atualizado")
                        give_instruction(f"M92 Y{D}", 1)
                        give_instruction(f"M500", 1)
                        give_instruction(f"M501", 1)
                        b = False

            '''
            while c:
                a = True
                message = f"Proc2_2"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header+message)
                time.sleep(1)

                #Send A to RP
                A = return_steps_x(1)
                message = f"{A}"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 X10 F100", 1)

                
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
                            message = client_socket.recv(message_length).decode("utf-8")
                            D = float(message)


                            if abs(D - A) == 0:
                                    c = False
                                a = False
                                print(D)
                                break
                            elif abs(D - A) > 0:
                                print("Parametro nao esta afinado")
                                print("Novo parametro ser?? atualizado")
                                give_instruction(f"M92 X{D}", 1)
                                give_instruction(f"M500", 1)
                                give_instruction(f"M501", 1)
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
                       

        if process == "3_RP2":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503

            while c:
                a = True
                message = f"Proc3_2"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header+message)
                time.sleep(1)

                #Send A to RP
                A = return_steps_y(1)
                message = f"{A}"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)

                #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
                give_instruction("G91", 1)
                time.sleep(5)
                give_instruction("G0 Y10 F100", 1)


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
                            message = client_socket.recv(message_length).decode("utf-8")
                            D = float(message)


                            if abs(D - A) < 0.5:
                                c = False
                                a = False
                                print(D)
                                break
                            elif abs(D - A) > 0.5:
                                print("Parametro nao esta afinado")
                                print("Novo parametro ser?? atualizado")
                                give_instruction(f"M92 Y{D}", 1)
                                give_instruction(f"M500", 1)
                                give_instruction(f"M501", 1)
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
                         '''

        if process == "4_RP2":
            message = f"Proc_4_2"
            send_message(HEADER_LENGTH, message, client_socket)
            give_instruction("G91", 1)
            time.sleep(5)
            give_instruction("G0 X10 F100", 1)
            
            time.sleep(20)
            give_instruction("G0 Y10 F100", 1)

            #Receive Skew Angle
            skew_angle = receive_message(HEADER_LENGTH, client_socket)
            print(f"{username} > {skew_angle}")
            print(f"O ??ngulo entre os vetores deslocamento xx e yy: {skew_angle} ")


        '''
        if process == "4_RP2":
            message = f"Proc4_2"
            message = message.encode("utf-8")
            message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(message_header+message)
            #Esperar 5 segundos para o RP receber a ordem de come??ar a gravar e mandar a m??quina mover
            give_instruction("G91", 1)
            time.sleep(5)

            give_instruction("G0 X10 F100", 1)
            
            time.sleep(20)
            give_instruction("G0 Y10 F100", 1)

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

                        skew_angle = float(message)
                        #skew_angle = pickle.loads(message)
                        print(f"{username} > {skew_angle}")
                        print(f"O ??ngulo entre os vetores deslocamento xx e yy: {d} ")
                        if message_length > 0:
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
        '''
    return None

#def main():
username = "PC"
HEADER_LENGTH = 10
#IP = "127.0.0.1"
IP = '10.16.233.124'
PORT = 1234

printer = Printer.create_printer_standard_from_parts_dimensions(length_x=380, length_y=400, length_z=50)
configuration = [2]
for pos_y in range(len(configuration)):
    for pos_x in range(configuration[pos_y]):
        aux_head = Head.create_standard_head()
        aux_head.set_position_in_rails(pos_x=pos_x, pos_y=pos_y)
        aux_head.calculate_origin_point(nr_rails=len(configuration), nr_heads_in_rail=configuration[pos_y])
        aux_head.place_head_in_point(point=aux_head.reference_point)
        aux_head.calculate_max_x_reference_point(nr_heads_in_rail=configuration[pos_y], length_x=printer.length_x)
        aux_head.calculate_safe_range(nr_rails=len(configuration))
        aux_head.calculate_soft_limits_from_reference_points()
        aux_head.create_safe_area(nr_rails=len(configuration))
        aux_head.create_unsafe_area(nr_rails=len(configuration))

        printer.add_head_to_printer(aux_head)

printer.set_heads_position_on_rails()
printer.update_printer_dimensions()
printer.place_heads_in_home_point()
printer.calculate_rails_build_area()
printer.calculate_neighbours_heads()

printer.set_com_ports(["COM3", "COM4"])
#printer.list_of_heads[0].material_id = 0
#printer.list_of_heads[1].material_id = 1

h1 = printer.list_of_heads[0]
h2 = printer.list_of_heads[1]


h1.connect_to_serial(h1.serial_port)
h2.connect_to_serial(h2.serial_port)

h2.flush_start_messages()
message = h2.read_serial_message(show=False)
#give_instruction("G28")
message = give_instruction("G28", 1)
message = give_instruction("G28", 2)
give_instruction("G0 X20 Z10 F100", 1)
give_instruction("G0 X20 Y20 Z10 F100", 2)
test_client_func(username, HEADER_LENGTH, IP, PORT)

#if __name__ == "__main__":
#    main()
