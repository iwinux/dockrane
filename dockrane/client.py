from docker import from_env


def get_docker_client(api_version='auto', **client_args):
    return from_env(version=api_version, **client_args)
