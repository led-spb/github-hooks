import os
import os.path
import hmac
import hashlib
import json
import logging
import subprocess
from collections import defaultdict


name = 'github_events'
version = '0.0.1'


class GitHubEventProcessor(object):
    def __init__(self, events_dir, sign_key, cmd_template):
        self.events_dir = events_dir
        self.sign_key = sign_key
        self.cmd_template = cmd_template or 'echo skipped'
        self.events = defaultdict(dict)
        pass

    def parse_events(self):
        _, _, files = list(os.walk(self.events_dir))[0]
        for fname in files:
            logging.debug(fname)
            full_name = os.path.join(self.events_dir, fname)
            event_id, event_type = fname.split('.')
            if event_type == 'sign':
                payload_key = 'signature'
            else:
                payload_key = 'payload'
                self.events[event_id]['type'] = event_type

            with open(full_name) as f:
                self.events[event_id][payload_key] = f.read()

            if 'files' not in self.events[event_id]:
                self.events[event_id]['files'] = []
            self.events[event_id]['files'].append(full_name)

        for event, data in self.events.iteritems():
            signature = 'sha1=' + hmac.new(self.sign_key, data['payload'], hashlib.sha1).hexdigest()
            data['payload'] = json.loads(data['payload'])
            data['verified'] = signature == data['signature']
            logging.debug(json.dumps(data, indent=2))
        pass

    def process_events(self):
        for event, data in self.events.iteritems():
            payload = data['payload']
            repository = payload['repository']['full_name']
            if not data['verified']:
                logging.warning('Event %s for %s is not verified', data['type'], repository)
                continue

            if not data['type'] == 'push':
                logging.warning('Event %s for %s is not wanted', data['type'], repository)
                continue

            logging.info('Processing event %s for %s', data['type'], repository)
            self.run_command(payload)
            pass
        pass

    def run_command(self, data):
        update_cmd = self.cmd_template.format(**data)

        logging.info('Running command %s', update_cmd)
        try:
            process = subprocess.Popen(
                update_cmd,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            result = process.communicate()
            logging.log(logging.WARNING if process.returncode > 0 else logging.DEBUG, "Process return code is: %d",
                        process.returncode)
            logging.info(result[0])
        except Exception:
            logging.exception('Error while running command')

    def clear_events(self):
        for event, data in self.events.iteritems():
            logging.info('Clear event %s', event)
            for f in data['files']:
                os.unlink(f)
        pass
