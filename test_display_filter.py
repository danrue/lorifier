import subprocess

def test_sample_1():
    ''' Just a typical example email '''
    out = subprocess.run('cat samples/1.email | ./display_filter.py', shell=True, check=True, capture_output=True)
    assert len(out.stderr) == 0
    lines = [
        '\nX-Date: Sat, 01 Dec 2018 03:55:51 -0600\n',
        '\nX-URI: https://lore.kernel.org/lkml/20181201095551.GN8952@piout.net\n',
    ]
    for line in lines:
        assert line in out.stdout.decode('utf-8')

def test_sample_2():
    ''' A typical example, with emoji in body '''
    out = subprocess.run('cat samples/2.email | ./display_filter.py', shell=True, check=True, capture_output=True)
    assert len(out.stderr) == 0
    lines = [
        '\nX-Date: Sat, 01 Dec 2018 03:55:51 -0600\n',
        '\nX-URI: https://lore.kernel.org/lkml/20181201095551.GN8952@piout.net\n',
        '\nHello,\n',
        '\nHere is some emoji! 🍌🍌🚀🚀\n',
    ]
    for line in lines:
        assert line in out.stdout.decode('utf-8')

def test_sample_3():
    ''' UTF-8 headers '''
    out = subprocess.run('cat samples/3.email | ./display_filter.py', shell=True, check=True, capture_output=True)
    assert len(out.stderr) == 0
    lines = [
        '\nX-Date: Wed, 05 Dec 2018 17:15:13 -0600\n',
        '\nX-URI: https://lore.kernel.org/lkml/CADYN=9LEVUgz_ou6kWrXZGBpUZ5Ti7BB+0Uxp1NtP18BJDVHCg@mail.gmail.com\n',
        '\nCc: =?UTF-8?B?RGFuaWVsIETDrWF6?= <daniel.diaz@linaro.org>,\n',
        '\n        "open list:KERNEL SELFTEST FRAMEWORK" \n',
    ]
    for line in lines:
        assert line in out.stdout.decode('utf-8')
