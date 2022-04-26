
from argparse import ArgumentParser
from cryptography.fernet import Fernet


def encrypt_password(passwd: str):

    # Generate key - Keep it somewhere safe!
    key = Fernet.generate_key()

    # Instantiate fernet with generated key
    f = Fernet(key)

    # Enrpyt password and return Password & Key
    e_passwd = f.encrypt(passwd.encode())

    # Display Password & key to console
    print(f'Encrypted Password = {e_passwd.decode()}\nKey = {key.decode()}')


if __name__ == '__main__':

    # Instantiate Argument Parser
    parser = ArgumentParser()

    # Add arguments
    parser.add_argument('-p', help='Password')

    try:
        args = parser.parse_args()
        encrypt_password(args.p)
    except:
        print(
            "Usage: encrypt_password -p <password>\nReturns:\n<encrypted-password>\n<key>")
