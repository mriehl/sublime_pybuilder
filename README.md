sublime_pybuilder
=======

Sublime text 3 plugin for [PyBuilder](http://pybuilder.github.io).

![sublime_pybuilder provides PyBuilder integration for Sublime Text 3](sublime_pybuilder.gif)

## Features
* Real-time output
* Minimal configuration if you use Anaconda or SublimePythonIDE as it reuses the settings
* Does not block so you can work or check out what to do next while building.
* [pyb-init](https://github.com/mriehl/pyb_init) support built-in

## Installation
Clone it in your sublime text `Packages/` directory.

**Package control installation coming soon!**

## Usage
Several commands will be made available to you through the command palette.
You can use them to :

* Run PyBuilder (implies default tasks)
* Clean your project
* Run unit tests
* Run integration tests
* Analyze (lint, etc.) your project
* Publish your project
* Verify your project
* Run [pyb-init](https://github.com/mriehl/pyb_init) on your project

## Configuration
sublime_pybuilder expects two project settings to be present:

* `python_interpreter`
  This is the path to your python interpreter. Could be your system python or a virtualenv.
* `project_root`
  The root of your project where the build descriptor (`build.py`) is located.

Here's what your project settings might look like :

```json
{
    "folders":
    [
        {
            "follow_symlinks": true,
            "path": "/home/mriehl/workspace/yadtshell"
        }
    ],
    "settings":
    {
        "python_interpreter": "/home/mriehl/workspace/yadtshell/venv/bin/python",
        "project_root": "/home/mriehl/workspace/yadtshell",
        "extra_paths": ["home/mriehl/workspace/yadtshell/src/main/python"]
    }
}
```

I'm using [Anaconda](https://github.com/DamnWidget/Anaconda) so I added the project sources with the `extra_paths` setting so that autocompletion and goto definition work. It is not necessary for sublime_pybuilder to work.

### Special case - only if you want to work on the PyBuilder project itself!
In order to build pybuilder, you need to run a bootstrapping script.
This script must be run with the right python interpreter in order to see your packages.
Thus we need to specify the path to the bootstrapping script additionally with the setting `pyb_path`.

My settings are:

```json
{
    "folders":
    [
        {
            "follow_symlinks": true,
            "path": "/home/mriehl/workspace/pybuilder"
        }
    ],
    "settings":
    {
        "python_interpreter": "/home/mriehl/workspace/pybuilder/venv/bin/python",
        "pyb_path": "/home/mriehl/workspace/pybuilder/bootstrap",
        "project_root": "/home/mriehl/workspace/pybuilder"
    }
}
```

## License
[MIT](https://github.com/mriehl/sublime_pybuilder/blob/master/LICENSE)
