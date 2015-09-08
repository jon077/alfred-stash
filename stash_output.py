import sys
from workflow import Workflow
from workflow.background import run_in_background, is_running
import argparse
import subprocess

def main(wf):

  parser = argparse.ArgumentParser()
  parser.add_argument('--browse', dest = 'browse', nargs = '?', default = None)
  parser.add_argument('--iterm', dest = 'iterm', nargs = argparse.REMAINDER, default = None)
  args = parser.parse_args(wf.args)

  if args.browse:
    out = ['open', args.browse]
    run_in_background('browse', out)
    return 0

  if args.iterm:
    out = ['osascript', 'open_iterm.scpt', ' '.join(args.iterm)]
    run_in_background('iterm', out)
    return 0

if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))
