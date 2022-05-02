import json
import uuid, base64
import time
from Crypto.Cipher import PKCS1_OAEP, AES
from Cryptodome.Hash import SHA256
from Crypto.PublicKey import RSA
from termcolor import colored, cprint
import requests
from config.StaticData import InteractShStaticValue
import random, string
from utils.ConfigUtil import ConfigUtil

class InteractSh:
    def __init__(self):
        self.key = RSA.generate(2048)
        self.secret = str(uuid.uuid4())
        self.subDomain = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(33))
        self.httpProxy = ConfigUtil.readConfig()["proxy"]

    def registerInteractShServer(self):
        pubkey = self.key.public_key().exportKey()
        publicKey = base64.b64encode(pubkey).decode()
        correlation = self.subDomain[:20]

        data = {
            "public-key": publicKey,
            "secret-key": self.secret,
            "correlation-id": correlation
        }

        session = requests.Session()
        session.proxies.update(self.httpProxy)
        session.verify = False
        session.allow_redirects = True
        registerCall = session.post(url=InteractShStaticValue.RegisterApi, json=data, timeout=InteractShStaticValue.RegisterTimeOut)
        registerSuccessSignature = "registration successful"
        if registerSuccessSignature in registerCall.content.decode():
            interactUrl = self.subDomain + "." + InteractShStaticValue.interactShPrimaryDomain
            cprint("\n[*] Registered interactSh successfully", "blue")
            cprint("    [•] Interact URL: " + interactUrl, "cyan")
        else:
            cprint("\n[*] Error while registering interactSh", "red")
            exit()
        return interactUrl

    def pollDataFromWeb(self):
        correlation = self.subDomain[:20]
        responseJson = None
        queryStr = "id={}&secret={}".format(correlation, self.secret)

        session = requests.Session()
        session.proxies.update(self.httpProxy)
        session.verify = False
        session.allow_redirects = True
        maxPollingTime = InteractShStaticValue.maxPollingTime
        cprint("\n[*] Waiting for a response(up to " + str(2 * maxPollingTime) + " seconds)...\n", "yellow")
        isError = False
        for second in range(maxPollingTime):
            isError = False
            time.sleep(2)
            try:
                fetchData = session.get(url=InteractShStaticValue.PollDataApi + queryStr, timeout=InteractShStaticValue.PollDataTimeOut)
            except TimeoutError:
                cprint("\n[*] Interactsh not responding", "red")
                if second < maxPollingTime - 1:
                    cprint("\n[*] Trying again...", "yellow")
                    isError = True
                    continue
            responseJson = fetchData.json()

            if responseJson is None:
                isError = True
                break

            if "error" in responseJson:
                isError = True
                cprint("\nError when polling data: " + responseJson["error"], "red")
                break

            if responseJson["data"]:
                break
        if not isError:
            data = responseJson["data"]
            aesKey = responseJson["aes_key"]
            return data, aesKey
        else:
            return None, None

    def decryptAESKey(self, aes_Key):
        privateKey = RSA.import_key(self.key.export_key())
        rsaKey = PKCS1_OAEP.new(key=privateKey, hashAlgo=SHA256)
        rawAESKey = base64.b64decode(aes_Key)
        decryptAESKey = rsaKey.decrypt(rawAESKey)
        return base64.b64encode(decryptAESKey).decode()

    @staticmethod
    def decryptMessage(aesKey, dataList):
        if dataList:
            listPlainText = list()
            for data in dataList:
                iv = base64.b64decode(data)[:16]
                key = base64.b64decode(aesKey)
                cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
                plainText = cipher.decrypt(base64.b64decode(data)[16:])
                listPlainText.append(json.loads(plainText))
            return listPlainText
        return None

