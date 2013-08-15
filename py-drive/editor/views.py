from datetime import datetime, timedelta

from django import http
from django.conf import settings
from django.template.response import TemplateResponse

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.appengine import StorageByKeyName
from oauth2client.appengine import simplejson as json

from apiclient.discovery import build
from apiclient.http import MediaInMemoryUpload

import httplib2

from .models import Credentials

def CreateService (service, version, creds):
  http2 = httplib2.Http()
  creds.authorize(http2)
  return build(service, version, http=http2)
  
class DriveAuth (object):
  def __init__ (self, request):
    self.request = request
    self.userid = None
    
  def CreateOAuthFlow (self):
    uri = 'http://' + self.request.get_host()
    redirect_uri = uri + self.request.path
    
    flow = OAuth2WebServerFlow(
      settings.PRIV_GOOGLE_API_CLIENT_ID,
      settings.PRIV_GOOGLE_API_CLIENT_SECRET,
      '',   # scope
      redirect_uri=redirect_uri,
      user_agent=None,
      auth_uri=settings.GOOGLE_AUTH_URI,
      token_uri=settings.GOOGLE_TOKEN_URI
    )
    
    return flow
    
  def get_credentials (self, check_cookie=True):
    if check_cookie:
      creds = self.get_session_credentials()
      if creds:
        return creds
        
    code = self.request.REQUEST.get('code', '')
    if not code:
      return None
      
    oauth_flow = self.CreateOAuthFlow()
    
    try:
      creds = oauth_flow.step2_exchange(code)
      
    except FlowExchangeError:
      return None
      
    users_service = CreateService('oauth2', 'v2', creds)
    info = users_service.userinfo().get().execute()
    self.userid = info.get('id')
    StorageByKeyName(Credentials, self.userid, 'credentials').put(creds)
    return creds
    
  def get_session_credentials (self):
    userid = self.request.get_signed_cookie(settings.USERID_COOKIE, default=None, salt=settings.PRIV_SALT)
    if userid:
      creds = StorageByKeyName(Credentials, userid, 'credentials').get()
      if creds and creds.invalid:
        return None
        
      self.userid = userid
      return creds
      
    return None
    
  def redirect_auth (self):
    flow = self.CreateOAuthFlow()
    flow.scope = settings.ALL_SCOPES
    uri = flow.step1_get_authorize_url()
    return http.HttpResponseRedirect(uri)
    
def home (request):
  da = DriveAuth(request)
  creds = da.get_credentials(check_cookie=False)
  if creds is None:
    return da.redirect_auth()
    
  c = {
    'CLIENT_ID': settings.PRIV_GOOGLE_API_CLIENT_ID.split('.')[0],
  }
  response = TemplateResponse(request, 'editor.html', c)
  
  expires = datetime.utcnow() + timedelta(seconds=settings.MAX_AGE)
  response.set_signed_cookie(
    settings.USERID_COOKIE,
    value=da.userid,
    salt=settings.PRIV_SALT
  )
  return response
  