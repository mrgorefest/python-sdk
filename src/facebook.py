from google.appengine.api import urlfetch

# Find a JSON parser
try:
    import json
    _parse_json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _parse_json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _parse_json = lambda s: simplejson.loads(s)
        
def isset(var): #TODO: change with this: http://www.php2python.com/wiki/function.isset/
    try:
        (lambda x: x)(var)
    except NameError:
        return False
    else:
        return True
def is_array(var):
    return isinstance(var, (list, tuple))
def is_string(obj):
    return isinstance(obj, basestring)
        
        
class FacebookApiException(Exception):
    __result = None
    def __init__(self, result):
        self.result = result
        code = result['error_code'] if isset(result['error_code']) else 0
        if isset(result['error_description']):
            msg = result['error_description']
        elif (isset(result['error']) and is_array(result['error'])):
            msg = result['error']['message']
        elif isset(result['error_msg']):
            msg = result['error_msg']
        else:
            msg = 'Unknown Error. Check getResult()'
    def getResult(self):
        return self.result
    def getType(self):
        if isset(self.result['error']):
            error = self.result['error']
            if is_string(error):
            # OAuth 2.0 Draft 10 style
                return error
            elif is_array(error):
            # OAuth 2.0 Draft 00 style
                if isset(error['type']):
                    return error['type']

        return 'Exception'
    def toString(self):
        str = self.getType() + ': '
        if self.code != 0:
            str += self.code + ': '
        return str + self.message

class Facebook:   
    VERSION = '2.1.2'
    '''
      /**
   * Default options for curl.
   */
  public static CURL_OPTS = array(
    CURLOPT_CONNECTTIMEOUT => 10,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 60,
    CURLOPT_USERAGENT      => 'facebook-php-2.0',
  )

  /**
       * List of query parameters that get automatically dropped when rebuilding
       * the current URL.
   '''
    DROP_QUERY_PARAMS = [
                         'session',
                         'signed_request',
                        ]

    '''
       * Maps aliases to Facebook domains.
   '''
    DOMAIN_MAP = {
                 'api' : 'https://api.facebook.com/',
                 'api_read' : 'https://api-read.facebook.com/',
                 'graph'    : 'https://graph.facebook.com/',
                 'www'      : 'https://www.facebook.com/',
                 }

    '''
       * The Application ID.
   '''
    appId = None

    '''
       * The Application API Secret.
   '''
    apiSecret = None

    '''
       * The active user session, if one is available.
  '''
    session = None

    '''
       * The data from the signed_request token.
   '''
    signedRequest = None

    '''
       * Indicates that we already loaded the session as best as we could.
   '''
    sessionLoaded = False

    '''
       * Indicates if Cookie support should be enabled.
   '''
    cookieSupport = False

    '''
       * Base domain for the Cookie.
   '''
    baseDomain = ''

    '''
       * Indicates if the CURL based @ syntax for file uploads is enabled.
   '''
    fileUploadSupport = False

    '''
       * Initialize a Facebook Application.
       *
       * The configuration:
       * - appId: the application ID
       * - secret: the application secret
       * - cookie: (optional) boolean true to enable cookie support
       * - domain: (optional) domain for the cookie
       * - fileUpload: (optional) boolean indicating if file uploads are enabled
       *
       * @param Array config the application configuration
       */
   '''
    def __init__(self, config):
        self.setAppId(config['appId'])
        self.setApiSecret(config['secret'])
        if isset(config['cookie']):
            self.setCookieSupport(config['cookie'])
        if isset(config['domain']):
            self.setBaseDomain(config['domain'])
        if isset(config['fileUpload']):
            self.setFileUploadSupport(config['fileUpload'])
        
    '''
       * Set the Application ID.
       *
       * @param String appId the Application ID
    '''
    def setAppId(self, appId):
        self.appId = appId
        return self
    
    '''
       * Get the Application ID.
       *
       * @return String the Application ID
    '''
    def getAppId(self):
        return self.appId

    '''
       * Set the API Secret.
       *
       * @param String appId the API Secret
    '''
    def setApiSecret(self, apiSecret):
        self.apiSecret = apiSecret
        return self

    '''
       * Get the API Secret.
       *
       * @return String the API Secret
    '''
    def getApiSecret(self):
        return self.apiSecret
    
    '''
       * Set the Cookie Support status.
       *
       * @param Boolean cookieSupport the Cookie Support status
    '''
    def setCookieSupport(self, cookieSupport):
        self.cookieSupport = cookieSupport
        return self

    '''
       * Get the Cookie Support status.
       *
       * @return Boolean the Cookie Support status
    '''
    def useCookieSupport(self):
        return self.cookieSupport
    
    '''
       * Set the base domain for the Cookie.
       *
       * @param String domain the base domain
    '''
    def setBaseDomain(self, domain):
        self.baseDomain = domain
        return self

    '''
       * Get the base domain for the Cookie.
       *
       * @return String the base domain
    '''
    def getBaseDomain(self):
        return self.baseDomain

    '''
       * Set the file upload support status.
       *
       * @param String domain the base domain
    '''
    def setFileUploadSupport(self, fileUploadSupport):
        self.fileUploadSupport = fileUploadSupport
        return self
    
    '''
       * Get the file upload support status.
       *
       * @return String the base domain
    '''
    def useFileUploadSupport(self):
        return self.fileUploadSupport

    '''
       * Get the data from a signed_request token
       *
       * @return String the base domain
    '''
    def getSignedRequest(self):
        if not self.signedRequest:
            if isset($_REQUEST['signed_request']): #TODO: $_REQUEST
                self.signedRequest = self.parseSignedRequest($_REQUEST['signed_request'])  #TODO: $_REQUEST
        return self.signedRequest

    '''
        * Set the Session.
        *
        * @param Array session the session
        * @param Boolean write_cookie indicate if a cookie should be written. this
        * value is ignored if cookie support has been disabled.
    '''
    def setSession(self, session=None, write_cookie=True):
        session = self.validateSessionObject(session)
        self.sessionLoaded = true
        self.session = session
        if (write_cookie):
            self.setCookieFromSession(session)
        return self