'''
This is a minimal implementation that accesses eTrade APIs using python.

Prerequisites:
    1. Own an eTrade brokerage account
    2. Be registered with the eTrade API (Although not mandatory, it is recommended to have set up a callback url)

How it works:
    1. Populate the following from the eTrade API: app_key and app_secret
    2. Call generate_request_code() and generate the request_token & request_token_secret
    3. Generate the URL by invoking generate_authorization_url()
       Note: If a callback url is configured with eTrade API, the verifier code will be delivered through
             the callback so that generate_access_token() can be automatically executed.
             Otherwise, the verifier code will be displayed on the webpage and generate_access_token() needs
             to be executed manually.
    4. After generate_access_token() is executed, the access_token & access_token_secret should be saved.
    5. With access_token & access_token_secret ready, various APIs can be invoked such as get_stock_price()     

Note:
    Ensure request_token, request_token_secret are preserved between steps (2) generate_request_code() 
    and (4) generate_access_token() by storing them externally (ex. a file/database)

    After obtaining access_token & access_token_secret, these can also be saved for later usage.
'''

from pip._vendor import requests
from urllib.parse import urlencode, quote_plus, unquote
import hashlib
import hmac
import collections
from xml.dom.minidom import parseString
import base64
import uuid
import time

SIGNATURE_METHOD = "HMAC-SHA1"

class ETradeReader():

    def __init__(self):

        # the following two values should be retrieved from eTrade API configurations
        self.app_key = "<get from the eTrade API configuration>"
        self.app_secret = "<get from the eTrade API configuration>"

        # the following two pairs of tokens & secrets will be populated by the code
        # IMPORTANT: the values need to be preserved between function calls (e.g. to a file/database)
        self.request_token = ""
        self.request_token_secret = ""

        self.access_token_secret = "" 
        self.access_token = "" 

        # urls
        self.oauth_base_url = "https://us.etrade.com/e/t/etws/authorize?key=" + self.app_key + "&token="
        self.access_token_base_url = "https://api.etrade.com/oauth/access_token"
        self.request_token_base_url = "https://api.etrade.com/oauth/request_token"
        self.api_base_url = "https://api.etrade.com/v1/market/quote/"
       
    '''
    Generates request_token and request_token_secret which are used in both generate_authorization_url() 
    and generate_access_token()
    '''
    def generate_request_code(self):

        url = self.request_token_base_url

        param = {
            "oauth_nonce"               : self._get_nonce(),
            "oauth_timestamp"           : self._get_timestamp(),
            "oauth_signature_method"    : SIGNATURE_METHOD,
            "oauth_consumer_key"        : self.app_key,
            "oauth_callback"            : "oob"
        }

        self.sign("GET", url, param, self.app_secret, "")
        url = url + "?" + self._urlencode_alt(param)
        data = requests.get(url)

        x = data.text.split("&")

        # IMPORTANT: these two values should be preserved to a file/database etc for later retrieval
        self.request_token = unquote(x[0].split("=")[1])
        self.request_token_secret = unquote(x[1].split("=")[1])


    '''
    Generates the authorization url for the user to manually authorize. The retrieved verifier code 
    can be used to generate_access_token()
    '''
    def generate_authorization_url(self):
        url = self.oauth_base_url + self.request_token
        print(f'please visit {url} to get a verifier code and call generate_access_token')

    '''
    Gets the access_token and access_token secret with verifier code acquired from 
    generate_authorization_url()
    '''
    def generate_access_token(self, verifier_code):

        url = self.access_token_base_url
        param = {
            "oauth_nonce"               : self._get_nonce(),
            "oauth_timestamp"           : self._get_timestamp(),
            "oauth_signature_method"    : SIGNATURE_METHOD,
            "oauth_consumer_key"        : self.app_key,
            "oauth_verifier"            : verifier_code,
            "oauth_token"               : self.request_token
        }
        self.sign("GET", url, param, self.app_secret, self.request_token_secret)

        url = url + "?" + self._urlencode_alt(param) 
        data = requests.get(url)
        x = data.text.split("&")

        # IMPORTANT: these two fiels need to be preserved to a file/database for later retrieval.
        self.access_token = unquote(x[0].split("=")[1])
        self.access_token_secret = unquote(x[1].split("=")[1])
    
    '''
    Gets the latest price of the stock using access_token and access_token_secret
    '''
    def get_stock_price(self, ticker):

        url = self.api_base_url + ticker
        param = {
            "oauth_nonce"               : self._get_nonce(),
            "oauth_timestamp"           : self._get_timestamp(),
            "oauth_signature_method"    : SIGNATURE_METHOD,
            "oauth_consumer_key"        : self.app_key,
            "oauth_token"               : self.access_token
        }
        self.sign("GET", url, param, self.app_secret, self.access_token_secret)
        
        url = url + "?" + self._urlencode_alt(param)
        data = requests.get(url)
        xml = parseString(data.text)
        d = xml.getElementsByTagName("lastPrice")[0].firstChild.data
        print(f'{ticker}: {d}')
        
    '''
    Signs the message and inserts the signature to the given param_map.
    '''
    def _sign(self, http_method, url, param_map, token_secret, token):

        ordered = collections.OrderedDict(sorted(param_map.items()))
        dict_str = urlencode(ordered)
        base_url = quote_plus(http_method) + "&" + quote_plus(url) + "&" + quote_plus(dict_str)
        key = quote_plus(token_secret) + "&" + quote_plus(token)
        hashed = hmac.new(key.encode(),
                          base_url.encode(),
                          digestmod=hashlib.sha1).digest()
        signed = quote_plus(base64.b64encode(hashed).decode())
        param_map["oauth_signature"] = signed
        return signed
        
    '''
    Utility function to generate a query string from a given map
    '''
    def _urlencode_alt (self, dict):
        return "&".join([k + "=" + v for k,v in dict.items()]) 
    
    '''
    Utility function to generate a random value
    '''
    def _get_nonce(self):
        return str(uuid.uuid1()).replace("-","")

    '''
    Utility function to generate a timestamp
    '''
    def _get_timestamp(self):
        return str(int(time.time()))

