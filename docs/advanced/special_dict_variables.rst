.. _dict-variables:

Special Dictionary Variables (V???)
-----------------------------------

Dictionary variables can also be used to specify concepts such as custom prompt, description, prompt_user,
skip if, skip to, multilist, validation, welcome messages, etc.

Basic Usage
~~~~~~~~~~~

Dictionary variables for the special format need to have the default attribute. The available types are
string, int, bool, float, multilist,raw, list, password, json. The default type is string.
Most of the basic types have the same functionality

::

    {"variable_name": {
        "default" : "Some default"
    }}

The statement is equivalent to
::

    {"variable_name": "Some default"}

For lists/multilist, the default attribute can be skipped as the first item in the list is chosen as the default. For lists,
the choice attribute must be in the dictionary.

::

    {"variable_name": {
        "choices": ["var1","var2","var3"]
    }}

The statement is equivalent to
::

    {"variable_name": ["var1","var2","var3"]}


Custom Prompt
~~~~~~~~~~~~~~
Instead of the default var_name[default], in the cookiecutter.json a new format can be supported.

::

    {"variable_name": {
        "default": "special",
        "prompt" : "This is a special prompt for the text."
    }}

The following text would be printed on the console.

::

    $ This is a special prompt for the text["special"]

Description
~~~~~~~~~~~
This would allow printing a description of a certain variable before it is processed.

::

    {"version number": {
        "default": "1.0.0",
        "description" : "The library requires a certain version of the text before it can be processed."
    }}

The following text would be printed on the console.

::

    The library requires a certain version of the text before it can be processed.
    $ version number["1.0.0"]

Visibility of the Prompt
~~~~~~~~~~~~~~~~~~~~~~~~~~
This would allow for variables to be passed into the system without prompting. This is the same functionality as using
an underscore. It uses the default attribute.

::

    {"version number": {
        "default": "1.0.0",
        "prompt_user" : false
    }}


This could also allow the functionality of keywords.
In order to pass lists in to the system specify it in the default property.


::

    {"keywords": {
        "default": ["template","flask","django","node.js"],
        "prompt_user" : false
    }}

Example Debug/Welcome Message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To create welcome and debug messages, combine the visibility and the description attribute.
Set visibility to false and set the description to the message

::

    {"welcome message": {
        "prompt_user": false,
        "description": "Welcome to the cookiecutter template......"
    },
    "authors": {"prompt_user": false, "description": "The author of this template is the CookieMonster"},
    "url": {"prompt_user": false, "description": "The url to the repo is https://github.com/audreyr/cookiecutter" },
    "keywords":
        {   "prompt_user": false,
            "default": ["template","flask","django","node.js"]},
        },
    "project_name": "reddit clone"
    }

This would print the following message.

::
    Welcome to the cookiecutter template......

    The author of this template is the CookieMonster

    The url to this repo is

    project_name[reddit clone]:

This can also be used to provide a url to the project, and provide a link to the authors.



Skip if/Skip to
~~~~~~~~~~~~~~~~~
This would allow for a variable to be skipped if the attribute is true. This could allow for powerful templates where
unnecessary items aren't prompted.

::

    {"version number": {
        "default": "1.0.0",
        "skip_if" : "true"
    }}

Note: Since jinja is rendered as strings, cookiecutter interprets "true" will be interpreted as the boolean True.

If the attribute "skip if" is true, then an optional attribute of "skip_to" can be specified. This can allow skipping to
a future key in the dictionary.

::

    {"version number": {
        "default": "1.0.0",
        "skip_if": "true",
        "skip_to": "special_attribute"
        },
    "next_attribute": "",
    "special_attribute": "default"
    }


The following output would be displayed for this example.
::

    skipped version number
    skipping to special_attribute
    skipped next_attribute
    special_attribute[default]:

Multilist
~~~~~~~~~~

This is an extension to the current choice variables.

This would be an example multilist ``cookiecutter.json``::

   {
       "license": {
                  "choices": ["MIT", "BSD-3", "GNU GPL v3.0", "Apache Software License 2.0"]
            }
   }

you'd get the following choices when running Cookiecutter::

   Select license:
   1 - MIT
   2 - BSD-3
   3 - GNU GPL v3.0
   4 - Apache Software License 2.0
   Use commas to separate the items in the multi list
   Choose from 1, 2, 3, 4 [1]: 1, 2, 3

The user can input a list separated by commas with the options.
This can be used as a list::

    {% for item in cookiecutter.license %}
        {{ item }}
    {% endif %}


Validation
~~~~~~~~~~
Some items such as email or version numbers require a certain format. With regular expression, this can allow for testing
of the expression. This is an alternative to the checking in the pre_gen_hooks.py file.

::

    {"email": {
        "prompt": "Please enter your email"
        "default": "test@gmail.com",
        "validation" : "(\w+)@gmail.com"
    }}

This would provide the following functionality:

::

    Please enter your email[test@gmail.com]: test

    Invalid Pattern for email. Please follow the format (\w+)@gmail.com

    Please enter your email[test@gmail.com]: test@gmail.com

The default is the validate a maximum of 5 times. However, this can be overridden with the attribute max_times_validated.

::

    {"email": {
        "prompt": "Please enter your email"
        "default": "test@gmail.com",
        "validation" : "(\w+)@gmail.com",
        "max_times_validated": 100
    }}

.. _`Regex`: https://en.wikipedia.org/wiki/Regular_expression