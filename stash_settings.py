import sys
from workflow import Workflow, PasswordNotFound, ICON_WARNING

def main(wf):

  if len(wf.args):
    query = wf.args[0]
  else:
    query = None

  if query:
    canComplete = True
  else:
    canComplete = False

  BASEURL = wf.settings.get('baseurl', None)
  DELIMITER = wf.settings.get('delimiter', None)
  DIRECTORY = wf.settings.get('directory', None)
  USERNAME = wf.settings.get('username', None)

  try:
    PASSWORD = wf.get_password('stash_password')
  except PasswordNotFound:
    PASSWORD = None

  if BASEURL:
    baseUrlSub = 'Base url set: "{}"'.format(BASEURL)
    baseUrlIcon = None
  else:
    baseUrlSub = 'Add your base url and hit Enter'
    baseUrlIcon = ICON_WARNING

  if DELIMITER:
    delimiterSub = 'Delimiter set: "{}"'.format(DELIMITER)
  else:
    delimiterSub = 'Default delimiter set: ":"'

  if DIRECTORY:
    directorySub = 'Directory set: "{}"'.format(DIRECTORY)
  else:
    directorySub = 'Add your local workspace directory and hit Enter'

  if USERNAME:
    usernameSub = 'Username set: "{}"'.format(USERNAME)
    usernameIcon = None
  else:
    usernameSub = 'Add your username and hit Enter'
    usernameIcon = ICON_WARNING

  if PASSWORD:
    passwordSub = 'Password is set.'
    passwordIcon = None
  else:
    passwordSub = 'Add your password and hit Enter'
    passwordIcon = ICON_WARNING

  wf.add_item(title = 'Set base url',
    subtitle = baseUrlSub,
    valid = canComplete,
    arg = '--baseurl {}'.format(query),
    icon = baseUrlIcon)

  wf.add_item(title = 'Set delimiter',
    subtitle = delimiterSub,
    valid = canComplete,
    arg = '--delimiter {}'.format(query))

  wf.add_item(title = 'Set directory',
    subtitle = directorySub,
    valid = canComplete,
    arg = '--directory {}'.format(query))

  wf.add_item(title = 'Set username',
    subtitle = usernameSub,
    valid = canComplete,
    arg = '--username {}'.format(query),
    icon = usernameIcon)

  wf.add_item(title = 'Set password',
    subtitle = passwordSub,
    valid = canComplete,
    arg = '--password {}'.format(query),
    icon = passwordIcon)

  wf.add_item(title = 'Get project avatars',
    subtitle = 'Get project avatars',
    valid = True,
    arg = '--avatars')

  wf.add_item(title = 'Edit settings',
    subtitle = 'Hit Enter to open this settings file',
    valid = True,
    arg = '--edit')

  wf.send_feedback()
  return 0

if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))
