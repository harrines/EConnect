from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
import datetime
from datetime import timezone

def generate_certificate():
    # Generate a key pair
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # Create a certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"3.110.162.80"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(timezone.utc)
    ).not_valid_after(
        # Certificate valid for 365 days
        datetime.datetime.now(timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"3.110.162.80"),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256(), default_backend())

    # Save the key and certificate to files
    with open('key.pem', 'wb') as key_file:
        key_file.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open('cert.pem', 'wb') as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

if __name__ == '__main__':
    generate_certificate()
    print("SSL certificates generated successfully.")
