import base64
import binascii
import os
import stat
import tempfile
from typing import Optional
from urllib.parse import parse_qs, urlparse

from Crypto.Cipher import AES
from google.api_core.client_info import ClientInfo as APICoreClientInfo
from google.api_core.exceptions import GoogleAPICallError, RetryError
from google.api_core.gapic_v1.client_info import ClientInfo as GAPIClientInfo
from google.cloud import storage, kms

from berglas.constants import METADATA_KMS_KEY, REFERENCE_PREFIX, USER_AGENT
from berglas.exceptions import AutoException


def is_reference(key: str) -> bool:
    """
    Does this key represent a berglas reference
    """
    return key.startswith(REFERENCE_PREFIX)


def _decrypt_gcm(dek: bytes, ciphertext: bytes) -> bytes:
    # TODO use some constant from crypto library instead of hardcoding here
    nonce_size = 12
    tag_size = 16
    if len(ciphertext) < nonce_size + tag_size:
        raise AutoException("malformed ciphertext")
    nonce, ciphertext, tag = ciphertext[:nonce_size], ciphertext[nonce_size:-tag_size], ciphertext[-tag_size:]
    cipher = AES.new(dek, AES.MODE_GCM, nonce=nonce)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise AutoException("failed to decrypt ciphertext")


class Client:
    storage_client: storage.Client
    kms_client: kms.KeyManagementServiceClient

    def __init__(self):
        self.storage_client = storage.Client(client_info=APICoreClientInfo(user_agent=USER_AGENT))
        self.kms_client = kms.KeyManagementServiceClient(client_info=GAPIClientInfo(user_agent=USER_AGENT))

    def _access(self, bucket_name: str, path: str, generation: Optional[int] = None) -> bytes:
        """
        Get plaintext value of the secret stored at path in bucket
        """
        blob = self.storage_client.bucket(bucket_name).get_blob(path, client=self.storage_client, generation=generation)
        if not blob:
            raise AutoException("secret object not found")

        if not blob.metadata or not blob.metadata.get(METADATA_KMS_KEY):
            raise AutoException("missing kms key in secret metadata")

        key = blob.metadata[METADATA_KMS_KEY]
        data = blob.download_as_string()
        parts = data.split(b":", maxsplit=1)
        if len(parts) < 2:
            raise AutoException("invalid ciphertext: not enough parts")

        try:
            enc_dek = base64.decodebytes(parts[0])
        except binascii.Error:
            raise AutoException("invalid ciphertext: failed to parse dek")

        try:
            ciphertext = base64.decodebytes(parts[1])
        except binascii.Error:
            raise AutoException("invalid ciphertext: failed to parse ciphertext")

        try:
            response = self.kms_client.decrypt(key, enc_dek, path.encode("UTF8"))
            dek = response.plaintext
        except (GoogleAPICallError, RetryError, ValueError):
            raise AutoException("failed to decrypt dek")

        return _decrypt_gcm(dek, ciphertext)

    def resolve(self, value: str) -> bytes:
        """
        Resolves a berglas reference value to the plain text secret
        """
        if not is_reference(value):
            raise AutoException("not a berglas reference")

        parsed = urlparse(value)
        bucket = parsed.netloc
        obj = parsed.path.lstrip("/")
        destination = parse_qs(parsed.query).get("destination", [""])[0]
        generation = int(parsed.fragment or 0)
        tmpfile = None

        if destination in ["tmpfile", "tempfile"]:
            tmpfile = tempfile.NamedTemporaryFile(prefix="berglas-", delete=False)
        elif destination:
            tmpfile = open(destination, "wb")

        plaintext = self._access(bucket, obj, generation=generation)

        if tmpfile:
            os.chmod(tmpfile.name, stat.S_IRUSR | stat.S_IWUSR)
            tmpfile.write(plaintext)
            plaintext = tmpfile.name.encode()
            tmpfile.close()

        return plaintext

    def replace(self, key: str, value: str = None) -> None:
        """
        Replace a berglas reference represented by value and update key in environment with plain text value
        :param value: if specified use this value instead of reading from os.environ
        """
        plaintext = self.resolve(value or os.environ[key])
        # don't assume UTF-8, or system encoding even
        os.environb[key.encode()] = plaintext
