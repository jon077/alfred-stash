import sys
import base64
import os
import subprocess
from workflow import Workflow, web, ICON_WARNING, PasswordNotFound
from workflow.background import run_in_background

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
                subtitle = 'Please use asgard-settings to set your base url.',
                valid=False,
                icon=ICON_WARNING)
    wf.send_feedback()
    return 0

  global DELIMITER
  DELIMITER = wf.settings.get('delimiter', ':')

  global DIRECTORY
  DIRECTORY = wf.settings.get('directory', '')

  global USERNAME
  USERNAME = wf.settings.get('username', None)
  if not USERNAME:
    wf.add_item(title = 'No username set.',
                subtitle = 'Please use asgard-settings to set your username.',
                valid=False,
                icon=ICON_WARNING)
    wf.send_feedback()
    return 0

  global PASSWORD
  try:
    PASSWORD = wf.get_password('stash_password')
  except PasswordNotFound:
    wf.add_item(title = 'No password set.',
                subtitle = 'Please use asgard-settings to set your password.',
                valid=False,
                icon=ICON_WARNING)
    wf.send_feedback()
    return 0

def get_inbox():
  auth = base64.b64encode('{}:{}'.format(USERNAME, PASSWORD))
  limit = 1000
  isLastPage = False
  start = 0
  inbox = []
  roles = ['author', 'reviewer', 'participant']
  for role in roles:
    log.debug(role)
    while not isLastPage:
      url = '{}/rest/inbox/1.0/pull-requests'.format(BASE_URL)
      params = {'limit': 1000, 'start': start, 'role': role}
      headers = {'Authorization': 'Basic {}'.format(auth)}
      response = web.get(url, params = params, headers = headers)
      response.raise_for_status()
      result = response.json()
      isLastPage = result['isLastPage']
      if not isLastPage:
        start = result['nextPageStart']
      inbox.extend(result['values'])
      log.debug(result['size'])
    isLastPage = False
  return inbox

def search_key_for_inbox(pr):
  elements = []
  elements.append(pr['title'].replace(' ', '-'))
  return u' '.join(elements)

def list_inbox(inbox):
  for pr in inbox:
    icon_path = 'avatars/{}.png'.format(pr['toRef']['repository']['project']['key'])
    avatarExists = os.path.isfile(icon_path)
    approvals = []
    for reviewer in pr['reviewers']:
      approval = 'o' if reviewer['approved'] else 'x'
      name = reviewer['user']['name']
      approvals.append('{} {}'.format(approval, name))
    approvals.sort()
    wf.add_item(title = pr['title'],
                subtitle = '{} | {}'.format(pr['author']['user']['displayName'], ', '.join(approvals)),
                autocomplete = pr['title'].replace(' ', '-'),
                icon = icon_path if avatarExists else None)

def name_repo_tab(pr):
  projectKey = pr['toRef']['repository']['project']['key']
  repoName = pr['toRef']['repository']['name']
  command = ' && echo -ne \'\\033]0;{}/{}\\007\''.format(projectKey, repoName)
  return command

def list_pr_options(pr):
  projectKey = pr['toRef']['repository']['project']['key']
  repoName = pr['toRef']['repository']['name']
  directory = '{}/{}/{}'.format(DIRECTORY, projectKey, repoName)
  dirExists = os.path.isdir(directory)

  pull_request_url = '{}{}'.format(BASE_URL, pr['link']['url'])
  wf.add_item(title = 'Open pull-request in browser',
              subtitle = pull_request_url,
              valid = True,
              arg = '--browse {}'.format(pull_request_url))

  if dirExists:
    iterm = 'cd {} && git status{}'.format(directory, name_repo_tab(pr))
    wf.add_item(title = 'Open repo in iTerm',
                subtitle = directory,
                valid = True,
                arg = '--iterm "{}"'.format(iterm))

    wf.add_item(title = 'Reveal repo in finder',
                subtitle = directory,
                valid = True,
                arg = '--browse {}'.format(directory))
  else:
    sshLink = next((link['href'] for link in pr['toRef']['repository']['links']['clone'] if ('ssh' == link['name'])), None)
    if sshLink:
      clone = 'cd {0} && if [ -d {1} ]; then cd {1}; else mkdir {1} && cd {1}; fi && git clone {2} && cd {3} && git status{4}'.format(DIRECTORY, projectKey, sshLink, repoName, name_repo_tab(pr))
      wf.add_item(title = 'Clone repo locally',
                  subtitle = directory,
                  valid = True,
                  arg = '--iterm "{}"'.format(clone))

def split_query(query):
  query_list = query.split(DELIMITER)
  if query_list[-1].endswith('\\'):
    command = 'stash-inbox {}'.format(DELIMITER.join(query_list[:-1]))
    subprocess.call(['osascript', 'alfred_search.applescript', command])
    sys.exit(0)
  return query_list

def main(wf):
  check_for_settings(wf)

  if len(wf.args):
    query = wf.args[0]
  else:
    query = None

  inbox = wf.cached_data('inbox', get_inbox, max_age=30)

  if query:
    query = split_query(query)
    inbox_filtered = wf.filter(query[0], inbox, key=search_key_for_inbox)
    pr = next((pr for pr in inbox_filtered if (query[0] == pr['title'].replace(' ', '-'))), None)
    if pr and len(query) == 1:
      list_pr_options(pr)
    else:
      list_inbox(inbox_filtered)
  else:
    list_inbox(inbox)

  wf.send_feedback()
  return 0


if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))