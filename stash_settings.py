import sys
import subprocess
import json
from workflow import Workflow, PasswordNotFound, ICON_WARNING

DELIMITER = '='

def split_and_check_for_backslash(query):
  query_list = query.split(DELIMITER)
  if query_list[-1].endswith('\\'):
    command = 'stash-settings '
    if len(query_list) > 1 and len(query_list[1]) > 1:
      command = '{} {}'.format(command, DELIMITER.join(query_list[:-1]) + DELIMITER)
    subprocess.call(['osascript', 'alfred_search.applescript', command])
    sys.exit(0)
  return query_list

def get_settings():
  with open('stash_settings.json') as data_file:
    data = json.load(data_file)
    return data['settings']

def list_settings(settings, query, is_valid):
  for setting in settings:
    setting_name = setting.get('name')
    setting_title = setting.get('title')
    setting_subtitle = setting.get('subtitle')
    setting_arg = '--{}'.format(setting_name)
    setting_type = setting.get('type')

    if setting_type == 'action':
      wf.add_item(title = setting_title,
                  subtitle = setting_subtitle,
                  valid = True,
                  arg = setting_arg)
    else:
      setting_default = setting.get('default', None)
      setting_value = wf.settings.get(setting_name, setting_default)
      setting_icon = None

      if setting_type == 'password':
        try:
          setting_value = wf.get_password('stash_password')
        except PasswordNotFound:
          setting_value = None

      if setting_value:
        if setting_type != 'password':
          setting_subtitle = '{} {}'.format(setting.get('subtitle'), setting_value)
      else:
        setting_subtitle = setting.get('subtitleAlt')
        setting_icon = ICON_WARNING

      if query and len(query) > 1:
        setting_arg = '{} {}'.format(setting_arg, query[1])

      wf.add_item(title = setting_title,
                  subtitle = setting_subtitle,
                  valid = is_valid,
                  arg = setting_arg,
                  autocomplete = setting_name + DELIMITER,
                  icon = setting_icon)

def search_key_for_setting(setting):
  elements = []
  elements.append(setting['name'])
  return u' '.join(elements)

def main(wf):

  if len(wf.args):
    query = wf.args[0]
  else:
    query = None

  is_valid = False
  settings = get_settings()

  if query:
    query = split_and_check_for_backslash(query)
    settings_filtered = wf.filter(query[0], settings, key = search_key_for_setting)
    if len(settings_filtered) == 1 and len(query) > 1 and len(query[1]) > 1:
      is_valid = True
    list_settings(settings_filtered, query, is_valid)
  else:
    list_settings(settings, query, is_valid)

  wf.send_feedback()
  return 0

if __name__ == u"__main__":
  wf = Workflow()
  log = wf.logger
  sys.exit(wf.run(main))
