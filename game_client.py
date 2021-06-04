# Marco Frattarola - Alex Siroli

import random
import tkinter as tk
from tkinter import PhotoImage
from tkinter import messagebox
import socket
import packet_decoder as pd
import packet_type as pt
import threading

# FINESTRA DI GIOCO PRINCIPALE
window_main = tk.Tk()
window_main.title("Il Gioco delle Tabelline")

server = None
HOST_ADDR = '127.0.0.1'
HOST_PORT = 8080
players_data = []  # id, name, score
BUFFER_SIZE = 4096
your_name = ""
your_id = ""

top_welcome_frame = tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text="Name:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command=lambda: connect())
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line_server = tk.Label(top_message_frame, text="***********************************************************")
lbl_line_server.pack()
top_message_frame.pack(side=tk.TOP)

top_frame = tk.Frame(window_main)
ranking_frame = tk.Frame(top_frame, highlightbackground="blue", highlightcolor="blue", highlightthickness=2)
lbl_title_name = tk.Label(ranking_frame, text="---- Classifica attuale ----", font="Helvetica 13 bold")
lbl_title_name.pack()
ranking_frame.pack(padx=(10, 10))
tk.Label(top_frame, text="***********************************************************").pack()
tk.Label(top_frame, text="Scegli un emoji", font="Helvetica 13").pack()

top_frame.pack()

middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()

button_frame = tk.Frame(window_main)

photo_one = PhotoImage(file=r"images/love.png")
photo_two = PhotoImage(file=r"images/thinky.png")
photo_three = PhotoImage(file=r"images/sassypng.png")

btn_one = tk.Button(button_frame, text="1", command=lambda: choice(1), state=tk.DISABLED, image=photo_one)
btn_two = tk.Button(button_frame, text="2", command=lambda: choice(2), state=tk.DISABLED, image=photo_two)
btn_three = tk.Button(button_frame, text="3", command=lambda: choice(3), state=tk.DISABLED, image=photo_three)
btn_one.grid(row=0, column=0)
btn_two.grid(row=0, column=1)
btn_three.grid(row=0, column=2)
button_frame.pack()

rules_frame = tk.Frame(middle_frame)
lbl_outcome = tk.Label(rules_frame, text="", font="Helvetica 13 bold")
lbl_outcome.pack()
lbl_rules = tk.Label(rules_frame, text="")
rules_frame.pack(side=tk.TOP)

form_frame = tk.Frame(middle_frame)
lbl_question = tk.Label(form_frame, text="")
lbl_question.pack(side=tk.LEFT)
lbl_question = tk.Label(form_frame, text="")
lbl_question.pack(side=tk.LEFT)
ent_answer = tk.Entry(form_frame)
ent_answer.pack(side=tk.LEFT)
ent_answer.config(state=tk.DISABLED)

btn_send = tk.Button(form_frame, text="Invia", command=lambda: send_answer())
btn_send.pack(side=tk.LEFT)
form_frame.pack(side=tk.TOP)
btn_send.config(state=tk.DISABLED)

final_frame = tk.Frame(middle_frame)
lbl_result = tk.Label(final_frame, text="", foreground="blue", font="Helvetica 14 bold")
lbl_result.pack()
tk.Label(final_frame, text="***********************************************************").pack()
lbl_final_result = tk.Label(final_frame, text="", font="Helvetica 13 bold", foreground="blue")
lbl_final_result.pack()
tk.Label(final_frame, text="***********************************************************").pack()
final_frame.pack(side=tk.TOP)

middle_frame.pack()

# azioni da eseguire per la chiusura
def on_closing():
    if server is not None:
        server.close()
    window_main.destroy()


# se viene interrotta la connessione con server
def connection_interrupted():
    tk.messagebox.showerror(title="Errore", message="La sessione è stata chiusa.")
    on_closing()


window_main.protocol("WM_DELETE_WINDOW", on_closing)


# per disattivare o attivare i button delle emoji
def enable_disable_buttons(todo):
    if todo == "disable":
        btn_one.config(state=tk.DISABLED)
        btn_two.config(state=tk.DISABLED)
        btn_three.config(state=tk.DISABLED)
    else:
        btn_one.config(state=tk.NORMAL)
        btn_two.config(state=tk.NORMAL)
        btn_three.config(state=tk.NORMAL)


# invio di una risposta
def send_answer():
    global server
    try:
        result = int(ent_answer.get())
        try:
            server.send(pd.encode({"p_id": pt.Packet.answer.value, "answer": result}))
        except:
            connection_interrupted()

        # disabilito gli elementi per inviare una risposta
        ent_answer.delete(0, 'end')
        ent_answer.config(state=tk.DISABLED)
        btn_send.config(state=tk.DISABLED)
    except ValueError:
        tk.messagebox.showerror(title="Errore", message="Devi inserire un numero!")


def connect():
    global your_name
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="Errore", message="Devi inserire il tuo nome!")
    else:
        your_name = ent_name.get()
        connect_to_server(your_name)


