import os
import subprocess
import sys

from workflow import Workflow, PasswordNotFound
from workflow.background import is_running, run_in_background
from workflow.workflow import ICON_INFO, ICON_WARNING


BASE_URL = None
DELIMITER = None
DIRECTORY = None
USERNAME = None
PASSWORD = None

def check_for_settings(wf):
  missing_settings = False
  global BASE_URL
  BASE_URL = wf.settings.get('baseurl', None)

  global DELIMITER
  DELIMITER = wf.settings.get('delimiter', ':')

  global DIRECTORY
  DIRECTORY = wf.settings.get('directory', '~')

  global USERNAME
  USERNAME = wf.settings.get('username', None)

  if not BASE_URL or not USERNAME:
    missing_settings = True

  global PASSWORD
  try:
    PASSWORD = wf.get_password('stash_password')
  except PasswordNotFound:
    missing_settings = True

  if missing_settings:
    wf.add_item(title = 'Missing Settings',
                subtitle = 'Please use stash-settings command',
                valid=False,
                icon=ICON_WARNING)
    wf.send_feedback()
    return 0

def get_inbox():
  inbox = wf.cached_data('inbox', None, max_age=0)

  if not wf.cached_data_fresh('inbox', max_age=60) and not is_running('update-inbox'):
    cmd = ['/usr/bin/python', wf.workflowfile('update_inbox.py')]
    run_in_background('update-inbox', cmd)
    log.debug('inbox not fresh')

  if is_running('update-inbox'):
    log.debug('running update-inbox')
    if not inbox:
      wf.add_item(title = 'Retrieving inbox data',
                  icon = ICON_INFO)
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
  pull_request_url = pr['links']['self'][0]['href']
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

def split_and_check_for_backslash(query):
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
    query = split_and_check_for_backslash(query)
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
