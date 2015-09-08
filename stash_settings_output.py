import sys
from workflow import Workflow
from workflow.background import run_in_background, is_running
import argparse

def main(wf):

  parser = argparse.ArgumentParser()
  parser.add_argument('--baseurl', dest='baseurl', nargs='?', default=None)
  parser.add_argument('--delimiter', dest='delimiter', nargs='?', default=None)
  parser.add_argument('--directory', dest='directory', nargs='?', default=None)
  parser.add_argument('--username', dest='username', nargs='?', default=None)
  parser.add_argument('--password', dest='password', nargs='?', default=None)
  parser.add_argument('--avatars', dest='avatars', action='store_true', default=None)
  parser.add_argument('--edit', dest='edit', action='store_true', default=None)
  args = parser.parse_args(wf.args)

  if args.baseurl:
    wf.settings['baseurl'] = args.baseurl.rstrip('/')
    return 0

  if args.delimiter:
    wf.settings['delimiter'] = args.delimiter
    return 0

  if args.directory:
    wf.settings['directory'] = args.directory.rstrip('/')
    return 0

  if args.username:
    wf.settings['username'] = args.username
    return 0

  if args.password:
    wf.save_password('stash_password', args.password)
    return 0

  if args.avatars:
    cmd = ['/usr/bin/python', wf.workflowfile('update_avatars.py')]
    run_in_background('update-avatars', cmd)
    return 0

  if args.edit:
    out = ['open', wf.settings_path]
    run_in_background('edit', out)
    return 0

if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))
