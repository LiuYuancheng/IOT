#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        x509cReader.py
#
# Purpose:     This function is used to read the x509 certificate and get the
#              public key to encrypt a message then use the private key file 
#              to decrypt the messsage.
#
# Author:      Yuancheng Liu
#
# Created:     2019/04/30
# Copyright:   YC
# License:     YC
#------------------------------------------------------------------------
import os
import sys
import ssl
import chilkat
from OpenSSL import crypto


dirpath = os.getcwd()
print("Current working directory is : %s" %dirpath)

CER_PATH = "".join([dirpath, "\\firmwSign\\publickey.cer"])
PRI_PATH = "".join([dirpath, "\\firmwSign\\privatekey.pem"])
PLAINTEXT = "Encrypting and decrypting should be easy!"
ENCODE_MODE = 'hex'

#------------------------------------------------------------------------
# use SSL to check the file
print("1. OpenSSL: Verify the certifcate file by SSL lib:")
cert_file_name = os.path.join(os.path.dirname(__file__), CER_PATH)
try:
    cert_dict = ssl._ssl._test_decode_cert(cert_file_name)
    print(cert_dict)
except Exception as e:
    print("Error decoding certificate: {:}".format(e))
print('Done.')

# user Pyopenssl to check the certificate.
with open(CER_PATH, 'rb') as f:
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
pubKeyObject = cert.get_pubkey()
pubKeyString = crypto.dump_publickey(crypto.FILETYPE_PEM,pubKeyObject)
print (pubKeyString)
print("---------------------------------------------------")

#------------------------------------------------------------------------
# Use chilkat to parse the certificate file. 
print('2. Chilkat: Load the certificate and get public key.')
# get the public key
cert = chilkat.CkCert()
success = cert.LoadFromFile(CER_PATH)
if not success:
    print(cert.lastErrorText())
    sys.exit()
print(" - SubjectDN:" + cert.subjectDN())
print(" - Common Name:" + cert.subjectCN())
print(" - Issuer Common Name:" + cert.issuerCN())
print(" - Serial Number:" + cert.serialNumber())    
pubKey = cert.ExportPublicKey()
if not cert.get_LastMethodSuccess():
    print(cert.lastErrorText())
    sys.exit()
print(" - Key type = " + pubKey.keyType())
# XML format public key
xml = chilkat.CkXml()
xml.LoadXml(pubKey.getXml())
print("Public Key XML:\n"+xml.getXml())
# base64 format public key
modulus = xml.getChildContent("Modulus")
print("base64 modulus:\n"+modulus)
# Hex formate publick key
binDat = chilkat.CkBinData()
binDat.Clear()
binDat.AppendEncoded(modulus,"base64")
hexModulus = binDat.getEncoded(ENCODE_MODE)
print("hex modulus:\n"+hexModulus)
print('Done')
print("---------------------------------------------------")

#------------------------------------------------------------------------
# Encrypt the message with public key.
print('3. Encrypt the message with public key')
rsaEncryptor = chilkat.CkRsa()
# must do the unlocak process ? 
if not rsaEncryptor.UnlockComponent("Anything for 30-day trial"):
    print("RSA component unlock failed")
    sys.exit()
rsaEncryptor.put_EncodingMode(ENCODE_MODE)
# Encrypt 
success = rsaEncryptor.ImportPublicKey(pubKey.getXml())
print (success)
usePrivateKey = False
encryptedStr = rsaEncryptor.encryptStringENC(PLAINTEXT, usePrivateKey)
print("Encrypted message:\n"+ encryptedStr)
print('Done')
print("---------------------------------------------------")

#------------------------------------------------------------------------
# Decript the string and get the message. 
print("4. Decrypt the message to plain text")
# Decript
rsaDecryptor = chilkat.CkRsa()
if not rsaDecryptor.UnlockComponent("Anything for 30-day trial"):
    print("RSA component unlock failed")
    sys.exit()
privKey = chilkat.CkPrivateKey()
success = privKey.LoadPemFile(PRI_PATH)
if not success:
    print(privKey.lastErrorText())
    sys.exit()
print("Private Key from DER: \n" + privKey.getXml())
rsaDecryptor.put_EncodingMode(ENCODE_MODE)
success = rsaDecryptor.ImportPrivateKey(privKey.getXml())
if not success:
    print(rsaDecryptor.lastErrorText())
    sys.exit()
usePrivateKey = True
decryptedStr = rsaDecryptor.decryptStringENC(encryptedStr,usePrivateKey)
print("Decripted message: \n" + decryptedStr)
print('Done')