def connect_to_server(name):
    global server, HOST_PORT, HOST_ADDR
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((HOST_ADDR, HOST_PORT))
        try:
            server.send(pd.encode(
            {'p_id': pt.Packet.new_player_name.value, 'name': name}))  # Invia il nome al server dopo la connessione
        except:
            connection_interrupted()
        lbl_final_result["text"] = "LA PARTITA STA PER COMINCIARE..."

        # disabilita gli elementi per l'inserimento del nome
        btn_connect.config(state=tk.DISABLED)
        ent_name.config(state=tk.DISABLED)
        lbl_name.config(state=tk.DISABLED)

        # avvia un thread per continuare a ricevere messaggi dal server
        threading._start_new_thread(manage_messages_from_server, (server, ""))
    except Exception:
        tk.messagebox.showerror(title="Errore!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(
            HOST_PORT) + " Server may be Unavailable. Try again later")


# azioni da eseguire quando si sceglie una delle tre emoji
def choice(arg):
    # calcolo un numero random, sarà il numero della emoji trabocchetto
    rnd = random.randint(1, 3)
    if arg != rnd:
        # l'emoji non è trabocchetto
        lbl_outcome["text"] = "Complimenti! :)"
        lbl_outcome.configure(foreground="green")
        # invio la richiesta di una domanda
        try:
            server.send(pd.encode({"p_id": pt.Packet.new_question_request.value}))
        except:
            connection_interrupted()
        lbl_rules["text"] = "Rispondi alla seguente domanda:"
        lbl_rules.pack()
        enable_disable_buttons("disable")
    else:
        # l'emoji è trabocchetto
        lbl_outcome["text"] = "Mi dispiace :("
        lbl_outcome.configure(foreground="red")
        lbl_final_result["text"] = "SEI STATO ELIMINATO"
        # l'utente viene disconnesso
        server.close()


# aggiornamento della classifica in tempo reale
def update_scores():
    for player in players_data:
        player["label"]["text"] = player["name"] + " -> " + str(player["score"])


# gestione di tutti i messaggi ricevuti dal server
def manage_messages_from_server(sck, m):
    global lbl_question, your_id

    while True:  # per ogni partita
        while True:  # finche il server non invia l'inizio della partita
            data = ""
            try:
                data = sck.recv(BUFFER_SIZE)
            except:
                connection_interrupted()
            update_scores()
            if not data:
                connection_interrupted()
                break
            data = pd.decode(data)

            if int(data["p_id"]) == pt.Packet.start.value:  # se il messsaggio indica l'inizio della partita
                enable_disable_buttons("active")
                lbl_final_result["text"] = "PARTITA IN CORSO..."
                break

            if data["name"] == your_name and your_id == "":  # se il messaggio indica le mie informazioni
                your_id = data["id"]

            # tutti i dati del giocatore vengono salvati
            players_data.append({"name": data["name"], "id": data["id"], "score": 0})
            players_data[-1]["label"] = tk.Label(ranking_frame, text=players_data[-1]["name"] + " -> " + str(
                players_data[-1]["score"]))
            players_data[-1]["label"].pack()

        while True:  # finche non è finita la partita
            try:
                data = sck.recv(BUFFER_SIZE)
            except:
                connection_interrupted()
            if not data:
                connection_interrupted()
                break
            data = pd.decode(data)

            if int(data["p_id"]) == pt.Packet.new_question.value:  # mi arriva una domanda nuova
                enable_disable_buttons("disable")
                lbl_question["text"] = data["question"]
                ent_answer.config(state=tk.NORMAL)
                btn_send.config(state=tk.ACTIVE)

            elif int(data["p_id"]) == pt.Packet.player_score.value:  # mi arriva il punteggio di qualcuno

                # se il punteggio è il mio capisco se la risposta che ho inviato era giusta o sbagliata
                # e richiedo una nuova domanda
                if data["client"] == your_id:
                    your_score = 0
                    for player in players_data:
                        if player["id"] == your_id:
                            your_score = int(player["score"])
                            player["score"] = data["score"]
                    if int(data["score"]) > your_score:  # la risposta era corretta
                        lbl_result["text"] = "Giusto! +1"
                        lbl_result.configure(foreground="green")
                    else:  # la risposta era sbagliata
                        lbl_result["text"] = "Errato! -1"
                        lbl_result.configure(foreground="red")
                    update_scores()

                    # richiedo una nuova domanda
                    try:
                        server.send(pd.encode({"p_id": pt.Packet.new_question_request.value}))
                    except:
                        connection_interrupted()
                else:  # il punteggio è di un altro giocatore
                    for opp in players_data:
                        if opp["id"] == data["client"]:
                            opp["score"] = data["score"]
                    update_scores()

            elif int(data["p_id"]) == pt.Packet.player_left.value:  # un giocatore è stato eliminato
                for opp in players_data:
                    if opp["id"] == data["client"]:
                        opp["score"] = "Eliminato"
                update_scores()

            elif int(data["p_id"]) == pt.Packet.game_over.value:  # un giocatore ha vinto
                for opp in players_data:
                    if opp["id"] == data["winner"]:
                        opp["score"] = "Vincitore"
                update_scores()
                enable_disable_buttons("disable")
                break

        # resetto la grafica per una nuova partita
        lbl_outcome["text"] = ""
        lbl_rules["text"] = ""
        lbl_result["text"] = ""
        lbl_question["text"] = ""
        lbl_final_result["text"] = "NUOVA PARTITA A BREVE..."

        # rimuovo dalla classifica i giocatori eliminati e resetto i punteggi degli altri
        for player in players_data:
            if player["score"] == "Eliminato":
                player["label"].destroy()
                players_data.remove(player)
            else:
                player["score"] = 0


window_main.mainloop()
