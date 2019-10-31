import esp32
import random
import os
import ubinascii
import machine
import hmac, hashlib
import json
import struct
from ucryptolib import aes


class CryptAes:

    #-----------------------------------------------COMMON-----------------------------------------------------------#   

    def __init__(self, sessionID):
        """
        This class initializes all keys and ids
        nodeid     : unique id to identify device or board
        iv         : pseudorandom initialization vector, this needs to be DIFFERENT for every message.
        staticiv   : static initialization vector to obfuscate the randomized
                     initialization vector sent with each message, NOT used for any data
        ivkey      : unique key to encrypt the initialization vector
        datakey    : unique key to encypt the Payload/Data
        passphrase : key to generate the HMAC code for authentication
        
        sessionID  : unique value to identify the current communication session, generated only by Spinner #2
        
        ***********************NOTE******************************
        AES is a block cipher with a block size of 128 bits; that's why it encrypts 16 bytes at a time.        
        The block size of CBC mode of encryption is 16, make sure that any data going into AES
        Encryption is of size 16 bytes.
        """
        self.nodeid = b"1212121212121212"
        self.staticiv = b"abcdef2345678901"
        #self.iv = b"6969420069694200"
        #self.iv = 'b"' + str(random.randint(1000000000000000,9999999999999999)) + '"'
        piece1 = str(random.randint(10000000, 99999999))
        piece2 = str(random.randint(10000000, 99999999))
        self.iv = piece1 + piece2
        self.iv = self.iv.encode()
        #self.iv = 'b"'
        #self.iv = "1"
        #self.iv = os.urandom(16)
        #print(self.iv)
        self.ivkey = b"2345678901abcdef"
        self.datakey = b"0123456789abcdef"
        self.passphrase = b"mypassphrase1234"
        self.sessionID = str(sessionID).encode("utf-8")

    #------------------------------------SPINNER #1 Needs to Use These Functions--------------------------------------#   


    def encrypt(self, sensor_data):
        """Encrypt each of the current initialization vector (iv), the nodeid, and the sensor_data 
        using (staticiv, ivkey) for iv and (iv, datakey) for nodeid and sensor_data
        :param sensor_data  : Acceleration X, Acceleration Y, Acceleration Z, and Temperature
        """
#         for x in range(0,15):
#             self.iv = self.iv + str(random.randint(0,9))
#         #self.iv = self.iv + '"'
#         self.iv = self.iv.encode()

        print(self.iv)
        print(type(self.iv))

        encryption1 = aes(self.ivkey, 2, self.staticiv)
        encryption2 = aes(self.datakey, 2, self.iv)
        
        print(self.iv)
        print(type(self.iv))
        
        self.encrypted_data = encryption2.encrypt(sensor_data)
        self.encrypted_iv = encryption1.encrypt(self.iv)
        self.encrypted_nodeid = encryption2.encrypt(self.nodeid)
        
    
    def sign_hmac(self, sessionID):
        """Generate HMAC by using passphrase, and combination of encrypted iv, encrypted nodeid, 
        encrypted data, received sessionID.
        :param sessionID: unique value to identify the current communication session
        :return         : generated HMAC
        """
        msg = repr(self.encrypted_iv) + repr(self.encrypted_nodeid) + repr(self.encrypted_data) + str(sessionID)
        print(repr(self.encrypted_iv))
        print(repr(self.encrypted_nodeid))
        print(repr(self.encrypted_data))
        print(str(sessionID))
        dig = hmac.new(self.passphrase, msg=msg, digestmod=hashlib.sha224).hexdigest()
        print(dig)
        return dig

        
    def send_mqtt(self, hmac_signed):
        """Prepare the message for MQTT transfer using all of encrypted iv, encrypted nodeid, 
        encrypted data, HMAC. Create the message in JSON format.
        :param hmac_signed  : generated HMAC
        :return             : MQTT message to publish to Spinner #2 on Topic "Sensor_Data"
        """
        encrypt_dict = {'iv' : repr(self.encrypted_iv), 'nodeid' : repr(self.encrypted_nodeid), 'data' : repr(self.encrypted_data), 'hmac' : hmac_signed}
        payload = json.dumps(encrypt_dict)
        print(payload)
        return payload
        
        
        
    #------------------------------------SPINNER #2 Needs to Use These Functions--------------------------------------#   
    
    
    def verify_hmac(self, payload, sessionID):
        """Authenticates the received MQTT message. 
        Generate HMAC using passphrase, sessionID, RECEIVED encrypted iv, encrypted nodeid, encrypted data 
        and compare with received hmac inside payload to authenticate.
        :param payload  : received MQTT message from Spinner #1. This includes all encrypted data, nodeid, iv, and HMAC
        :return message : MQTT message to publish to Spinner #1 on Topic "Acknowledge", can be "Failed Authentication" 
                          if verification is unsuccessful
        """
        #remake hmac
        
        return_str = None
        
        sessionID = str(sessionID)
        sessionID = sessionID.encode()
        #((str(sessionID)).encode())
        msg = payload['iv'] + payload['nodeid'] + payload['data'] + repr(sessionID)
        dig = hmac.new(self.passphrase, msg=msg, digestmod=hashlib.sha224).hexdigest()
        print("My Hmac")
        print(dig)
        print("His Hmac")
        print(payload['hmac'])
#         print("IV")
#         print(payload['iv'])
#         print("NodeID")   
#         print(payload['nodeid'])
        print("Data")
        print(payload['data'])
#         print("SessionID")
#         print(str(sessionID).encode())

        if (payload['hmac']) == dig:
            return_str = self.decrypt(payload)
        else:
            return_str = "Failed Authentication"
            
        return(return_str)     
            
    def decrypt(self, payload):
        """Decrypts the each encrypted item of the payload.
        Initialize decryption cipher for each item and and use cipher to decrypt payload items.
        :param payload  : received MQTT message from Spinner #1. This includes all encrypted data, nodeid, iv, and HMAC
        :return         : MQTT message to publish to Spinner #1 on Topic "Acknowledge", can be "Successful Decryption"
        """
        encryption3 = aes(self.ivkey, 2, self.staticiv)

        #print(len(eval(payload['iv'])))
        #print(len(payload['data']))
        self.decrypt1 = encryption3.decrypt(eval(payload['iv']))
        encryption4 = aes(self.datakey, 2, self.decrypt1)
        self.decrypt2 = encryption4.decrypt(eval(payload['data']))
        self.decrypt3 = encryption4.decrypt(eval(payload['nodeid']))
        
        decrypt_dict = {'decrypt_iv' : self.decrypt1, 'decrypt_data' : self.decrypt2, 'decrypt_nodeid' : self.decrypt3}
        decrypt_payload = json.dumps(decrypt_dict)
        return decrypt_payload
