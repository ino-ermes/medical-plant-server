import json
import socket
import uuid
import threading

class PredictClient:
    
    __instance = None

    @staticmethod
    def get_instance():
        if PredictClient.__instance is None:
            PredictClient()
        return PredictClient.__instance

    def __init__(self, PORT=5001):
        if PredictClient.__instance is not None:
            raise Exception("This class is a singleton!")
        
        PredictClient.__instance = self
        
        self.PORT = PORT
        
        self.BUFSIZE = 4096
        self.SERVER = socket.gethostbyname(socket.gethostname())
        print("Server address:", self.SERVER)
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = "utf-8"
        self.SEP = ':!'.encode(self.FORMAT)
        self.BUFFER = b''
        self.results = dict()
        self.listening = False

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.server.listen(1)
        
        self.lock = threading.Lock()      

    def __recv(self):
        try:
            endIndex = -1
            while True:
                chunk = self.client.recv(self.BUFSIZE)
                
                if not chunk:
                    self.BUFFER = b''
                    break
                
                self.BUFFER += chunk
                
                endIndex = self.BUFFER.find(self.SEP)
                if endIndex != -1:
                    break
            
            if self.BUFFER:
                data = self.BUFFER[ : endIndex]
                self.BUFFER = self.BUFFER[endIndex + len(self.SEP) : ]
                return data.decode(self.FORMAT)
            return ''
        except:
            return ''

    def __send(self, raw):
        try:
            self.client.sendall(raw.encode(self.FORMAT) + self.SEP)
            return True
        except:
            return False

    def listen(self):
        threading.Thread(target=self.__connect, daemon=True).start()

    def __connect(self):
        self.lock.acquire()
        self.listening = True
        while True:
            print("Listening for predict server...")
            client, addr = self.server.accept()
            self.client = client
            self.addr = addr
            
            if not self.__send('YAWARAKAI'):
                print("Error when connect to predict server. Retrying...")
                client.close()
                continue
            key = self.__recv()
            if key != "MYKEY":
                self.__send("Error code: doko ni mo ikanaide")
                client.close()
                print("Error when connect to predict server. Retrying...")
                continue

            if not self.__send("OK"):
                print("Error when connect to predict server. Retrying...")
                continue
            
            self.listening = False
            print("Connected to predict server")
            break
        
        self.lock.release()

    def predict(self, imageUrl, mode):
        if self.listening == True:
            return -1
        
        self.lock.acquire()
        
        id = str(uuid.uuid1())
        request = json.dumps({"id": id, "payload": {"img_url": imageUrl, 'mode': mode}})
        if not self.__send(request):
            self.listen()
            self.lock.release()
            return -1
        while not self.results.get(id):
            raw = self.__recv()
            if raw:
                response = json.loads(raw)
                self.results[response['id']] = response['payload']
            else:
                self.lock.release()
                return -1
            
        self.lock.release()
        
        return self.results.pop(id)

    def close(self):
        self.__send('YUMEMISETE')
        self.client.close()
        self.server.close()