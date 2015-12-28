import M2Crypto
import sys
import PyKCS11
from M2Crypto import X509
import OpenSSL
from base64 import b64encode

class cc_utils():
    def get_cert(self, certLabel):
        lib = "/usr/local/lib/libpteidpkcs11.so"
        status = 0
        #Load PKCS11 lib
        pkcs11 = PyKCS11.PyKCS11Lib()
        pkcs11.load(lib)

        #Open slots
        try:
            slots = pkcs11.getSlotList()
        except:
            print "Slot list failed: ", str(sys.exc_info()[1])
            return ("Failed to read citizen card!", None)

        s = slots[0]
        try:
            session = pkcs11.openSession(s)
        except:
            print "Session opening failed", str(sys.exc_info()[1])
            return ("Failed to open citizen card!", None)

        objs = session.findObjects(template=(
                (PyKCS11.CKA_LABEL, certLabel),
                (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE)))

        der = ''.join(chr(c) for c in objs[0].to_dict()['CKA_VALUE'])
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, der)
        pem = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509)
        return ("Success", pem)

    def get_subca_common_names(self):
        subca = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                self.get_cert('AUTHENTICATION SUB CA')[1])
        subca_cn = None
        for (name, value) in subca.get_subject().get_components():
            if name == 'CN':
                subca_cn = value
        rootca = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                self.get_cert('ROOT CA')[1])
        rootca_cn = None
        for (name, value) in rootca.get_subject().get_components():
            if name == 'CN':
                rootca_cn = value
        return (subca_cn, rootca_cn)

    # Signs given data
    def sign(self, data):
        lib = "/usr/local/lib/libpteidpkcs11.so"
        pkcs11 = PyKCS11.PyKCS11Lib()
        pkcs11.load(lib)
        slots = pkcs11.getSlotList()
        session = pkcs11.openSession(slots[0])

        key = session.findObjects( template=( (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION KEY"),
                                              (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                                              (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA) ))[0]
        mech = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, "")
        sig = session.sign(key, data, mech)
        ret = ''.join(chr(c) for c in sig)
        return ret

