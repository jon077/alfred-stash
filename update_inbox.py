import base64
import sys

from workflow import Workflow, web

def get_inbox():
  USERNAME = wf.settings.get('username', None)
  PASSWORD = wf.get_password('stash_password')
  BASE_URL = wf.settings.get('baseurl', None)
  auth = base64.b64encode('{}:{}'.format(USERNAME, PASSWORD))
  limit = 1000
  isLastPage = False
  start = 0
  inbox = []
  roles = ['author', 'reviewer', 'participant']
  for role in roles:
    while not isLastPage:
      url = '{}/rest/inbox/1.0/pull-requests'.format(BASE_URL)
      params = {'limit': limit, 'start': start, 'role': role}
      headers = {'Authorization': 'Basic {}'.format(auth)}
      response = web.get(url, params = params, headers = headers)
      response.raise_for_status()
      result = response.json()
      isLastPage = result['isLastPage']
      if not isLastPage:
        start = result['nextPageStart']
      inbox.extend(result['values'])
    isLastPage = False
  return inbox

def main(wf):
  wf.cached_data('repos', get_inbox, max_age=60)
  return 0

if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))