# Tests for the misc utilities module.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Port to Cuts.
#
import string

import cuts.blueprints.img.misc_utils as mutils


class TestMiscUtils(object):

    ID_CHARS = set(string.ascii_letters + string.digits + '_')
    geeks = "Ge;ek * s:fo ! r;_Ge *!@#$%^&*()-+={[}]|\\:;\"'<,>.?/ e*k:s_ !"
    teststr = '*Nothing* [0]...is returned 2 U: (that is 4 sure) by DEFAULT!'

    testdict = {'a': True, 'b': False, 'c': 0, 'd': 1, 'e': {}, 'f': {1: 1},
                'g': [], 'h': [1], 'i': None, 'j': 'Jstr', 'k': 99.9}
    testvec = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']


    def test_get_in(self):
        nester = { 'a': 'a',
                   'L1': { 'a': 'a',
                           'L2': { 'a': 'a',
                                   'badval': [],
                                   'L3': { 'a': 'a',
                                           'L4': {} } } } }

        assert mutils.get_in(nester, ['a']) == 'a'
        assert mutils.get_in(nester, ['L1', 'a']) == 'a'
        assert mutils.get_in(nester, ['L1', 'L2', 'a']) == 'a'
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'a']) == 'a'

        assert mutils.get_in(nester, []) is None
        assert mutils.get_in(nester, ['b']) is None
        assert mutils.get_in(nester, ['L1', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4', 'b']) is None
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4', 'a']) is None

        assert mutils.get_in(nester, ['L1']) is not None
        assert isinstance(mutils.get_in(nester, ['L1']), dict)
        assert mutils.get_in(nester, ['L1', 'L2']) is not None
        assert isinstance(mutils.get_in(nester, ['L1', 'L2']), dict)
        assert mutils.get_in(nester, ['L1', 'L2', 'L3']) is not None
        assert isinstance(mutils.get_in(nester, ['L1', 'L2', 'L3']), dict)
        assert mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4']) is not None
        assert isinstance(mutils.get_in(nester, ['L1', 'L2', 'L3', 'L4']), dict)
        assert mutils.get_in(nester, ['L1', 'L2', 'badval', 'nosuchkey']) is None



    def test_keep_characters_empty(self):
        assert mutils.keep_characters('') == ''
        assert mutils.keep_characters(self.teststr) == ''
        assert mutils.keep_characters(self.geeks) == ''


    def test_keep_characters(self):
        assert mutils.keep_characters('aAbBcC..xXyYzZ', string.ascii_lowercase) == 'abcxyz'
        assert mutils.keep_characters('aAbBcC..xXyYzZ', string.ascii_uppercase) == 'ABCXYZ'
        assert mutils.keep_characters('aAbBcC..xXyYzZ', string.ascii_letters) == 'aAbBcCxXyYzZ'
        assert mutils.keep_characters(self.geeks, self.ID_CHARS) == 'Geeksfor_Geeks_'
        assert mutils.keep_characters(self.teststr, string.digits) == '024'
        assert mutils.keep_characters(self.teststr, string.punctuation) == '**[]...:()!'


    def test_keep_characters_sets(self):
        assert mutils.keep_characters('aAbBcC..xXyYzZ', set(string.ascii_lowercase)) == 'abcxyz'
        assert mutils.keep_characters('aAbBcC..xXyYzZ', set(string.ascii_uppercase)) == 'ABCXYZ'
        assert mutils.keep_characters('aAbBcC..xXyYzZ', set(string.ascii_letters)) == 'aAbBcCxXyYzZ'
        assert mutils.keep_characters(self.geeks, set(self.ID_CHARS)) == 'Geeksfor_Geeks_'
        assert mutils.keep_characters(self.teststr, set(string.digits)) == '024'
        assert mutils.keep_characters(self.teststr, set(string.punctuation)) == '**[]...:()!'



    def test_keep_empty_dict(self):
        empty = dict()
        vec = mutils.keep(empty.get, self.testvec)
        assert vec == []


    def test_keep_dict(self):
        vec = mutils.keep(self.testdict.get, self.testvec)
        print(vec)
        assert vec == [True, False, 0, 1, {}, {1: 1}, [], [1], 'Jstr', 99.9]



    def test_missing_entries_noreq(self):
        miss = mutils.missing_entries(self.testdict, [])
        print(miss)
        assert miss is None


    def test_missing_entries_keys(self):
        miss = mutils.missing_entries(self.testdict, list(self.testdict.keys()))
        print(miss)
        assert miss is None


    def test_missing_entries_1(self):
        miss = mutils.missing_entries(self.testdict, ['nosuchkey'])
        print(miss)
        assert miss is not None
        assert len(miss) == 1
        assert miss[0] == 'nosuchkey'


    def test_missing_entries(self):
        miss = mutils.missing_entries(self.testdict, ['a', 'aa', 'b', 'bb', 'c', 'ccc'])
        print(miss)
        assert miss is not None
        assert len(miss) == 3
        assert 'a' not in miss
        assert 'b' not in miss
        assert 'c' not in miss
        assert 'aa' in miss
        assert 'bb' in miss
        assert 'ccc' in miss


    def test_remove_entries_default(self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs)  # modifies by side-effect
        print(hdrs)
        assert len(hdrs) == old_len
        assert 'HISTORY' in hdrs
        assert 'COMMENT' in hdrs
        assert 'history' in hdrs
        assert 'comment' in hdrs


    def test_remove_entries_ignore_nonexist(self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs, ignore=['AAA', 'pikey'])  # modifies by side-effect
        print(hdrs)
        assert len(hdrs) == old_len
        assert 'AA' in hdrs
        assert 'pi' in hdrs
        assert 'AAA' not in hdrs
        assert 'pikey' not in hdrs


    def test_remove_entries_ignore_empty(self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs, ignore=[])  # modifies by side-effect
        print(hdrs)
        assert len(hdrs) == old_len
        assert 'AA' in hdrs
        assert 'pi' in hdrs
        assert 'HISTORY' in hdrs
        assert 'COMMENT' in hdrs
        assert 'history' in hdrs
        assert 'comment' in hdrs


    def test_remove_entries_nohist(self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        old_len = len (hdrs)
        mutils.remove_entries(hdrs, ignore=['HISTORY', 'history'])
        print(hdrs)
        assert len(hdrs) == (old_len - 2)
        assert 'HISTORY' not in hdrs
        assert 'history' not in hdrs
        assert 'COMMENT' in hdrs
        assert 'comment' in hdrs


    def test_remove_entries_all(self):
        hdrs = {
            'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne',
            'COMMENT': 'no comment', 'HISTORY': 'repeats',
            'comment': 'A comment', 'history': 'again'
        }
        keys = list(hdrs.keys()).copy()     # prevent change-during-iteration error
        mutils.remove_entries(hdrs, ignore=keys)
        print(hdrs)
        assert len(hdrs) == 0
        assert 'HISTORY' not in hdrs
        assert 'history' not in hdrs
        assert 'COMMENT' not in hdrs
        assert 'comment' not in hdrs



    def test_to_JSON_empty(self):
        tstdict = dict()
        json = mutils.to_JSON(tstdict)
        print(json)
        assert json is not None
        assert json == '{}'


    def test_to_JSON(self):
        tstdict = {'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne' }
        json = mutils.to_JSON(tstdict)
        print(json)
        assert json is not None
        assert '"a": 1' in json
        assert '"b": "bee"' in json
        assert '"pi": 3.14159' in json
        assert '"AA": "Milne"' in json


    def test_to_JSON_keywords(self):
        tstdict = {'a': 1, 'b': 'bee', 'pi': 3.14159, 'AA': 'Milne' }
        json = mutils.to_JSON(tstdict, sort_keys=True)
        print(json)
        assert json is not None
        assert '"a": 1' in json
        assert '"b": "bee"' in json
        assert '"pi": 3.14159' in json
        assert '"AA": "Milne"' in json
        assert json.index('"AA"') < json.index('"a"')
        assert json.index('"AA"') < json.index('"b"')
        assert json.index('"AA"') < json.index('"pi"')
        assert json.index('"a"') < json.index('"b"')
        assert json.index('"a"') < json.index('"pi"')
        assert json.index('"b"') < json.index('"pi"')
