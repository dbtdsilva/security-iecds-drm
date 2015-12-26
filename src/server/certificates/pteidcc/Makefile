WGET = wget --no-check-certificate

CC_CERTS = 1 2 3
CC_CERT_FILES = $(foreach n, $(CC_CERTS), Cartao-de-Cidadao-00$(n).cer)

CC_SIGN_CERTS = 1 2 3 4 5 6 7 8 9
CC_SIGN_CERT_FILES = $(foreach n, $(CC_SIGN_CERTS), EC-de-Assinatura-Digital-Qualificada-do-Cartao-de-Cidadao-000$(n).cer)

CC_AUTH_CERTS = 1 2 3 4 5 6 7 8 9
CC_AUTH_CERT_FILES = $(foreach n, $(CC_AUTH_CERTS), EC-de-Autenticacao-do-Cartao-de-Cidadao-000$(n).cer)

CC_ALL_CERT_FILES = $(CC_CERT_FILES) $(CC_SIGN_CERT_FILES) $(CC_AUTH_CERT_FILES)

all:  
	@for i in $(CC_CERT_FILES); do \
	    [ -f $$i ] || \
	    ( \
		u=`echo $$i | sed -e s/-/%20/g`; \
	    	$(WGET) https://pki.cartaodecidadao.pt/publico/certificado/cc_ec_cidadao/$$u; \
		s=`echo $$i | sed -e s/-/\ /g`; \
		mv "$$s" $$i; \
		touch newCert; \
	    ) \
	done
	#@for i in $(CC_SIGN_CERT_FILES); do \
	#    [ -f $$i ] || \
	#    ( \
	#	u=`echo $$i | sed -e s/-/%20/g`; \
	#    	$(WGET) https://pki.cartaodecidadao.pt/publico/certificado/cc_ec_cidadao_assinatura/$$u; \
	#	s=`echo $$i | sed -e s/-/\ /g`; \
	#	mv "$$s" $$i; \
	#	touch newCert; \
	#    ) \
	#done
	@for i in $(CC_AUTH_CERT_FILES); do \
	    [ -f $$i ] || \
	    ( \
		u=`echo $$i | sed -e s/-/%20/g`; \
	    	$(WGET) https://pki.cartaodecidadao.pt/publico/certificado/cc_ec_cidadao_autenticacao/$$u; \
		s=`echo $$i | sed -e s/-/\ /g`; \
		mv "$$s" $$i; \
		touch newCert; \
	    ) \
	done
	@for i in $(CC_AUTH_CERT_FILES); do\
		openssl x509 -in $$i -inform DER -out $$i.pem -outform PEM; \
	done
	@for i in $(CC_CERT_FILES); do\
		openssl x509 -in $$i -inform DER -out $$i.pem -outform PEM; \
	done
	#cat *.pem > PTEID_CA_Bundle.crt
	echo "All Done"


clean:
	@rm -f *.cer
	@rm -f *.pem

