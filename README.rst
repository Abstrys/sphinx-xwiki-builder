####################
Sphinx XWiki Builder
####################

Builds XWiki syntax output from Sphinx documentation source files. For more information, see:

* XWiki: https://www.xwiki.org/
* Sphinx: http://www.sphinx-doc.org

*Additionally*, this extension will automatically convert snake-case input files into a CamelCase
variant in line with XWiki page names, so using this extension doesn't require you to change your
filenames to be more "wiki" like. You can override this behavior, however, by using the
``xwiki_page_name_overrides`` option to set your own file to XWiki page name mapping.

You can easily copy the output for any of the generated pages and paste it or upload it to your
XWiki instance.

Installing
==========

To install the extension, run::

    python3 ./setup.py install --user

or install it from PyPi::

    pip3 install sphinx-xwiki-builder


Using the extension
===================

In your ``conf.py``, add the following::

    extensions.append("abstrys.sphinx_xwiki_builder")

Now you can build XWiki output by building the "xwiki" target::

    sphinx-build -b xwiki <sourcedir> <outputdir>

The files will be stored as <PageName>.xwiki within the 'xwiki' directory within <outputdir>.

Options
=======

You can use the following options to modify the output:


xwiki_root_page
---------------

Set the XWiki page that serves as the "root" page. This is the page that will contain the contents
of your Sphinx documentation's ``index.rst`` file.

All other pages in the documentation will be sub-pages of the root page::

    {RootPage}/{PageName}
     |          |
     |          +-- All other pages in the toctree.
     |
     +-- The `index.rst` file.

No attempt is made to create further sub-pages to avoid incompatibility with normal Sphinx projects,
and to prevent linking issues due to varying local paths.

**You should definitely set this option!** It has no default value.

xwiki_page_template
-------------------

By default, the output of the writer will be fairly plain, with minimal styling. Use this option to
provide a path to your own Jinja2 template that will be used when writing output files.

If you want to add CSS style rules to a page, for example. or include XWiki templates, custom
headers or footers, this is the place to do it.

This is optional—no template is needed to get a reasonable XWiki page from a Sphinx project.

    **Important**

    Because XWiki uses the ``{%`` and ``{{`` syntax that's also Jinja's default block and variable
    markers, and uses ``[[`` and ``((`` markers for links and group markers, you must use the following
    characters in your template to begin and end blocks, variables, and comments:

    * blocks: enclose within ``<%`` and ``%>``
    * variables: enclose within ``<<`` and ``>>``
    * comments: enclose within ``<#`` and ``#>``

    In other words, just change your normal curly-braces with angle braces.

The following variables are provided for placement of the content within the template:

* ``doc_name``: the name of the page itself (*not* the title of the H1 element).
* ``page_contents``: the rendered XWiki contents of the page.

xwiki_page_name_overrides
-------------------------

By default, Sphinx (HTML) style snake-case page names will be automatically converted to
CamelCase, which is the way that XWiki page names tend to be written.

You can use this option to provide a mapping of input file names to output wiki names. As with
Sphinx toctrees, use the file's *basename*—the filename's extension (``.rst``, ``.md``) should not
be included.

License and further information
===============================

This Sphinx extension was originally developed by Eron Hennessey <eron@abstrys.com>.

This software is provided under the conditions of the MIT open-source license. See the ``LICENSE``
file included in this repository for complete details.

