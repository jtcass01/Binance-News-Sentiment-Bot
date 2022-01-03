"""Cipher.py:"""
from __future__ import annotations

__author__ = "Jacob Taylor Casasdy"
__email__ = "jacobtaylorcassady@outlook.com"

from unittest import TestCase, TestResult, TestSuite
from abc import ABC, abstractmethod
from os.path import join, dirname, isfile, sep
from os import listdir
from yaml import load, FullLoader, safe_load
from argparse import ArgumentParser
from random import shuffle
from typing import Union, Dict, Any

LOCK_AND_KEY_DIRECTORY = join(dirname(__file__), "..", "lock_and_key")
RESOURCE_DIRECTORY = join(dirname(__file__), "..", "resources")
CIPHER_RESOURCE = join(LOCK_AND_KEY_DIRECTORY, "cipher.yaml")
assert isfile(CIPHER_RESOURCE), "CIPHER resource file unable to be found."

DATA_KEY_BASE = "0123456789AaBbCcDdEeFfGgHhJjKkLlMmNnOoPpQqRrSsTtUuVvXxYyZz \n{}[]()<>,.!@#$%^&*_+-=/\\\'\""
FILE_NAME_KEY_BASE = "0123456789AaBbCcDdEeFfGgHhJjKkLlMmNnOoPpQqRrSsTtUuVvXxYyZz "


class Cipher(ABC):
    """[summary]"""

    @abstractmethod
    def encode(self, message: str) -> str:
        """[summary]
        Args:
            message (str): [description]
        Returns:
            str: [description]"""
        pass

    @abstractmethod
    def decode(self, message: str) -> str:
        """[summary]
        Args:
            message (str): [description]
        Returns:
            str: [description]"""
        pass

    @staticmethod
    def generate_random_key(key_base: str) -> str:
        """[summary]
        Args:
            key_base (str): [description]
        Returns:
            str: [description]"""
        key_list = [char for char in key_base]
        shuffle(key_list)
        return "".join(key_list)

    def decode_file(self, file_path: str) -> None:
        """[summary]
        Args:
            file_path (str): [description]"""
        with open(file_path, "r") as file:
            file_data = file.read()

        file_name = file_path.split(sep=sep)[-1]

        decoded_data = self.decode(message=file_data)
        decoded_file_name = self.decode(message=file_name)
        decoded_file_path = join(RESOURCE_DIRECTORY, decoded_file_name)

        with open(decoded_file_path, "w+") as encoded_file:
            encoded_file.write(decoded_data)

    def load_encoded_file(self, file_directory: str, file_name) -> Dict[str, Any]:
        """[summary]
        Args:
            file_directory (str): [description]
            file_name ([type]): [description]
        Returns:
            str: [description]"""
        encoded_key_file_name = self.encode(file_name)

        with open(join(file_directory, encoded_key_file_name), 
                  "r") as encoded_key_file:
            encoded_key_file_data = encoded_key_file.read()

        return safe_load(self.decode(encoded_key_file_data))


class VigenereCipher(Cipher):
    """First described by Italian Cryptologist Giovan Battista Bellaso in 1553"""

    def __init__(self, key: Union[str, None] = None, alphabet: Union[str, None] = None):
        """[summary]
        Args:
            key (str): [description]
            alphabet (str): [description]"""
        self.key = key
        self.alphabet = alphabet

    def encode(self, message: str) -> str:
        """[summary]
        Args:
            message (str): [description]
        Returns:
            str: [description]"""
        result = ""
        stretched_key = VigenereCipher.get_stretched_key(key=self.key, message_length=len(message))

        for character_index, character in enumerate(message):
            if self.alphabet.find(character) != -1:
                result += VigenereCipher.shift_char(alphabet=self.alphabet, character=character, 
                                                    shift_char=stretched_key[character_index])
            else:
                result += message[character_index]
        
        return result

    def decode(self, message: str) -> str:
        """[summary]
        Args:
            message (str): [description]
        Returns:
            str: [description]"""
        result = ""
        stretched_key = VigenereCipher.get_stretched_key(key=self.key, message_length=len(message))

        for character_index, character in enumerate(message):
            if self.alphabet.find(character) != -1:
                result += VigenereCipher.deshift_char(alphabet=self.alphabet,
                                                      character=character,
                                                      shift_char=stretched_key[character_index])
            else:
                result += character
        return result

    @staticmethod
    def shift_char(alphabet: str, character: str, shift_char: str) -> str:
        """[summary]
        Args:
            alphabet (str): [description]
            character (str): [description]
            shift_char (str): [description]
        Returns:
            str: [description]"""
        shift = alphabet.find(shift_char)
        shifted_value = alphabet.find(character) + shift

        if shifted_value >= len(alphabet):
            shifted_value -= len(alphabet)

        return alphabet[shifted_value]

    @staticmethod
    def deshift_char(alphabet: str, character: str, shift_char: str) -> str:
        """[summary]
        Args:
            alphabet (str): [description]
            character (str): [description]
            shift_char (str): [description]
        Returns:
            str: [description]"""
        shift = alphabet.find(shift_char)
        shifted_value = alphabet.find(character) - shift

        if shifted_value < 0:
            shifted_value += len(alphabet)
        
        return alphabet[shifted_value]

    @staticmethod
    def get_stretched_key(key: str, message_length: int) -> str:
        """[summary]
        Args:
            message_length (int): [description]
        Returns:
            str: [description]"""
        stretched_key: str = ""

        while len(stretched_key) <= message_length:
            stretched_key += key

        return stretched_key[:message_length]




