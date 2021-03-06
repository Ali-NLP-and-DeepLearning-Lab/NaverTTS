# -*- coding: utf-8 -*-
import os
import pytest
from mock import Mock

from navertts.tts import NaverTTS, NaverTTSError
from navertts.lang import _extra_langs

# Testing all languages takes some time.
# Set TEST_LANGS envvar to choose languages to test.
#  * 'fetch': Languages fetched from the Web
#  * 'extra': Languagee set in Languages.EXTRA_LANGS
#  * 'all': All of the above
#  * <csv>: Languages tags list to test
# Unset TEST_LANGS to test everything ('all')
# See: langs_dict()


"""Construct a dict of suites of languages to test.
{ '<suite name>' : <list or dict of language tags> }

ex.: { 'fetch' : {'en': 'English', 'fr': 'French'},
       'extra' : {'en': 'English', 'fr': 'French'} }
ex.: { 'environ' : ['en', 'fr'] }
"""
env = os.environ.get('TEST_LANGS')
if not env or env == 'all':
    langs = {} # _fetch_langs()
    langs.update(_extra_langs())
elif env == 'fetch':
    langs = {} # _fetch_langs()
elif env == 'extra':
    langs = _extra_langs()
else:
    env_langs = {l: l for l in env.split(',') if l}
    langs = env_langs


@pytest.mark.parametrize('lang', langs.keys(), ids=list(langs.values()))
def test_TTS(tmp_path, lang):
    """Test all supported languages and file save"""

    text = "This is a test"
    """Create output .mp3 file successfully"""
    for speed in ('normal', 'slow', 'fast'):
        filename = tmp_path / 'test_{}_.mp3'.format(lang)
        # Create NaverTTS and save
        tts = NaverTTS(text=text, lang=lang, speed=speed)
        tts.save(filename)

        # Check if files created is > 2k
        assert filename.stat().st_size > 2000


def test_unsupported_language_check():
    """Raise ValueError on unsupported language (with language check)"""
    lang = 'xx'
    text = "Lorem ipsum"
    check = True
    with pytest.raises(ValueError):
        NaverTTS(text=text, lang=lang, lang_check=check)


def test_empty_string():
    """Raise AssertionError on empty string"""
    text = ""
    with pytest.raises(AssertionError):
        NaverTTS(text=text)


def test_no_text_parts(tmp_path):
    """Raises AssertionError on no content to send to API (no text_parts)"""
    text = "                                                                                                          ..,\n"
    with pytest.raises(AssertionError):
        filename = tmp_path / 'no_content.txt'
        tts = NaverTTS(text=text)
        tts.save(filename)


# Test write_to_fp()/save() cases not covered elsewhere in this file

def test_bad_fp_type():
    """Raise TypeError if fp is not a file-like object (no .write())"""
    # Create gTTS and save
    tts = NaverTTS(text='test')
    with pytest.raises(TypeError):
        tts.write_to_fp(5)


def test_save(tmp_path):
    """Save .mp3 file successfully"""
    filename = tmp_path / 'save.mp3'
    # Create NaverTTS and save
    tts = NaverTTS(text='test')
    tts.save(filename)

    # Check if file created is > 2k
    assert filename.stat().st_size > 2000


def test_msg():
    """Test NaverTTSError internal exception handling
    Set exception message successfully"""
    error1 = NaverTTSError('test')
    assert 'test' == error1.msg

    error2 = NaverTTSError()
    assert error2.msg is None


def test_infer_msg():
    """Infer message sucessfully based on context"""

    # Without response:

    # Bad TLD
    ttsTLD = Mock(tld='invalid')
    errorTLD = NaverTTSError(tts=ttsTLD)
    assert errorTLD.msg == "Failed to connect. Probable cause: Host 'https://papago.naver.invalid/apis/tts/makeID' is not reachable"

    # With response:

    # 403
    tts403 = Mock()
    response403 = Mock(status_code=403, reason='aaa')
    error403 = NaverTTSError(tts=tts403, response=response403)
    assert error403.msg == "403 (aaa) from TTS API. Probable cause: Bad token or upstream API changes"

    # 404 (and not lang_check)
    tts404 = Mock(lang='xx', lang_check=False)
    response404 = Mock(status_code=404, reason='bbb')
    error404 = NaverTTSError(tts=tts404, response=response404)
    assert error404.msg == "404 (bbb) from TTS API. Probable cause: Unsupported language 'xx'"

    # >= 500
    tts500 = Mock()
    response500 = Mock(status_code=500, reason='ccc')
    error500 = NaverTTSError(tts=tts500, response=response500)
    assert error500.msg == "500 (ccc) from TTS API. Probable cause: Uptream API error. Try again later."

    # Unknown (ex. 100)
    tts100 = Mock()
    response100 = Mock(status_code=100, reason='ddd')
    error100 = NaverTTSError(tts=tts100, response=response100)
    assert error100.msg == "100 (ddd) from TTS API. Probable cause: Unknown"


def test_WebRequest(tmp_path):
    """Test Web Requests"""

    text = "Lorem ipsum"

    """Raise NaverTTSError on unsupported language (without language check)"""
    lang = 'xx'
    check = False

    with pytest.raises(ValueError):
        filename = tmp_path / 'xx.txt'
        # Create NaverTTS
        tts = NaverTTS(text=text, lang=lang, lang_check=check)
        tts.save(filename)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
