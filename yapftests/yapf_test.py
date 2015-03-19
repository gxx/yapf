# -*- coding: utf-8 -*-
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
"""Tests for yapf.yapf."""

import io
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

from yapf.yapflib import yapf_api

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
YAPF_BINARY = [sys.executable, '-m', 'yapf']


class YapfTest(unittest.TestCase):

  def _Check(self, unformatted_code, expected_formatted_code):
    formatted_code = yapf_api.FormatCode(unformatted_code)
    self.assertEqual(expected_formatted_code, formatted_code)

  def testSimple(self):
    unformatted_code = textwrap.dedent(u"""\
        print('foo')
        """)
    self._Check(unformatted_code, unformatted_code)


class CommandLineTest(unittest.TestCase):
  """Test how calling yapf from the command line acts."""

  def setUp(self):
    self.test_tmpdir = tempfile.mkdtemp()

  def tearDown(self):
    shutil.rmtree(self.test_tmpdir)

  def testUnicodeEncodingPipedToFile(self):
    unformatted_code = textwrap.dedent(u"""\
        def foo():
          print('⇒')
        """)

    with tempfile.NamedTemporaryFile(suffix='.py',
                                     dir=self.test_tmpdir) as outfile:
      with tempfile.NamedTemporaryFile(suffix='.py',
                                       dir=self.test_tmpdir) as testfile:
        testfile.write(unformatted_code.encode('UTF-8'))
        subprocess.check_call(YAPF_BINARY + ['--diff', testfile.name],
                              stdout=outfile)

  def testInPlaceReformatting(self):
    unformatted_code = textwrap.dedent(u"""\
        def foo():
          x = 37
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        def foo():
          x = 37
        """)

    with tempfile.NamedTemporaryFile(suffix='.py',
                                     dir=self.test_tmpdir) as testfile:
      testfile.write(unformatted_code.encode('UTF-8'))
      testfile.seek(0)

      p = subprocess.Popen(YAPF_BINARY + ['--in-place', testfile.name])
      p.wait()

      with io.open(testfile.name, mode='r', newline='') as fd:
        reformatted_code = fd.read()

    self.assertEqual(reformatted_code, expected_formatted_code)

  def testReadFromStdin(self):
    unformatted_code = textwrap.dedent(u"""\
        def foo():
          x = 37
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        def foo():
          x = 37
        """)

    p = subprocess.Popen(YAPF_BINARY,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    reformatted_code, stderrdata = p.communicate(input=unformatted_code)
    self.assertIsNone(stderrdata)
    self.assertEqual(reformatted_code, expected_formatted_code)

  def testReadSingleLineCodeFromStdin(self):
    unformatted_code = textwrap.dedent(u"""\
        if True: pass
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        if True: pass
        """)

    p = subprocess.Popen(YAPF_BINARY,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    reformatted_code, stderrdata = p.communicate(input=unformatted_code)
    self.assertIsNone(stderrdata)
    self.assertEqual(reformatted_code, expected_formatted_code)

  def testEncodingVerification(self):
    unformatted_code = textwrap.dedent(u"""\
        '''The module docstring.'''
        # -*- coding: utf-8 -*-
        def f():
            x = 37
        """)

    with tempfile.NamedTemporaryFile(suffix='.py',
                                     dir=self.test_tmpdir) as outfile:
      with tempfile.NamedTemporaryFile(suffix='.py',
                                       dir=self.test_tmpdir) as testfile:
        testfile.write(unformatted_code.encode('UTF-8'))
        subprocess.check_call(YAPF_BINARY + ['--diff', testfile.name],
                              stdout=outfile)

  def testReformattingSpecificLines(self):
    unformatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and
              xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass
        """)

    p = subprocess.Popen(YAPF_BINARY + ['--lines', '1-2'],
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    reformatted_code, stderrdata = p.communicate(input=unformatted_code)
    self.assertIsNone(stderrdata)
    self.assertEqual(reformatted_code, expected_formatted_code)

  def testReformattingSkippingLines(self):
    unformatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        # yapf: disable
        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass
        # yapf: enable
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and
              xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        # yapf: disable
        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass
        # yapf: enable
        """)

    p = subprocess.Popen(YAPF_BINARY,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    reformatted_code, stderrdata = p.communicate(input=unformatted_code)
    self.assertIsNone(stderrdata)
    self.assertEqual(reformatted_code, expected_formatted_code)

  def testReformattingSkippingToEndOfFile(self):
    unformatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        # yapf: disable
        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        def f():
          def e():
            while (xxxxxxxxxxxxxxxxxxxxx(yyyyyyyyyyyyy[zzzzz]) == 'aaaaaaaaaaa' and
                   xxxxxxxxxxxxxxxxxxxxx(yyyyyyyyyyyyy[zzzzz].aaaaaaaa[0]) ==
                   'bbbbbbb'):
              pass
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and
              xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        # yapf: disable
        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        def f():
          def e():
            while (xxxxxxxxxxxxxxxxxxxxx(yyyyyyyyyyyyy[zzzzz]) == 'aaaaaaaaaaa' and
                   xxxxxxxxxxxxxxxxxxxxx(yyyyyyyyyyyyy[zzzzz].aaaaaaaa[0]) ==
                   'bbbbbbb'):
              pass
        """)

    p = subprocess.Popen(YAPF_BINARY,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    reformatted_code, stderrdata = p.communicate(input=unformatted_code)
    self.assertIsNone(stderrdata)
    self.assertEqual(reformatted_code, expected_formatted_code)

  def testReformattingSkippingSingleLine(self):
    unformatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass

        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):  # yapf: disable
            pass
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        def h():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and
              xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):
            pass


        def g():
          if (xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0]) == 'aaaaaaaaaaa' and xxxxxxxxxxxx.yyyyyyyy(zzzzzzzzzzzzz[0].mmmmmmmm[0]) == 'bbbbbbb'):  # yapf: disable
            pass
        """)

    p = subprocess.Popen(YAPF_BINARY,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    reformatted_code, stderrdata = p.communicate(input=unformatted_code)
    self.assertIsNone(stderrdata)
    self.assertEqual(reformatted_code, expected_formatted_code)

  def testDisableWholeDataStructure(self):
    unformatted_code = textwrap.dedent(u"""\
        A = set([
            'hello',
            'world',
        ])  # yapf: disable
        """)
    expected_formatted_code = textwrap.dedent(u"""\
        A = set([
            'hello',
            'world',
        ])  # yapf: disable
        """)

    p = subprocess.Popen(YAPF_BINARY,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    reformatted_code, stderrdata = p.communicate(input=unformatted_code)
    self.assertIsNone(stderrdata)
    self.assertEqual(reformatted_code, expected_formatted_code)


def suite():
  result = unittest.TestSuite()
  result.addTests(unittest.makeSuite(YapfTest))
  result.addTests(unittest.makeSuite(CommandLineTest))
  return result


if __name__ == '__main__':
  unittest.main()