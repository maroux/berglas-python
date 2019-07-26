import logging
from typing import Dict

from berglas.constants import CONTINUE_ON_ERROR
from berglas.exceptions import AutoException
from berglas.resolver import Client, is_reference
from berglas.runtime import RuntimeEnv, detect_runtime_environment


def _handle_error(e: BaseException) -> None:
    logging.exception(e.args[0])
    if not CONTINUE_ON_ERROR:
        raise


def _filter_refs(runtime_env: RuntimeEnv) -> Dict[str, str]:
    env_vars = runtime_env.get_env()
    return {k: v for k, v in env_vars.items() if is_reference(v)}


def auto() -> None:
    """
    Automatically resolve and update environment with plain text secrets
    """
    logging.debug("automatically resolving all berglas references from environment")
    try:
        runtime_env = detect_runtime_environment()

        env_var_refs = _filter_refs(runtime_env)
        if not env_var_refs:
            logging.warning("berglas auto was included, but no secrets were found in the environment")
            return

        client = Client()
        for k, v in env_var_refs.items():
            client.replace(k, v)
    except AutoException as e:
        _handle_error(e)
    except BaseException as e:
        _handle_error(e)


if __name__ == "berglas.auto":
    auto()
