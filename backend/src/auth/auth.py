import json
from functools import wraps
from urllib.request import urlopen
from flask import request
from jose import jwt

AUTH0_DOMAIN = 'martinium3.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://coffeeshop.com'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():

    authorize = request.headers.get('Authorization', None)

    if not authorize:
        raise AuthError({
            'code': 'Authorization Header Missing',
            'description': 'Authorization Header is expected'
        }, 401)

    authorize_token_list = authorize.split()

    if len(authorize_token_list) == 1:
        raise AuthError({
            'code': 'Invalid Header',
            'description': 'Token Not Found'
        }, 401)

    elif len(authorize_token_list) > 2:
        raise AuthError({
            'code': 'Invalid Header',
            'description': 'Authorization Header Malformed'
        }, 401)

    elif authorize_token_list[0].lower() != 'bearer':
        raise AuthError({
            'code': 'Invalid Header',
            'description': 'Authorization Header Must start with "Bearer". '
        }, 401)

    else:
        token = authorize_token_list[1]

    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        print("Permissions not in payload")
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'permissions not included in JWT'
        }, 403)

    if permission not in payload['permissions']:
        print(f'The passed permission <{permission}> is not in the payload')
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission Not Found'
        }, 403)

    return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    # Verify The JWT with Auth0
    json_url_string = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    # Get The JSON Web Key Set
    jw_key_set = json.loads(json_url_string.read())

    # Get The Unverified Header
    to_be_verified_header = jwt.get_unverified_header(token)

    # RSA Public Key To Verify The Digital Signature
    rsa_pub_key = {}

    if 'kid' not in to_be_verified_header:
        raise AuthError({
            'code': 'Invalid Header',
            'description': 'Authorization Header Malformed'
        }, 401)

    for key in jw_key_set['keys']:
        if key['kid'] == to_be_verified_header['kid']:
            rsa_pub_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_pub_key:
        try:
            payload = jwt.decode(
                token,
                rsa_pub_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'Incorrect Claims',
                'description': 'Incorrect Claims. Please check the audience and the issuer'
            }, 401)

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'Token Expired',
                'description': 'Expired Token'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'Invalid header',
                'description': 'Unable to parse authentication token'
            }, 403)

    raise AuthError({
        'code': 'Invalid header',
        'description': 'Unable to find appropriate key'
    }, 403)


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            tok = get_token_auth_header()
            payload = verify_decode_jwt(tok)
            res = check_permissions(permission, payload)
            print(f'Permission checked, result: {res}')
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
