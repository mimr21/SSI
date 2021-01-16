#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import signal
import errno
import time
import random
import nexmo


from fuse import FUSE, FuseOSError, Operations

def enviarSMS(tokenEnviar, numero):
    sms = nexmo.Client(key='06b932d7', secret='d6cwUZDsyWBTZSlS')
    try:
        sms.send_message({
            'from': 'Vonage APIs',
            'to': numero,
            'text': 'Ola este é o token '+tokenEnviar,
        })
        return True
    except:
        print("falha no envio da mensagem")
        return False

def timeout(signum, frame):
    raise IOError("Token nao chegou a tempo")

class Passthrough(Operations):
    def __init__(self, root):
        self.root = root

    def open(self, path, flags):
        full_path = self._full_path(path)
        fl = 1
        #Perguntar quem e
        try:
            print("Insira username:")
            username = input()
            os.chmod("utilizadores.txt", 400)
            with open("utilizadores.txt", 'r') as fich:        
                for linha in fich:
                    utilizador = linha.split(' ')
                    if(utilizador[0] == username):
                        #enviar sms com token
                        fl = 0
                        tokenEnviar = str(random.randint(100000, 999999))
    
                        enviou = enviarSMS(tokenEnviar,utilizador[1])
                        os.chmod("utilizadores.txt", 000)
                        if enviou :
                            tempoEspera = 30
                            try:
                                signal.signal(signal.SIGALRM, timeout)
                                signal.alarm(tempoEspera)
                                print("Introduza token recebido:")
                                tokenR = input() 
                                if(tokenR == tokenEnviar):
                                    signal.alarm(0)  #se chegar ca em 30s cancela o timeout                           
                                    os.chmod("utilizadores.txt", 444)
                                    return os.open(full_path, flags)
                                else: 
                                    #os.chmod("utilizadores.txt", 000)                                
                                    print("Codigo Incorreto!")
                                    signal.alarm(0)                                   
                                    return 0                            
                            except IOError: #alarme ultrapassou
                                #os.chmod("utilizadores.txt", 000)
                                print("\nToken nao chegou a tempo\n")
                        else : 
                            #os.chmod("utilizadores.txt", 000)
                            print("Erro no envio da mensagem")
                if fl==1:
                    os.chmod("utilizadores.txt", 000)
                    print("Utilizador desconhecido!")
        except IOError:
            print("the end")



    # Helpers
    # =======

    def _full_path(self, partial):
        partial = partial.lstrip("/")
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============


    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)



def main(mountpoint, root):
    os.chmod("utilizadores.txt", 000)
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    main(sys.argv[2], sys.argv[1])
