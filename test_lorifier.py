import lorifier
import os
import subprocess
import time
import urllib


def test_sample_1():
    """ Just a typical example email """
    out = subprocess.run(
        "cat samples/1.email | ./lorifier.py",
        shell=True,
        check=True,
        capture_output=True,
    )
    assert len(out.stderr) == 0
    lines = [
        "\nX-Date: ",
        "\nX-URI: https://lore.kernel.org/lkml/20181201095551.GN8952@piout.net\n",
    ]
    for line in lines:
        assert line in out.stdout.decode("utf-8")


def test_sample_2():
    """ A typical example, with emoji in body """
    out = subprocess.run(
        "cat samples/2.email | ./lorifier.py",
        shell=True,
        check=True,
        capture_output=True,
    )
    assert len(out.stderr) == 0
    lines = [
        "\nX-Date: ",
        "\nX-URI: https://lore.kernel.org/lkml/20181201095551.GN8952@piout.net\n",
        "\nHello,\n",
        "\nHere is some emoji! 🍌🍌🚀🚀\n",
    ]
    for line in lines:
        assert line in out.stdout.decode("utf-8")


def test_sample_3():
    """ UTF-8 headers """
    out = subprocess.run(
        "cat samples/3.email | ./lorifier.py",
        shell=True,
        check=True,
        capture_output=True,
    )
    assert len(out.stderr) == 0
    lines = [
        "\nX-Date: ",
        "\nX-URI: https://lore.kernel.org/lkml/CADYN=9LEVUgz_ou6kWrXZGBpUZ5Ti7BB+0Uxp1NtP18BJDVHCg@mail.gmail.com\n",
        "\nCc: =?UTF-8?B?RGFuaWVsIETDrWF6?= <daniel.diaz@linaro.org>,\n",
        '\n        "open list:KERNEL SELFTEST FRAMEWORK" \n',
    ]
    for line in lines:
        assert line in out.stdout.decode("utf-8")


def test_get_lorifier_list_fresh(mocker):
    with open("samples/lists.txt") as f:
        lists = f.read()
    with open(".in", "w") as f:
        f.write(lists)
    mocker.patch("urllib.request.urlretrieve")
    lore_lists = lorifier.muttemail._get_lorifier_list(
        cache_file=os.path.abspath(".in")
    )
    urllib.request.urlretrieve.assert_not_called()
    assert len(lore_lists) == 29
    for line in lists.splitlines():
        (key, value) = line.split(": ")
        assert lore_lists[key] == value
    os.remove(".in")


def test_get_lorifier_list_old(mocker):
    with open("samples/lists.txt") as f:
        lists = f.read()
    with open(".in", "w") as f:
        f.write(lists)
    os.utime(".in", (time.time(), time.time() - 604800))

    mocker.patch("urllib.request.urlretrieve")
    lorifier.muttemail._get_lorifier_list(
        url="https://lore.kernel.org/lists.txt",
        cache_file=os.path.abspath(".in"),
        cache_ttl=86400,
    )
    urllib.request.urlretrieve.assert_called_once_with(
        "https://lore.kernel.org/lists.txt", os.path.abspath(".in")
    )

    os.remove(".in")


def test_get_lorifier_list_first_run(mocker):
    mocker.patch("urllib.request.urlretrieve")
    lorifier.muttemail._get_lorifier_list(
        url="https://lore.kernel.org/lists.txt", cache_file=os.path.abspath(".in")
    )
    urllib.request.urlretrieve.assert_called_once_with(
        "https://lore.kernel.org/lists.txt", os.path.abspath(".in")
    )
