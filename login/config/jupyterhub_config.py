# Configuration for JupyterHub
import os
import json
import requests
import globus_sdk
import configparser
from tornado import gen, web
from tornado.web import HTTPError
from oauthenticator.globus import LocalGlobusOAuthenticator


class VC3GlobusOAuthenticator(LocalGlobusOAuthenticator):
    @gen.coroutine
    def authenticate(self, handler, data=None):
        """
        Authenticate with globus.org. Globus uuids are mapped
        to vc3 usernames and used for Jupyterhub accounts.
        """
        code = handler.get_argument("code")
        redirect_uri = self.get_callback_url(self)

        client = self.globus_portal_client()
        client.oauth2_start_flow(
            redirect_uri,
            requested_scopes=' '.join(self.scope),
            refresh_tokens=self.allow_refresh_tokens
        )
        # Doing the code for token for id_token exchange
        tokens = client.oauth2_exchange_code_for_tokens(code)
        id_token = tokens.decode_id_token(client)
        globus_uuid = id_token.get('sub', None)
        vc3_username = globusvc3_map.get(globus_uuid, None)
        
        if vc3_username is None:
            raise HTTPError(
                403,
                """Your account is not authorized
                to a access this Jupyterhub."""
            )
                
        return {
            'name': vc3_username,
            'auth_state': {
                'client_id': self.client_id,
                'tokens': {
                    tok: v for tok, v in tokens.by_resource_server.items()
                    if tok not in self.exclude_tokens
                },
            }
        }


def putRedirectUri(client_id, secret, redirect_uri):
    """
    Check if VC3 headnode IP address is in the Redirect_URI
    globus app list (and add it if not).
    """
    clients_api_base_url = "/v2/api/clients"
    authorizer = globus_sdk.BasicAuthorizer(client_id, secret)
    auth_client = globus_sdk.AuthClient(client_id=client_id, authorizer=authorizer)
    res = auth_client.get("{}/{}".format(clients_api_base_url, client_id))
    redirects = res["client"]["redirect_uris"] 
    if redirect_uri not in redirects:
            redirects.append(redirect_uri)

    res = auth_client.put("{}/{}".format(clients_api_base_url, client_id), {'client': {'redirect_uris': redirects}})
    
    assert redirect_uri in res["client"]["redirect_uris"], "Failed adding Redirect_URI"

# Jupyter auth config
c = get_config()
# Enable debug mode
# c.JupyterHub.log_level = 'DEBUG'

# Jupyter generic configfile
config = configparser.ConfigParser()
config.read('/etc/.jupyterhub/jupyterhub.conf')

# Globus vc3-app client

try:
    vc3client_id = config.get('globus', 'clientid')
    vc3client_passphrase = config.get('globus', 'secret')
    jupyter_port = config.getint('jupyter', 'port')
except Exception as e:
    print('Could not get configuration. Error: {0}'.format(e))

# Use port 8080 for Jupyterhub
c.JupyterHub.ip = requests.get('https://api.ipify.org').text
c.JupyterHub.port = jupyter_port

redirect_uri = 'https://{0}:{1}/hub/oauth_callback'.format(c.JupyterHub.ip, c.JupyterHub.port)

# Check/Put Redirect_URI in app client
putRedirectUri(vc3client_id, vc3client_passphrase, redirect_uri)

# Mapfile for globus-uuid to vc3-usernames
globusMap = open("/etc/vc3/vc3-mapfile.json")
globusvc3_map = json.load(globusMap)

c.JupyterHub.authenticator_class = VC3GlobusOAuthenticator

c.JupyterHub.ssl_cert = '/etc/.jupyterhub/jupyterhub.crt'
c.JupyterHub.ssl_key = '/etc/.jupyterhub/jupyterhub.key'

c.VC3GlobusOAuthenticator.enable_auth_state = True
c.VC3GlobusOAuthenticator.oauth_callback_url = redirect_uri
c.VC3GlobusOAuthenticator.client_id = vc3client_id
c.VC3GlobusOAuthenticator.client_secret = vc3client_passphrase
c.CryptKeeper.keys = [ os.urandom(32) ]

c.VC3GlobusOAuthenticator.scope = ['profile', 'openid', 'urn:globus:auth:scope:demo-resource-server:all']
# c.Authenticator.admin_users = ['vc3-user']
# Create notebooks with shell environment
c.Spawner.cmd = '/etc/.jupyterhub/notebook_wrapper.sh'
