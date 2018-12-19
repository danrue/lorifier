#!/usr/bin/env python3

# Utility script to modify the display of email in mutt.
#
# Installation:
#   In muttrc, set the following:
#     set display_filter="$HOME/.mutt/lorifier.py"
#     ignore *
#     unignore from date subject to cc x-date x-uri User-Agent message-id
#
# Note that it's important that message-id is unignored; only unignored headers
# are passed to display_filter. If message-id is not passed, x-uri won't be
# generated. Therefore as a workaround, the message-id header will be removed
# so that it will not actually be displayed.
#
# This script contains the following functions:
#   X-Date: Add an X-Date header, which is Date translated to localtime
#   X-URI: Add an X-URI header, which is added when lore-compatible mail is
#          found

import email
import email.policy
import os
import sys
import time
import urllib.request

from email.utils import mktime_tz, parsedate_tz, formatdate
from collections import OrderedDict


class muttemail:
    def __init__(self, raw_message):
        self.message = email.message_from_string(raw_message)

    def as_string(self):
        return self.message.as_string(policy=email.policy.EmailPolicy(utf8=True))

    def create_xdate_header(self):
        """ Add an X-Date header, which is Date converted to localtime. """
        date = self.message.get("Date", None)
        if not date:
            return

        tz_tuple = parsedate_tz(date)
        epoch_time = mktime_tz(tz_tuple)
        self.message.add_header("X-Date", formatdate(epoch_time, localtime=True))

    def remove_header(self, header):
        """ Remove the named header """
        for i in reversed(range(len(self.message._headers))):
            header_name = self.message._headers[i][0].lower()
            if header_name == header.lower():
                del (self.message._headers[i])

    @staticmethod
    def _get_lorifier_list(
        url="https://lore.kernel.org/lists.txt",
        cache_file="~/.cache/lorifier.list",
        cache_ttl=86400,
    ):
        """
        Retrieve Lore's list of supported mailing lists. Fail gracefully.

        Cache the list at cache_file. File update is attempted at most daily.
        """

        lore_lists = OrderedDict()
        list_file = os.path.expanduser(cache_file)
        update = False

        if not os.path.isdir(os.path.expanduser(os.path.dirname(cache_file))):
            os.mkdir(os.path.expanduser(os.path.dirname(cache_file)))

        try:
            st = os.stat(list_file)
            if (time.time() - st.st_mtime) > cache_ttl:
                update = True
        except FileNotFoundError:
            update = True

        if update:
            try:
                urllib.request.urlretrieve(url, list_file)
            except Exception as e:
                # In such an event, 'touch' the file so that an update won't
                # be attempted again until cache_ttl has passed
                os.utime(list_file, (time.time(), time.time()))
                sys.stderr.write("Error fetching {}: {}\n".format(url, str(e)))

        if os.path.exists(list_file):
            with open(list_file) as f:
                for line in f.readlines():
                    (key, value) = line.strip().split(": ")
                    lore_lists[key] = value

        # Prefer lkml links
        if "linux-kernel.vger.kernel.org" in lore_lists:
            lore_lists.move_to_end("linux-kernel.vger.kernel.org", last=False)

        return lore_lists

    def create_xuri_header(self):
        """
        If the mail is sent to a lore-supported mailing list, provide a header
        with a lore link directly.

        Message-ID header must be present. Be sure it is unignored. This
        function will remove Message-ID.
        """

        lore_lists = self._get_lorifier_list()

        message_id = self.message.get("Message-ID", None)
        if not message_id:
            return

        recipients = self.message.get("To", "") + " " + self.message.get("Cc", "")
        recipients = recipients.replace("@", ".")
        for email_list, lore_url in lore_lists.items():
            if email_list in recipients:
                self.message.add_header("X-URI", str(lore_url + message_id[1:-1]))
                return


if __name__ == "__main__":
    e = muttemail(sys.stdin.read())
    e.create_xdate_header()
    e.create_xuri_header()
    e.remove_header("Message-ID")
    sys.stdout.write(e.as_string())
