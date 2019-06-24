import os
import os.path
import hmac
import hashlib
import json
from collections import defaultdict

key = 'qwerty'
root_dir, _, files = list(os.walk('tests/data'))[0]

events = defaultdict(dict)
for fname in files:
    full_name = os.path.join(root_dir, fname)
    event_id, event_type = fname.split('.')
    if event_type == 'sign':
        payload_key = 'signature'
    else:
        payload_key = 'payload'
        events[event_id] = {'type': event_type}

    with open(full_name) as f:
        events[event_id][payload_key] = f.read()

    if 'files' not in events[event_id]:
       events[event_id]['files'] = []
    events[event_id]['files'].append(full_name)

for event, data in events.iteritems():
    signature = 'sha1='+hmac.new(key, data['payload'], hashlib.sha1).hexdigest()

    if signature == data['signature']:
        data['verified'] = True
        data['payload'] = json.loads(data['payload'])
    else:
        data['verified'] = False
        del data['payload']


for event, data in events.iteritems():
    if data['type'] == 'push':
       branch = data['payload']['ref'].replace('refs/heads/','')

       repo = data['payload']['repository']['full_name']
       clone_url = data['payload']['repository']['clone_url']

       update_cmd = '~/bin/pip install --upgrade %s@%s' % (clone_url, branch)
       print update_cmd
    else:
       # ignore
       pass
