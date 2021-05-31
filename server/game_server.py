# Laboratorio di Programmazione di Reti - Università di Bologna - Campus di Cesena
# Giovanni Pau - Andrea Piroddi

# importiamo i moduli che utilizzeremo
import tkinter as tk
import socket
import threading
import packet_decoder as pd
import random as rnd
from time import sleep

BUFFER_SIZE = 4096

window = tk.Tk()
window.title("Server")

# Cornice superiore composta da due pulsanti (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda: start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda: stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

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

server = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080
clients = []
clients_number = 3
max_points = 3
game_is_over = False


# Avvia la funzione server
def start_server():
    global server, HOST_ADDR, HOST_PORT
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # il server è in ascolto per la connessione del client

    threading._start_new_thread(accept_clients, (server, ""))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Arresta la funzione server
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)


def send_game_start():
    global clients
    for c in clients:
        c['client'].send("start").encode()


def accept_clients(the_server, y):
    global clients_number
    while len(clients) < clients_number:
        client, addr = the_server.accept()
        clients.append(create_new_client(addr, client))
        print(clients[-1]['addr'])
        # utilizza un thread in modo da non intasare il thread della gui
        threading._start_new_thread(manage_new_client, (len(clients) - 1, ""))
    sleep(1)
    send_game_start()


def create_new_client(addr, client):
    return {'client': client, 'addr': addr, 'name': "", 'answer': -1, 'score': 0, 'present': True, 'id': len(clients)}


# controlla se utente ha chiesto una domanda
def ask_for_choice(player_choice):
    if player_choice.decode() == "get":
        return True
    return False


def is_an_answer(player_choice):
    try:
        player_choice.decode().get("answer")
        return True
    except Exception as e:
        return False


# Funzione per gestire i messaggi dal client corrente
def player_left(index):
    global clients
    # send removed player to all
    clients[int(index)]['present'] = False
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
    global clients, game_is_over
    game_is_over = True
    for c in clients:
        c['client'].send(pd.encode({"winner": clients[int(i)]['id']}))


def manage_new_client(client_index, ignored):
    global server, clients, game_is_over

    # riceve il nome del client
    i = int(client_index)
    clients[i]['name'] = pd.decode(clients[i]['client'].recv(BUFFER_SIZE))['name']
    update_client_names_display()  # aggiornare la visualizzazione dei nomi dei client
    # invia il nome dell'avversario
    for k in range(len(clients)):
        if k != i:
            clients[k]['client'].send(pd.encode({'opponent_name':clients[i]['name']}))

    # rimane in attesa
    player_loop(i)
    try:
        clients[i]['socket'].close()
    except Exception as e:
        pass


def player_loop(i):
    global clients, game_is_over
    i = int(i)
    while not game_is_over:
        try:
            data = clients[i]['client'].recv(BUFFER_SIZE)
        except Exception as e:
            player_left(i)
            break
        if not data:
            break

        # estrae il messaggio del giocatore dai dati ricevuti
        player_choice = data[11:len(data)]

        if ask_for_choice(player_choice):
            send_new_question(i)
        elif is_an_answer(player_choice):
            # invia i nuovi punteggi a tutti e manda una nuova domanda
            update_score(player_choice.decode(), i)
            for c in clients:
                c['client'].send(pd.encode({'client': clients[i]['id'], 'score': clients[i]['score']}))
            if game_over(i):
                stop_game(i)
        print(player_choice.decode())


def send_new_question(i):
    global clients
    question = generate_new_question()
    clients[int(i)]['answer'] = question[1]
    clients[int(i)]['client'].send(pd.encode({'question': question[0]}))


def generate_new_question():
    a = rnd.randint(0, 10)
    b = rnd.randint(0, 10)
    return "%a * %b".format(a, b), int(a * b)


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
