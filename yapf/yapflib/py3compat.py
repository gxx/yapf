# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for Python2 / Python3 compatibility."""

import sys

PY3 = sys.version_info[0] == 3


if PY3:
  import io
  StringIO = io.StringIO
  BytesIO = io.BytesIO

  range = range
  ifilter = filter
  raw_input = input

  import configparser
else:
  import __builtin__
  import cStringIO
  StringIO = BytesIO = cStringIO.StringIO

  range = xrange

  from itertools import ifilter
  raw_input = raw_input

  import ConfigParser as configparser


def EncodeForStdout(s):
  """Encode the given string for emission to stdout.

  The string may contain non-ascii characters. This is a problem when stdout is
  redirected, because then Python doesn't know the encoding and we may get a
  UnicodeEncodeError.

  Arguments:
    s: (string) The string to encode.

  Returns:
    The encoded string if Python 2.7.
  """
  if PY3:
    return s
  else:
    return s.encode('UTF-8')


def unicode(s):
  """Force conversion of s to unicode."""
  if PY3:
    return s
  else:
    return __builtin__.unicode(s, 'unicode_escape')


# In Python 3.2+, readfp is deprecated in favor of read_file, which doesn't
# exist in Python 2 yet. To avoid deprecation warnings, subclass ConfigParser to
# fix this - now read_file works across all Python versions we care about.
class ConfigParser(configparser.ConfigParser):
  if not PY3:
    def read_file(self, fp, source=None):
      self.readfp(fp, filename=source)
