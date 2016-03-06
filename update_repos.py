import sys
import base64
import os
from workflow import Workflow, web, ICON_WARNING, PasswordNotFound
from workflow.background import run_in_background

BASE_URL = None
USERNAME = None
PASSWORD = None

def check_for_settings(wf):
  global BASE_URL
  BASE_URL = wf.settings.get('baseurl', None)
  if not BASE_URL:
    wf.add_item(title = 'No base url set.',
                subtitle = 'Please use stash-settings to set your base url.',
                valid=False,
                icon=ICON_WARNING)
    wf.send_feedback()
    return 0

  global USERNAME
  USERNAME = wf.settings.get('username', None)
  if not USERNAME:
    wf.add_item(title = 'No username set.',
                subtitle = 'Please use stash-settings to set your username.',
                valid=False,
                icon=ICON_WARNING)
    wf.send_feedback()
    return 0

  global PASSWORD
  try:
    PASSWORD = wf.get_password('stash_password')
  except PasswordNotFound:
    wf.add_item(title = 'No password set.',
                subtitle = 'Please use stash-settings to set your password.',
                valid=False,
                icon=ICON_WARNING)
    wf.send_feedback()
    return 0

def get_repos():
  auth = base64.b64encode('{}:{}'.format(USERNAME, PASSWORD))
  limit = 1000
  isLastPage = False
  start = 0
  repos = []
  while not isLastPage:
    url = '{}/rest/api/1.0/repos'.format(BASE_URL)
    params = {'limit': 1000, 'start': start}
    headers = {'Authorization': 'Basic {}'.format(auth)}
    response = web.get(url, params = params, headers = headers)
    response.raise_for_status()
    result = response.json()
    isLastPage = result['isLastPage']
    if not isLastPage:
      start = result['nextPageStart']
    repos.extend(result['values'])
  repos = [repo for repo in repos if not repo.get('origin')]
  return repos

def main(wf):
  check_for_settings(wf)
  repos = wf.cached_data('repos', get_repos, max_age=60)
  return 0

if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))