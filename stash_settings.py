import sys
from workflow import Workflow

def main(wf):

  if len(wf.args):
    query = wf.args[0]
  else:
    query = None

  if query:
    canComplete = True
  else:
    canComplete = False

  wf.add_item(title = 'Set base url',
    subtitle = 'Add your base url and hit Enter',
    valid = canComplete,
    arg = '--baseurl {}'.format(query))

  wf.add_item(title = 'Set delimiter',
    subtitle = 'Add your delimiter and hit Enter',
    valid = canComplete,
    arg = '--delimiter {}'.format(query))

  wf.add_item(title = 'Set directory',
    subtitle = 'Add your local projects directory and hit Enter',
    valid = canComplete,
    arg = '--directory {}'.format(query))

  wf.add_item(title = 'Set username',
    subtitle = 'Add your username and hit Enter',
    valid = canComplete,
    arg = '--username {}'.format(query))

  wf.add_item(title = 'Set password',
    subtitle = 'Add your password and hit Enter',
    valid = canComplete,
    arg = '--password {}'.format(query))

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
