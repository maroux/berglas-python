import os

from berglas import VERSION


CONTINUE_ON_ERROR = os.environ.get("BERGLAS_CONTINUE_ON_ERROR", "false").lower() == "true"
REFERENCE_PREFIX = "berglas://"
USER_AGENT = f"berglas/{VERSION} (https://github.com/maroux/berglas)"
METADATA_KMS_KEY = "berglas-kms-key"
