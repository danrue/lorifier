#!/usr/bin/env python3

# Utility script to modify the display of email in mutt.
#
# Installation:
#   In muttrc, set the following:
#     set display_filter="$HOME/.mutt/lorifier.py"
#     ignore *
#     unignore from date subject to cc x-date x-uri message-id
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
import sys

from email.utils import mktime_tz, parsedate_tz, formatdate

LORE_MASK = "https://lore.kernel.org/all/%s"


class muttemail:
    def __init__(self, raw_message):
        self.message = email.message_from_string(raw_message)

    def as_string(self):
        return self.message.as_string(policy=email.policy.EmailPolicy(utf8=True))

    def create_xdate_header(self):
        """Add an X-Date header, which is Date converted to localtime."""
        date = self.message.get("Date", None)
        if not date:
            return

        tz_tuple = parsedate_tz(date)
        epoch_time = mktime_tz(tz_tuple)
        self.message.add_header("X-Date", formatdate(epoch_time, localtime=True))

    def remove_header(self, header):
        """Remove the named header"""
        for i in reversed(range(len(self.message._headers))):
            header_name = self.message._headers[i][0].lower()
            if header_name == header.lower():
                del self.message._headers[i]

    def create_xuri_header(self):
        """
        If the mail is sent to a lore-supported mailing list, provide a header
        with a lore link directly.

        Message-ID header must be present. Be sure it is unignored. Use
        remove_header("Message-ID") to avoid displaying Message-ID.
        """

        message_id = self.message.get("Message-ID", None)
        if not message_id:
            return

        lore_url = LORE_MASK % str(message_id).strip("<>")
        self.message.add_header("X-URI", lore_url)


if __name__ == "__main__":
    e = muttemail(sys.stdin.read())
    e.create_xdate_header()
    e.create_xuri_header()
    e.remove_header("Message-ID")
    sys.stdout.write(e.as_string())
