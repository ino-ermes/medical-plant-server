from threading import Lock
from flask_socketio import SocketIO, emit
import uuid
from flask import request
import time
import os

class PredictClient:
    __instance = None

    @staticmethod
    def get_instance():
        if PredictClient.__instance is None:
            PredictClient()
        return PredictClient.__instance

    def __init__(self):
        if PredictClient.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__socket = SocketIO()
            def handle_predict_response(data):
                try:
                    id = data['id']
                    result = data['result']
                except:
                    return
                with self.__lock:
                    if self.__response_data.get(id) == -1:
                        self.__response_data[id] = result
            self.__socket.on_event('predict_result', handle_predict_response)
            
            def handle_connect(auth):
                try:
                    if auth["key"] == self.__predict_key:
                        with self.__lock:
                            if self.__curSid is None:
                                self.__curSid = request.sid
                            else:
                                return
                    else:
                        return
                except:                    
                    return
                print("Predict server is connected")
                emit('message', 'i found out')
            self.__socket.on_event('connect', handle_connect)
            
            def handle_disconnect():
                with self.__lock:
                    if request.sid == self.__curSid:
                        self.__curSid = None
                        print("Predict server is disconnected")
            self.__socket.on_event('disconnect', handle_disconnect)
            
            
            self.__app = None
            self.__lock = Lock()
            self.__response_data = {}
            self.__curSid = None
            self.__predict_key = os.getenv("PREDICT_SECRET")
            PredictClient.__instance = self

    def init_app(self, app):
        self.__app = app
        self.__socket.init_app(app)

    def isPredictServerOn(self):
        with self.__lock:
            return self.__curSid is not None

    def predict(self, img_url, mode):
        
        id = str(uuid.uuid1())
        self.__socket.emit('predict', {'id': id, 'img_url': img_url, 'mode': mode}, to=self.__curSid)
        with self.__lock:
            self.__response_data[id] = -1
            
        start_time = time.time()
        while True:
            with self.__lock:
                response = self.__response_data.get(id)
                if response != -1:
                    self.__response_data.pop(id)
                    break
            if time.time() - start_time > 60:
                self.__response_data.pop(id)
                raise TimeoutError("Prediction request timed out after 60 seconds")
        return response 
        
        
        