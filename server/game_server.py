# Laboratorio di Programmazione di Reti - Università di Bologna - Campus di Cesena
# Giovanni Pau - Andrea Piroddi

# importiamo i moduli che utilizzeremo
import sys as os
import tkinter as tk
import sys
from tkinter import messagebox
import socket
import threading
import packet_decoder as pd
import random as rnd
import packet_type as pt
from time import sleep

BUFFER_SIZE = 4096
server = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080
clients = []
clients_number = 2
max_points = 2

window = tk.Tk()
window.title("Server")

# Cornice superiore composta da due pulsanti (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda: start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda: stop_server(server), state=tk.DISABLED)
btnStop.pack(side=tk.RIGHT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

players_num_frame = tk.Frame(window)
lbl_players = tk.Label(players_num_frame, text="Players number ->")
lbl_players.pack(side=tk.LEFT)
player_num_ent = tk.Entry(players_num_frame)
player_num_ent.pack(side=tk.RIGHT)
players_num_frame.pack(side=tk.TOP)

points_num_frame = tk.Frame(window)
lbl_points = tk.Label(points_num_frame, text="    Points to win ->")
lbl_points.pack(side=tk.LEFT)
points_num_ent = tk.Entry(points_num_frame)
points_num_ent.pack(side=tk.RIGHT)
points_num_frame.pack(side=tk.TOP)

# Cornice centrale composta da due etichette per la visualizzazione delle informazioni sull'host e sulla porta
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text="Address: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text="Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# Il frame client mostra l'area dove sono elencati i clients che partecipano al gioco
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


# Avvia la funzione server
def start_server():
    global server, HOST_ADDR, HOST_PORT, clients_number, max_points
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(socket.AF_INET)
        print(socket.SOCK_STREAM)

        server.bind((HOST_ADDR, HOST_PORT))
        server.listen(5)  # il server è in ascolto per la connessione del client
        clients_number = int(player_num_ent.get())
        max_points = int(points_num_ent.get())

        threading._start_new_thread(accept_clients, (server, ""))

        lblHost["text"] = "Address: " + HOST_ADDR
        lblPort["text"] = "Port: " + str(HOST_PORT)
        btnStart.config(state=tk.DISABLED)
        btnStop.config(state=tk.NORMAL)
    except ValueError as e:
        print(e)
        tk.messagebox.showerror(title="ERROR!", message="Invalid input")


# Arresta la funzione server
def stop_server(s):
    global clients
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    sys.exit()


def send_game_start():
    global clients
    for c in clients:
        if c['present'] is True:
            print("Mando start a " + c['name'])
            c['client'].send(pd.encode({'p_id': pt.Packet.start.value}))


def presents():
    i = 0
    for c in clients:
        if c['present'] is True:
            i += 1
    return i


def accept_clients(the_server, y):
    global clients_number
    print("New game ->" + str(len(clients)))
    while presents() < clients_number:
        client, addr = the_server.accept()
        clients.append(create_new_client(addr, client))
        print(clients[-1]['addr'])
        # utilizza un thread in modo da non intasare il thread della gui
        threading._start_new_thread(manage_new_client, (len(clients) - 1, True))
    sleep(3)
    send_game_start()


def create_new_client(addr, client):
    return {'client': client, 'addr': addr, 'name': "", 'answer': -1, 'score': 0, 'present': True, 'id': len(clients)}


# controlla se utente ha chiesto una domanda
def ask_for_question(data):
    if int(pd.decode(data)['p_id']) == pt.Packet.new_question_request.value:
        return True
    return False


def is_an_answer(data):
    if int(pd.decode(data)['p_id']) == pt.Packet.answer.value:
        return True
    return False


# Funzione per gestire l'uscita di un client
def player_left(index):
    global clients
    # send removed player to all
    index = int(index)
    clients[index]['present'] = False
    for c in clients:
        if c['present'] is True:
            c['client'].send(pd.encode({'p_id': pt.Packet.player_left.value, 'client': clients[index]['id']}))
    update_client_names_display()


def update_score(answer, index):
    i = int(index)
    if answer == clients[i]['answer']:
        clients[i]['score'] += 1
    else:
        clients[i]['score'] -= 1


def game_over(i):
    global clients, max_points
    i = int(i)
    if clients[i]['score'] == max_points:
        return True
    return False


def stop_game(i):
    global clients
    for c in clients:
        if c['present'] is True:
            c['score'] = 0
            c['client'].send(pd.encode({"p_id": pt.Packet.game_over.value, "winner": clients[int(i)]['id']}))
    threading._start_new_thread(accept_clients, (server, ""))
    update_client_names_display()


def manage_new_client(client_index, is_new):
    global server, clients, game_is_over
    # riceve il nome del client
    i = int(client_index)
    if is_new:
        clients[i]['name'] = pd.decode(clients[i]['client'].recv(BUFFER_SIZE))['name']
        update_client_names_display()  # aggiornare la visualizzazione dei nomi dei client
        # invia il nome dell'avversario
        for k in range(len(clients)):
            if clients[k]['present'] is True:
                clients[k]['client'].send(pd.encode({'p_id': pt.Packet.new_player.value, 'name': clients[i]['name'],
                                                     'id': clients[i]['id']}))
                if k == i:
                    for s in range(len(clients)):
                        if s != k:
                            clients[k]['client'].send(pd.encode({'p_id': pt.Packet.new_player.value,
                                                                 'name': clients[s]['name'],
                                                                 'id': clients[s]['id']}))

    # rimane in attesa
    player_loop(i)


def player_loop(i):
    global clients, game_is_over
    i = int(i)
    while True:
        # estrae il messaggio del giocatore dai dati ricevuti
        try:
            data = clients[i]['client'].recv(BUFFER_SIZE)
        except Exception as e:
            player_left(i)
            break
        if not data:
            break
        if ask_for_question(data):
            # invia una nuova domanda
            send_new_question(i)
        elif is_an_answer(data):
            # invia i nuovi punteggi a tutti e manda una nuova domanda
            update_score(int(pd.decode(data)['answer']), i)
            if game_over(i):
                stop_game(i)
            else:
                for c in clients:
                    if c['present'] is True:
                        c['client'].send(pd.encode({'p_id': pt.Packet.player_score.value, 'client': clients[i]['id'],
                                                    'score': clients[i]['score']}))


def send_new_question(i):
    global clients
    question = generate_new_question()
    clients[int(i)]['answer'] = question[1]
    clients[int(i)]['client'].send(pd.encode({'p_id': pt.Packet.new_question.value, 'question': question[0]}))


def generate_new_question():
    a = rnd.randint(0, 10)
    b = rnd.randint(0, 10)
    return "{} * {}".format(a, b), int(a * b)


# Aggiorna la visualizzazione del nome del client quando un nuovo client si connette O
# Quando un client connesso si disconnette
def update_client_names_display():
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in clients:
        if c['present'] is True:
            tkDisplay.insert(tk.END, c['name'] + "\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()
