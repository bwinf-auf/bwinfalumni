import hashlib
import base64
from django.contrib.auth.hashers import BasePasswordHasher

class MiaPlazaPasswordHasher(BasePasswordHasher):
    """
    Implements the hasher for the old MiaPlaza-style passwords, which is
        base64 . sha1 . base64 . sha1
    """

    algorithm = "miaplaza"

    def encode(self, password, salt, iterations=None):
        assert password is not None
        hash = hashlib.sha1(base64.b64encode(hashlib.sha1(password).digest()))
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%s$%s" % (self.algorithm, hash)

    def verify(self, password, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, None)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('hash'), mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        pass