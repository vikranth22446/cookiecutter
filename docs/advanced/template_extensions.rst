.. _`template extensions`:

Template Extensions
-------------------

*New in Cookiecutter 1.4*

A template may extend the Cookiecutter environment with custom `Jinja2 extensions`_,
that can add extra filters, tests, globals or even extend the parser.

To do so, a template author must specify the required extensions in ``cookiecutter.json`` as follows:

.. code-block:: json

    {
        "project_slug": "Foobar",
        "year": "{% now 'utc', '%Y' %}",
        "_extensions": ["jinja2_time.TimeExtension"]
    }

On invocation Cookiecutter tries to import the extensions and add them to its environment respectively.

In the above example, Cookiecutter provides the additional tag `now`_, after
installing the `jinja2_time.TimeExtension`_ and enabling it in ``cookiecutter.json``.

Please note that Cookiecutter will **not** install any dependencies on its own!
As a user you need to make sure you have all the extensions installed, before
running Cookiecutter on a template that requires custom Jinja2 extensions.

.. _`Jinja2 extensions`: http://jinja2.readthedocs.io/en/latest/extensions.html#extensions
.. _`now`: https://github.com/hackebrot/jinja2-time#now-tag
.. _`jinja2_time.TimeExtension`: https://github.com/hackebrot/jinja2-time

Example: Creating Extensions/Filters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create an extensions by accessing and adding it to the environment.
.. code-block:: python
    class LocalExtension(Extension):
        tags = {'hello'}
        def filter1(text):
            return reversed(text)
        def __init__(self, environment):
            super(LocalExtension, self).__init__(environment)
            enviorment["filter1"] = filter1

        def _local(self, name):
            return 'Hello World {name}!'.format(name=name)

        def parse(self, parser):
            lineno = next(parser.stream).lineno
            node = parser.parse_expression()
            call_method = self.call_method('_hello', [node], lineno=lineno)
            return nodes.Output([call_method], lineno=lineno)


Local Extensions: Using custom extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extensions can be placed in a local directory:
For example, place the localExtension in the previous example at template/extensions/local_extensions
.. code-block:: json

    {
        "project_slug": "Foobar",
        "_extensions": ["local.CustomExtension"]
    }
::

    Cookiecutter Template
    ├── LICENCE.txt
    ├── extensions
        ├──__init__.py
        ├──local_extension.py
    ├── {{ cookiecutter.proj_name }}
    │   ├── README.md


