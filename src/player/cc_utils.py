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

        der = ''.join(chr(c) for c in objs[0].to_dict()['CKA_VALUE'])
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, der)
        pem = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509)
        return ("Success", pem)

    def get_subca_common_names(self, pin):
        subca = self.get_cert('AUTHENTICATION SUB CA', pin)
        subca_cn = None
        for (name, value) in subca.get_subject().get_components():
            if name == 'CN':
                subca_cn = value
        rootca = self.get_cert('ROOT CA', pin)
        rootca_cn = None
        for (name, value) in rootca.get_subject().get_components():
            if name == 'CN':
                rootca_cn = value
        return (subca_cn, rootca_cn)

    # Signs given data
    def sign(self, data, pin):
        lib = "/usr/local/lib/libpteidpkcs11.so"
        pkcs11 = PyKCS11.PyKCS11Lib()
        pkcs11.load(lib)
        slots = pkcs11.getSlotList()
        session = pkcs11.openSession(slots[0])
        #print "logging in"
        try:
            session.login(pin=pin)
        except:
            return None

        key = session.findObjects( template=( (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION KEY"),
                                              (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                                              (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA) ))[0]
        #print key
        #print "logged in"
        mech = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, "")

        sig = session.sign(key, data, mech)
        ret = ''.join(chr(c) for c in sig)
        #print "ORIGINAL SIGNATURE: " + ret
        return ret
if __name__ == '__main__':
    pin = input("Insert pin: ")
    print pin
    cc = cc_utils()
    (status, cert) = cc.get_cert("CITIZEN AUTHENTICATION CERTIFICATE", str(pin))
    var = "-----BEGIN CERTIFICATE-----\n\
MIIHIDCCBgigAwIBAgIIBMxptU9FAMswDQYJKoZIhvcNAQEFBQAwfDELMAkGA1UE\n\
BhMCUFQxHDAaBgNVBAoME0NhcnTDo28gZGUgQ2lkYWTDo28xFDASBgNVBAsMC3N1\n\
YkVDRXN0YWRvMTkwNwYDVQQDDDBFQyBkZSBBdXRlbnRpY2HDp8OjbyBkbyBDYXJ0\n\
w6NvIGRlIENpZGFkw6NvIDAwMDYwHhcNMTIwNzIzMTIwNTA5WhcNMTcwNzIyMjMw\n\
MDAwWjCB3jELMAkGA1UEBhMCUFQxHDAaBgNVBAoME0NhcnTDo28gZGUgQ2lkYWTD\n\
o28xHDAaBgNVBAsME0NpZGFkw6NvIFBvcnR1Z3XDqnMxIzAhBgNVBAsMGkF1dGVu\n\
dGljYcOnw6NvIGRvIENpZGFkw6NvMSAwHgYDVQQEDBdCQVNUT1MgVEFWQVJFUyBE\n\
QSBTSUxWQTEOMAwGA1UEKgwFRElPR08xFDASBgNVBAUTC0JJMTQxMzc5NTg4MSYw\n\
JAYDVQQDDB1ESU9HTyBCQVNUT1MgVEFWQVJFUyBEQSBTSUxWQTCBnzANBgkqhkiG\n\
9w0BAQEFAAOBjQAwgYkCgYEAvCv/AtuSLZ0F/8kzH2cs7VyjrCP/m1793s2gUMqA\n\
M/6nkUvuuwXUmDrQiD/ZtfYJQmM8HOM2tsWsJpvlI3zgRshDyZ61o7ceMtr42hRr\n\
xLpd/ZT2qHe7xme5w9VntBW+DfRb0BYdvBnCDtbd90Bxp0dY4Tg4QHZ/3HRqGDwJ\n\
HM0CAwEAAaOCA8UwggPBMAwGA1UdEwEB/wQCMAAwDgYDVR0PAQH/BAQDAgOIMB0G\n\
A1UdDgQWBBTr0ArBcuyPcg+vtxC4Ku5utHxGNjAfBgNVHSMEGDAWgBSRwpLGRdqL\n\
2P1/HQ6IaNzeMRO29DCCAfUGA1UdIASCAewwggHoMIHyBghghGwBAQECFDCB5TAo\n\
BggrBgEFBQcCARYcaHR0cDovL3d3dy5zY2VlLmdvdi5wdC9wY2VydDCBuAYIKwYB\n\
BQUHAgIwgasegagATwAgAGMAZQByAHQAaQBmAGkAYwBhAGQAbwAgAGUAbQBpAHQA\n\
aQBkAG8AIABzAGUAZwB1AG4AZABvACAAZQBzAHQAYQAgAHAAbwBsAO0AdABpAGMA\n\
YQAgAOkAIAB1AHQAaQBsAGkAegBhAGQAbwAgAHAAYQByAGEAIABhAHUAdABlAG4A\n\
dABpAGMAYQDnAOMAbwAgAGQAbwAgAEMAaQBkAGEAZADjAG8weAYLYIRsAQEBAgQC\n\
AAcwaTBnBggrBgEFBQcCARZbaHR0cDovL3BraS5jYXJ0YW9kZWNpZGFkYW8ucHQv\n\
cHVibGljby9wb2xpdGljYXMvZHBjL2NjX3N1Yi1lY19jaWRhZGFvX2F1dGVudGlj\n\
YWNhb19kcGMuaHRtbDB3BgxghGwBAQECBAIAAQEwZzBlBggrBgEFBQcCARZZaHR0\n\
cDovL3BraS5jYXJ0YW9kZWNpZGFkYW8ucHQvcHVibGljby9wb2xpdGljYXMvcGMv\n\
Y2Nfc3ViLWVjX2NpZGFkYW9fYXV0ZW50aWNhY2FvX3BjLmh0bWwwawYDVR0fBGQw\n\
YjBgoF6gXIZaaHR0cDovL3BraS5jYXJ0YW9kZWNpZGFkYW8ucHQvcHVibGljby9s\n\
cmMvY2Nfc3ViLWVjX2NpZGFkYW9fYXV0ZW50aWNhY2FvX2NybDAwMDZfcDAwMDIu\n\
Y3JsMHEGA1UdLgRqMGgwZqBkoGKGYGh0dHA6Ly9wa2kuY2FydGFvZGVjaWRhZGFv\n\
LnB0L3B1YmxpY28vbHJjL2NjX3N1Yi1lY19jaWRhZGFvX2F1dGVudGljYWNhb19j\n\
cmwwMDA2X2RlbHRhX3AwMDAyLmNybDBLBggrBgEFBQcBAQQ/MD0wOwYIKwYBBQUH\n\
MAGGL2h0dHA6Ly9vY3NwLmF1Yy5jYXJ0YW9kZWNpZGFkYW8ucHQvcHVibGljby9v\n\
Y3NwMBEGCWCGSAGG+EIBAQQEAwIAoDAoBgNVHQkEITAfMB0GCCsGAQUFBwkBMREY\n\
DzE5OTIwNDA4MTIwMDAwWjANBgkqhkiG9w0BAQUFAAOCAQEAYZ7e2GdGofWmcNNI\n\
MFfTo366xObdHNCny2jkvXXbKGNEHwN31PR3MW4z+TyVZ/IiL8FZL/p47RysBn+i\n\
RGl7K7igB6YMYkfOA359GsdoyM+UcTwoRhozmyxDxGEU9kkNLRToJMR59XLZg5e2\n\
w+t0W+ryoudPHo6db4whph4eUZo08y4x6almLxiLxy6xzBo/Z/tUlAjpck8q+mV2\n\
SoV9sDuLW/iYqhmaTXTPu9YS4vUTQBDs7Qm9rwpbgE/PZC2B09ZZfQEyPLQ7EnPt\n\
XNBaJVCVRRBN0VI19+n1pJh3kHoNya2Lbg+oOzfUiclOZDmtdiNCrQQQoFa40+x9\n\
6UhOMw==\n\
-----END CERTIFICATE-----\n\
"
    print var, len(var)
    if status != "Success":
        print status
    else:
        print cert, len(cert)
