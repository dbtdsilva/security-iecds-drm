import M2Crypto
import sys
import PyKCS11
from M2Crypto import X509
import OpenSSL
from base64 import b64encode

class cc_utils():
    def get_cert(self, certLabel, pin):
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
            print session
        except:
            print "Session opening failed", str(sys.exc_info()[1])
            return ("Failed to open citizen card!", None)

        try:
            session.login(pin=pin)
        except:
            print "Login failed", str(sys.exc_info()[1])
            return ("Incorrect pin code!", None)

        objs = session.findObjects(template=(
            (PyKCS11.CKA_LABEL, certLabel),
            (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE)))

        try:
            session.logout()
        except:
            print "Logout failed"

        #print objs
        der = ''.join(chr(c) for c in objs[0].to_dict()['CKA_VALUE'])
        der_format = X509.load_cert_string(der, X509.FORMAT_DER)
        #return X509.load_cert_string(der, X509.FORMAT_DER)
        file_type=OpenSSL.crypto.FILETYPE_ASN1
        x509 = OpenSSL.crypto.load_certificate(file_type, der)
        return (status, OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509))

if __name__ == '__main__':
    pin = input("Insert pin: ")
    print pin
    cc = cc_utils()
    (status, cert) = cc.get_cert("CITIZEN AUTHENTICATION CERTIFICATE", str(pin))

    if status != "Success!":
        print status
    else:
        print cert
