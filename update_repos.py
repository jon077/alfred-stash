import base64
import sys

from workflow import Workflow, web

def get_repos():
  USERNAME = wf.settings.get('username', None)
  PASSWORD = wf.get_password('stash_password')
  BASE_URL = wf.settings.get('baseurl', None)
  auth = base64.b64encode('{}:{}'.format(USERNAME, PASSWORD))
  limit = 1000
  isLastPage = False
  start = 0
  repos = []
  while not isLastPage:
    url = '{}/rest/api/1.0/repos'.format(BASE_URL)
    params = {'limit': limit, 'start': start}
    headers = {'Authorization': 'Basic {}'.format(auth)}
    response = web.get(url, params = params, headers = headers)
    response.raise_for_status()
    result = response.json()
    isLastPage = result['isLastPage']
    if not isLastPage:
      start = result['nextPageStart']
    repos.extend(result['values'])
  for repo in repos:
    project = repo.get('project')
    repo['project']['key'] = project.get('key').replace('~', '')
  return repos

def main(wf):
  wf.cached_data('repos', get_repos, max_age=60)
  return 0

if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))