class Test_VigenereCipher(TestCase):
    """[summary]"""

    def test_encode_and_decode(self):
        test_message = "Hello World."

        test_cipher = VigenereCipher(key=Cipher.generate_random_key(key_base=DATA_KEY_BASE), alphabet=Cipher.generate_random_key(key_base=DATA_KEY_BASE))

        encoded_message = test_cipher.encode(message=test_message)

        decoded_message = test_cipher.decode(message=encoded_message)

        assert test_message == decoded_message


def load_resource(file_name_cipher: Cipher, data_cipher: Cipher, resource_file_name: str) -> Dict[str, Any]:
    """[summary]
    Args:
        resource_file_name (str): [description]
    Returns:
        Dict[str, Any]: [description]"""
    encoded_resource_file_name = file_name_cipher.encode(resource_file_name)

    with open(join(RESOURCE_DIRECTORY, encoded_resource_file_name), "r") as encoded_resource_file:
        encoded_resource_data = encoded_resource_file.read()

    return safe_load(data_cipher.decode(encoded_resource_data))


def initialize_lock_and_key_ciphers() -> Dict[str, VigenereCipher]:
    """[summary]
    Returns:
        Dict[VigenereCipher]: [description]"""
    ciphers = {}

    with open(CIPHER_RESOURCE, "r") as cipher_resource_file:
        cipher_data = load(cipher_resource_file, Loader=FullLoader)

    for cipher_key_name, cipher_keys in cipher_data.items():
        ciphers[cipher_key_name] = VigenereCipher(key=cipher_keys['key'], alphabet=cipher_keys['alphabet'])

    return ciphers


if __name__ == "__main__":
    argument_parser = ArgumentParser()
    argument_parser.add_argument("-t", "--test", type=bool, required=False, default=False,
                                 help="If true, performs unit tests for the cipher")
    argument_parser.add_argument("-ef", "--encodeFile", type=str, required=False, default=None, action="store")
    argument_parser.add_argument("-df", "--decodeFile", type=str, required=False, default=None, action="store")
    argument_parser.add_argument("-er", "--encodeResources", type=bool, required=False, default=False, action="store")
    argument_parser.add_argument("-dr", "--decodeResources", type=bool, required=False, default=False, action="store")
    argument_parser.add_argument("-gk", "--generateKey", type=str, required=False, default=None, action="store")
    argument_parser.add_argument("-gdk", "--generateDataKey", type=bool, required=False, default=False, action="store")
    argument_parser.add_argument("-gfk", "--generateFileKey", type=bool, required=False, default=False, action="store")
    arguments = argument_parser.parse_args()

    if arguments.test:
        print("Running unittests...")
        test_result = TestResult()
        unit_test_suite = TestSuite()
        unit_test_suite.addTests(tests= [Test_VigenereCipher.test_encode_and_decode])
        unit_test_suite.run(test_result)
        print("Unittest error count: ", len(test_result.errors))
    elif arguments.encodeFile is not None:
        pass
    elif arguments.decodeFile is not None:
        pass
    elif arguments.encodeResources:
        files_to_encode = [file for file in listdir(RESOURCE_DIRECTORY) if isfile(join(RESOURCE_DIRECTORY, file)) and ".json" or ".csv" in file]
        ciphers: Dict[str, VigenereCipher] = initialize_lock_and_key_ciphers()
        for file_name in files_to_encode:
            encoded_file_name = ciphers['file_name'].encode(file_name)

            with open(join(RESOURCE_DIRECTORY, file_name), "r") as decoded_file:
                encoded_file_data = ciphers['data'].encode(decoded_file.read())
            
            with open(join(RESOURCE_DIRECTORY, encoded_file_name), "w+") as encoded_file:
                encoded_file.write(encoded_file_data)
    elif arguments.decodeResources:
        files_to_decode = [file for file in listdir(RESOURCE_DIRECTORY) if isfile(join(RESOURCE_DIRECTORY, file)) and (".json" or ".csv" not in file) and file is not CIPHER_RESOURCE]
        ciphers = initialize_lock_and_key_ciphers()
        for file_name in files_to_decode:
            encoded_file_name = ciphers['file_name'].decode(file_name)

            with open(join(RESOURCE_DIRECTORY, file_name), "r") as encoded_file:
                decoded_file_data = ciphers['data'].decode(encoded_file.read())
            
            with open(join(RESOURCE_DIRECTORY, encoded_file_name), "w+") as decoded_file:
                decoded_file.write(decoded_file_data)
    elif arguments.generateKey is not None:
        generated_key = Cipher.generate_random_key(key_base=arguments.generateKey)
        print("generated_key: ", repr(generated_key))
    elif arguments.generateDataKey:
        generated_key = Cipher.generate_random_key(key_base=DATA_KEY_BASE)
        print("generated data key: ", repr(generated_key))
    elif arguments.generateFileKey:
        generated_key = Cipher.generate_random_key(key_base=FILE_NAME_KEY_BASE)
        print("generated file key: ", repr(generated_key))