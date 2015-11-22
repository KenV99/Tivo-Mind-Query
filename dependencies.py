#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2015 KenV99
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import os, sys

try:
    import pip
except ImportError:
    print 'Downloading/installing required module: pip'
    try:
        import subprocess
        res = subprocess.check_call([sys.executable, 'get-pip.py'])
        if res != 0:
            raise ImportError
    except ImportError:
        raise  ImportError('Could not install pip')
    except Exception as e:
        raise e
    else:
        try:
            import pip
        except Exception as e:
            raise e

def InstallDependencies(dependency_dict):
    try:
        import importlib, copy
    except ImportError:
        raise ImportError('Required base libraries not installed (importlib or copy')
    pip_args = [ '-vvv' ]
    try:
        proxy = os.environ['http_proxy']
    except Exception as e:
        sys.exc_clear()
        proxy = None
    if proxy is not None:
        pip_args.append('--proxy')
        pip_args.append(proxy)
    pip_args.append('install')
    try:
        for req in dependency_dict.keys():
            q = "Python package containing: %s not intalled.\n Download and install?" % req
            if query_yes_no(q) is False:
                raise ImportError("Required package not installed by user choice.")
            pai = copy.copy(pip_args)
            try:
                if '--upgrade' in dependency_dict[req] or '-U' in dependency_dict[req]:
                    raise ImportError
                importlib.import_module(req)
            except ImportError:
                if dependency_dict[req] != []:
                    pai.extend(dependency_dict[req])
                else:
                    pai.append(req)
                try:
                    res = pip.main(args=pai)
                    if res == 1:
                        raise ImportError("Could not download/install required package: %s" % req)
                except Exception as e:
                    raise ImportError("Could not download/install required package: %s" % req)
                try:
                    importlib.import_module(req)
                except ImportError:
                    ImportError("Could not import required package: %s after download/install" % req)
            except Exception as e:
                raise e
    except ImportError:
        raise
    except Exception as e:
        raise e


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


