import datetime
import io
import json
import logging
from datetime import timedelta

import requests
from fdk import response
from requests.auth import HTTPBasicAuth

import ociVault

oauth_apps = {}

def initContext(context):
    # This method takes elements from the Application Context and from OCI Vault to create the OAuth App Clients object.
    if (len(oauth_apps) < 2):
        logging.getLogger().info('Retriving details about the API and backend OAuth Apps')
        try:
            logging.getLogger().info('initContext: Initializing context')
            
            # Using ociVault
            oauth_apps['apigw'] = {'introspection_endpoint': context['idcs_introspection_endpoint'], 
                                  'client_id': context['apigw_idcs_app_client_id'], 
                                  'client_secret': ociVault.getSecret(context['apigw_idcs_app_client_secret_ocid'])}

        except Exception as ex:
            logging.getLogger().error('initContext: Failed to get config or secrets')
            print("ERROR [initContext]: Failed to get the configs", ex, flush=True)
            raise
    else:
        logging.getLogger().info('initContext: OAuth Apps already stored')

def introspectToken(access_token, introspection_endpoint, client_id, client_secret):
    # This method handles the introspection of the received auth token to IDCS.  
    payload = {'token': access_token}
    headers = {'Content-Type' : 'application/x-www-form-urlencoded;charset=UTF-8', 
               'Accept': 'application/json'}
               
    try:
        token = requests.post(introspection_endpoint, 
                              data=payload, 
                              headers=headers, 
                              auth=HTTPBasicAuth(client_id, client_secret))

    except Exception as ex:
        logging.getLogger().error("introspectToken: Failed to introspect token" + ex)
        raise

    return token.json()

def getAuthContext(token, client_apps):
    # This method populates the Auth Context that will be returned to the gateway.
    auth_context = {}

    # Calling IDCS to validate the token and retrieve the client info
    try:
        token_info = introspectToken(token[len('Bearer '):], client_apps['apigw']['introspection_endpoint'], client_apps['apigw']['client_id'], client_apps['apigw']['client_secret'])

    except Exception as ex:
            logging.getLogger().error("getAuthContext: Failed to introspect token" + ex)
            raise

    # If IDCS confirmed the token is valid and active, we can proceed to populate the auth context
    if (token_info['active'] == True):
        auth_context['active'] = True
        # auth_context['principal'] = token_info['sub']
        auth_context['expiresAt'] = (datetime.datetime.fromtimestamp(token_info['exp'])).replace(tzinfo=datetime.timezone.utc).astimezone().replace(microsecond=0).isoformat()
        # scope can be re-calculated, for use on the route Authorization policy
        auth_context['scope'] = token_info['scope']
        # context is an optional comma-delimited list of key-value pairs in JSON format to return to API Gateway, for use on the route policies
        auth_context['context'] = {'key1':'value1','key2':'value2'}

    else:
        # API Client token is not active, so we will go ahead and respond with the wwwAuthenticate header
        auth_context['active'] = False
        auth_context['wwwAuthenticate'] = 'Bearer realm=\"identity.oraclecloud.com\"'

    return(auth_context)

def handler(ctx, data: io.BytesIO=None):
    logging.getLogger().info('Entered Handler')
    initContext(dict(ctx.Config()))
      
    auth_context = {}
    try:
        gateway_auth = json.loads(data.getvalue())

        auth_context = getAuthContext(gateway_auth['token'], oauth_apps)

        if (auth_context['active']):
            logging.getLogger().info('Authorizer returning 200...')
            return response.Response(
                ctx,
                response_data=json.dumps(auth_context),
                status_code = 200,
                headers={"Content-Type": "application/json"}
                )
        else:
            logging.getLogger().info('Authorizer returning 401...')
            return response.Response(
                ctx,
                response_data=json.dumps(str(auth_context)),
                status_code = 401,
                headers={"Content-Type": "application/json"}
                )

    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

        return response.Response(
            ctx,
            response_data=json.dumps(str(auth_context)),
            status_code = 401,
            headers={"Content-Type": "application/json"}
            )

