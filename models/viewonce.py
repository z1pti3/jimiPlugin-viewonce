import time
from pathlib import Path
import secrets
import base64
import hashlib
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from core import db, audit

with open(Path("plugins","viewonce","data","viewoncePub.pem")) as f:
  viewoncePublicKey = f.read()
with open(Path("plugins","viewonce","data","viewoncePriv.pem")) as f:
  viewoncePrivateKey = f.read()

class _viewonce(db._document):
    data = str()
    tag = str()
    nonce = str()
    expiry = int()
    accessCount = int()

    _dbCollection = db.db["viewonce"]

    def new(self, data, expiry=0, accessCount=1):
        token, returnData = self.setData(data)
        if expiry > 0:
            self.expiry = time.time() + expiry
        self.accessCount = accessCount
        super(_viewonce, self).new()
        return ( str(self._id), token, returnData)
        
    def setData(self,data):
        # Get Key
        keyBytes = get_random_bytes(16)
        key = hashlib.sha256(keyBytes).digest()
        # AES
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        cipherText, tag = cipher.encrypt_and_digest(data.encode())
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(viewoncePublicKey))
        # RSA
        encKey = cipher_rsa.encrypt(keyBytes)
        # Storage
        encData = base64.b64encode(cipherText).decode()
        returnData = ""
        keepData = ""
        bit = False
        for encChar in encData:
            if not bit:
                returnData += encChar
            else:
                keepData += encChar
            bit = not bit
        self.data = keepData
        self.tag = base64.b64encode(tag).decode()
        self.nonce = base64.b64encode(nonce).decode()
        # Return token
        return base64.b64encode(encKey).decode(), returnData

    def getData(self,token,encData):
        # RSA
        cipher_rsa = PKCS1_OAEP.new(RSA.import_key(viewoncePrivateKey))
        key = hashlib.sha256(cipher_rsa.decrypt(base64.b64decode(token.encode()))).digest()
        # AES
        nonce = base64.b64decode(self.nonce.encode())
        tag = base64.b64decode(self.tag.encode())
        encData2 = self.data
        data = ""
        for x in range(0,len(encData)):
            data += encData[x]
            data += encData2[x]
        data = base64.b64decode(data.encode())
        # AES
        cipher = AES.new(key, AES.MODE_EAX, nonce = nonce)
        data = cipher.decrypt(data).decode()
        try:
            cipher.verify(tag)
            # Remove entry from DB when access count is below 1
            self.accessCount -= 1
            if self.accessCount < 1:
                self.delete()
            return data
        except ValueError:
            return None
