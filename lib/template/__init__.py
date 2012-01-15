"""

How to use Templating Engine
============================

Using the Engine
================

This section describes the use of the templating engine from the Python
backend.

    from lib import template

Imports the templating module to use the rendering functions.

    template.render(html_string, context)

Renders a string (html_string) based on a dictionary (context) which maps
strings of variable names to variable values.

If rendering is unsuccessful, a TemplateError is raised.

    template.render_file(filename, context)

Renders a file, given a filename based on a context dictionary. Unsuccessful
rendering handled as above.

The Locals Trick
================

If you wish to render based on the variables in the local scope, you can pass
locals() as the context argument.

Syntax of the Templating Engine
===============================

This section describes how the templating engine can be used from within HTML
code. NOTE: whitespace is required where indicated.

    {{ expr }}

Evaluates the expression and places the value in its place. The value is
HTML-escaped by default.

    {% safe expr %}

Performs the same operation as {{ expr }} except the evaluated value is not
HTML-escaped. WARNING: This should only be used if it is guaranteed that the
result of expr will be HTML-safe.

    {% include filename %}

Places the rendered contents of the file named filename in its place. If the
file does not exist, raises an IOError.

    {% if condition %}
    ...
    {% else %}
    ...
    {% end if %}

Inserts the rendered contents of the HTML between the {% if ... %} {% end if %}
tags of the statement if the condition is evaluated as true. Otherwise,
inserts the rendered contents of the body between {% else %} {% end if %}.
NOTE: defining an {% else %} block is optional.

    {% for name in iterable %}
    ...
    {% end for %}

Inserts the rendered contents of the body of the statement for each value (name)
in iterable. The current context is used to render the body.
"""

from template import render, render_file
