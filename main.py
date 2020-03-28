import socket
import pyperclip
import time
import multiprocessing
import ctypes

prev_clipboard = multiprocessing.Value(ctypes.c_char_p, bytes("kekwait", 'utf-8'))

def listen():
    global prev_clipboard

    sock_res = socket.socket()
    sock_res.bind(('', 9090))
    sock_res.listen(1)

    cur_clip = []

    while True:
        conn, addr = sock_res.accept()
        print('connected:', addr)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(data.upper())
            cur_clip.append(data.decode("utf-8"))

        if cur_clip:
            pyperclip.copy(''.join(cur_clip))
            prev_clipboard.acquire()
            prev_clipboard.value = bytes(pyperclip.paste(), 'utf-8')
            prev_clipboard.release()
            cur_clip = []

        conn.close()

        time.sleep(1)

def say():
    global prev_clipboard

    while True:
        cur_clipboard = pyperclip.paste()

        if cur_clipboard != prev_clipboard.value:
            sock = socket.socket()
            sock.connect(('192.168.1.68', 9090))
            sock.send(bytes(cur_clipboard, 'utf-8'))
            prev_clipboard.acquire()
            prev_clipboard.value = bytes(cur_clipboard, 'utf-8')
            prev_clipboard.release()
            sock.close()

        time.sleep(1)


if __name__ == '__main__':
    procs = []

    print(prev_clipboard.value)

    send_proc = multiprocessing.Process(target=say, args=())
    procs.append(send_proc)
    listen_proc = multiprocessing.Process(target=listen, args=())
    procs.append(listen_proc)

    for process in procs:
        process.start()

    for process in procs:
        process.join()

    for p in procs:
        print(p)