from google.cloud import secretmanager


def access_secret_version(project_id, secret_id, version_id="latest"):
    """Access the payload for the given secret version if one exists.

    The version can be a version number as a string (e.g. "5") or an
    alias (e.g. "latest").

    Args:
        project_id (str): Project ID of project regisered on GCP.
        secret_id (str): Secret ID of secret in Secret Manager.
        version_id (str) Version ID of secret. Defaults to 'latest'.

    """
    client = secretmanager.SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_id, version_id)
    response = client.access_secret_version(name)
    payload = response.payload.data.decode("UTF-8")
    return payload
