import sys
import base64
import os
import subprocess
from workflow import Workflow, web, ICON_INFO, ICON_WARNING, PasswordNotFound
from workflow.background import run_in_background, is_running

BASE_URL = None
DELIMITER = None
DIRECTORY = None
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

  global DELIMITER
  DELIMITER = wf.settings.get('delimiter', ':')

  global DIRECTORY
  DIRECTORY = wf.settings.get('directory', '~')

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
  repos = wf.cached_data('repos', None, max_age=0)

  if not wf.cached_data_fresh('repos', max_age=60):
    cmd = ['/usr/bin/python', wf.workflowfile('update_repos.py')]
    run_in_background('update-repos', cmd)
    log.debug('not fresh')

  if is_running('update-repos'):
    log.debug('running update-repos')
  return repos

def search_key_for_repo(repo):
  elements = []
  elements.append(repo['name'])
  return u' '.join(elements)

def list_repos(repos):
  if repos:
    for repo in repos:
      icon_path = 'avatars/{}.png'.format(repo['project']['key'])
      avatarExists = os.path.isfile(icon_path)
      wf.add_item(title = repo['name'],
                  subtitle = repo['project']['name'],
                  autocomplete = repo['name'],
                  icon = icon_path if avatarExists else None)

def name_repo_tab(repo):
  projectKey = repo['project']['key']
  repoName = repo['name']
  command = ' && echo -ne \'\\033]0;{}/{}\\007\''.format(projectKey, repoName)
  return command

def list_repo_options(repo):
  projectKey = repo['project']['key']
  repoName = repo['name']
  directory = '{}/{}/{}'.format(DIRECTORY, projectKey, repoName)
  dirExists = os.path.isdir(directory)
  if dirExists:
    iterm = 'cd {} && git status{}'.format(directory, name_repo_tab(repo))
    wf.add_item(title = 'Open repo in iTerm',
                subtitle = directory,
                valid = True,
                arg = '--iterm "{}"'.format(iterm))

  wf.add_item(title = 'List files',
              subtitle = 'Search files for this repo',
              autocomplete = repo['name'] + DELIMITER)

  pull_requests_url = '{}/projects/{}/repos/{}/pull-requests'.format(BASE_URL, projectKey, repoName)
  wf.add_item(title = 'Open pull-request list in browser',
              subtitle = pull_requests_url,
              valid = True,
              arg = '--browse {}'.format(pull_requests_url))

  commits_url = '{}/projects/{}/repos/{}/commits'.format(BASE_URL, projectKey, repoName)
  wf.add_item(title = 'Open commit list in browser',
              subtitle = commits_url,
              valid = True,
              arg = '--browse {}'.format(commits_url))

  branches_url = '{}/projects/{}/repos/{}/branches'.format(BASE_URL, projectKey, repoName)
  wf.add_item(title = 'Open branch list in browser',
              subtitle = branches_url,
              valid = True,
              arg = '--browse {}'.format(branches_url))

  source_url = '{}/projects/{}/repos/{}/browse'.format(BASE_URL, projectKey, repoName)
  wf.add_item(title = 'Open source in browser',
              subtitle = source_url,
              valid = True,
              arg = '--browse {}'.format(source_url))

  if dirExists:
    wf.add_item(title = 'Reveal repo in finder',
                subtitle = directory,
                valid = True,
                arg = '--browse {}'.format(directory))
  else:
    sshLink = next((link['href'] for link in repo['links']['clone'] if ('ssh' == link['name'])), None)
    if sshLink:
      clone = 'cd {0} && if [ -d {1} ]; then cd {1}; else mkdir {1} && cd {1}; fi && git clone {2} && cd {3} && git status{4}'.format(DIRECTORY, projectKey, sshLink, repoName, name_repo_tab(repo))
      wf.add_item(title = 'Clone repo locally',
                  subtitle = directory,
                  valid = True,
                  arg = '--iterm "{}"'.format(clone))

def get_files(repo):
  projectKey = repo['project']['key']
  repoName = repo['name']
  auth = base64.b64encode('{}:{}'.format(USERNAME, PASSWORD))
  limit = 1000
  isLastPage = False
  start = 0
  files = []
  while not isLastPage:
    url = '{}/rest/api/1.0/projects/{}/repos/{}/files'.format(BASE_URL, projectKey, repoName)
    params = {'limit': 1000, 'start': start}
    headers = {'Authorization': 'Basic {}'.format(auth)}
    response = web.get(url, params = params, headers = headers)
    response.raise_for_status()
    result = response.json()
    isLastPage = result['isLastPage']
    if not isLastPage:
      start = result['nextPageStart']
    files.extend(result['values'])
  return files

def search_key_for_file(file_path):
  elements = []
  elements.append(file_path.split('/')[-1])
  return u' '.join(elements)

def list_files(repo, files):
  for file_path in files:
    wf.add_item(title = file_path.split('/')[-1],
                subtitle = file_path,
                autocomplete = repo['name'] + DELIMITER + file_path.split('/')[-1])

def list_file_options(repo, file_path):
  projectKey = repo['project']['key']
  repoName = repo['name']
  file_url = '{}/projects/{}/repos/{}/browse/{}'.format(BASE_URL, projectKey, repoName, file_path)
  wf.add_item(title = 'Open file in browser',
              subtitle = file_url,
              valid = True,
              arg = '--browse {}'.format(file_url))

  repo_directory = '{}/{}/{}'.format(DIRECTORY, projectKey, repoName)
  full_file_path = '{}/{}'.format(repo_directory, file_path)
  file_directory = full_file_path.rsplit('/', 1)[0]
  dirExists = os.path.isdir(file_directory)
  if dirExists:
    wf.add_item(title = 'Reveal file in finder',
                subtitle = file_directory,
                valid = True,
                arg = '--browse {}'.format(file_directory))

def split_query(query):
  query_list = query.split(DELIMITER)
  if query_list[-1].endswith('\\'):
    command = 'stash {}'.format(DELIMITER.join(query_list[:-1]))
    subprocess.call(['osascript', 'alfred_search.applescript', command])
    sys.exit(0)
  return query_list

def main(wf):
  check_for_settings(wf)

  if len(wf.args):
    query = wf.args[0]
  else:
    query = None

  repos = get_repos()

  if query:
    query = split_query(query)
    repos_filtered = wf.filter(query[0], repos, key=search_key_for_repo)
    repo = next((repo for repo in repos_filtered if (query[0] == repo['name'])), None)
    if repo and len(query) > 1:
      def wrapper_get_files():
        return get_files(repo)
      files = wf.cached_data('files', wrapper_get_files, max_age=10)
      if query[1]:
        files_filtered = wf.filter(query[1], files, key=search_key_for_file)
        file_path = next((file_path for file_path in files if query[1] == file_path.split('/')[-1]), None)
        if file_path and len(query) == 2:
          list_file_options(repo, file_path)
        else:
          list_files(repo, files_filtered)
      else:
        list_files(repo, files)
    elif repo and len(query) == 1:
      list_repo_options(repo)
    else:
      list_repos(repos_filtered)
  else:
    list_repos(repos)

  wf.send_feedback()
  return 0


if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))