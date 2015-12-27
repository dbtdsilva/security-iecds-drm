from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from hashlib import sha512, pbkdf2_hmac
from Crypto import Random
import OpenSSL
from OpenSSL import crypto
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from base64 import b64decode
import os

class Cipher:
    BLOCK_SIZE = 32
    PLAYER_HASH_LEN = 64
    USER_HASH_LEN = 64
    def __init__(self):
        pass

    def generateChallenge(self):
        return Random.new().read(32)

    def verifySignature(self, certificate_pem, original_data, signature):
        b64 = certificate_pem.replace("\n","").\
                replace("-----BEGIN PUBLIC KEY-----","").\
                replace("-----END PUBLIC KEY-----","")
        keyder = b64decode(b64)
        keypub = RSA.importKey(keyder)
        verifier = PKCS1_v1_5.new(keypub)
        digest = SHA.new()
        digest.update(original_data)
        return verifier.verify(digest, signature)

    def cleanReceivedPEM(self, pem):
        pem = pem[:20] + pem[20:-20].replace(' ', '\n') + pem[-20:]
        if pem[-1] != '\n':
            pem += '\n'
        return pem

    def generatePlayerHash(self, pkey):
        h = sha512()
        h.update(pkey)
        return h.digest()

    def validateCertificate(self, certificate_pem, cidadao_name, autent_name):
        cert_obj = crypto.load_certificate(crypto.FILETYPE_PEM, certificate_pem)
        print len(certificate_pem)
        chain = []
        try:
            autent_id = int(autent_name[-1])
            cidadao_id = int(cidadao_name[-1])
            if cidadao_id < 1 or cidadao_id > 3 or autent_id < 1 or autent_id > 9:
                raise ValueError
        except ValueError:
            return False

        autent_filename = "EC-de-Autenticacao-do-Cartao-de-Cidadao-000" + str(autent_id) + ".pem"
        cidadao_filename = "Cartao-de-Cidadao-00" + str(cidadao_id) + ".pem"
        trusted_certs = [autent_filename, cidadao_filename, "Baltimore_CyberTrust_Root.pem","ECRaizEstado.pem"]
        for fn in trusted_certs:
            f = open(os.path.join(os.getcwd(), "certificates","pteidcc",fn), 'r')
            chain.append(crypto.load_certificate(crypto.FILETYPE_PEM, f.read()))
            f.close()

        try:
            store = crypto.X509Store()
            for cert in chain:
                store.add_cert(cert)

            store_ctx = crypto.X509StoreContext(store, cert_obj)
            if store_ctx.verify_certificate() == None:
                return True
        except Exception:
            return False
        return False

    def generateUserHash(self, user_pem):
        h = sha512()
        h.update(user_pem)
        return h.digest()

    def generateIV(self):
        return Random.new().read(AES.block_size)

    def generateUserKey(self):
        return Random.new().read(self.BLOCK_SIZE)

    def convert_certificate_to_PEM(self, file_string, file_type=OpenSSL.crypto.FILETYPE_ASN1):
        if file_type != OpenSSL.crypto.FILETYPE_ASN1 and \
            file_type != OpenSSL.crypto.FILETYPE_PEM:
            return None
        if file_type == OpenSSL.crypto.FILETYPE_PEM:
            return file_string
        x509 = OpenSSL.crypto.load_certificate(file_type, file_string)
        return OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509)

    def getPlayerIntegrityHash(self, player_filelist, salt):
        hash = ""
        for file in player_filelist:
            hash += pbkdf2_hmac('sha512', open(file, 'r').read(), salt, 1000)
        return hexlify(pbkdf2_hmac('sha512', hash, salt, 1000))

    def pkcs7_decode(self, data, block_size):
        return data[:-bytearray(data)[-1]]

    def pkcs7_encode(self, data, block_size):
        char_to_pad = block_size - (len(data) % block_size)
        return data + str(bytearray([ char_to_pad for c in range(char_to_pad) ]))