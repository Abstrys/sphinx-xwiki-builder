# -*- coding: utf-8 -*-
#===============================================================================
#
# Sphinx XWiki Builder
#
# by Eron Hennessey <eron@abstrys.com>
#
# Based on the syntax described here:
#
# * http://rendering.xwiki.org/xwiki/bin/view/XWiki/XWikiSyntax?syntax=2.1
#
#===============================================================================

import sys, os
import codecs, re
from typing import Iterator, Set
from docutils.nodes import Node
from docutils.core import publish_from_doctree
from sphinx.builders import Builder
from abstrys.sphinx_xwiki_writer import XWikiWriter, XWikiTranslator

JINJA2_MISSING_MSG = """
Jinja2 is required to use the xwiki_page_template option!

To install it, run::

    pip3 install jinja2

Then try building your Sphinx project again.
"""

TEMPLATE_MISSING_MSG = """
Couldn't find a template file at the path: %s

Make sure that either that file exists, or that you *remove* the
`xwiki_page_template` variable from your `conf.py` file!
"""

def snake2camel(snaked_str):
   """
   Remove hyphens or underscores and capitalize each word beyond them.

   snaked_str:
      The snake-cased string to convert.

   Example::

      snake2camel("this-is-a-snake-case-string")

   Output::

      'ThisIsASnakeCaseString'
   """
   snake_splitter = re.compile("[-_]")
   camel_str = ""
   words = snake_splitter.split(snaked_str)
   for w in words:
       camel_str += w.capitalize()
   return camel_str


class XWikiBuilder(Builder):
    """
    Build XWiki output from Sphinx input.
    """
    name = "xwiki"
    format = "xwiki"
    epilog = "XWiki output built to {outdir}"

    def get_target_uri(self, docname: str, typ: str = None) -> str:
        return snake2camel(docname)

    def get_outdated_docs(self) -> Iterator[str]:
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            targetname = os.path.join(self.outdir, docname + self.format)
            try:
                targetmtime = os.path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = os.path.getmtime(self.env.doc2path(docname))
                if srcmtime > targetmtime:
                    yield docname
            except OSError:
                # source doesn't exist anymore
                pass

    def prepare_writing(self, docnames: Set[str]) -> None:
        self.writer = XWikiWriter(self.app.config)

        # Is there a template set using the xwiki_page_template option?
        if (hasattr(self.app.config, 'xwiki_page_template')
            and (self.app.config.xwiki_page_template != None)):

            # attempt to load Jinja2 and fail if it can't be found.
            try:
                from jinja2 import Environment, FileSystemLoader
            except:
                print(JINJA2_MISSING_MSG)
                sys.exit(1)

            # make sure that the template path exists, at least.
            if not os.path.exists(self.app.config.xwiki_page_template):
                print(TEMPLATE_MISSING_MSG % self.app.config.xwiki_page_template)
                sys.exit(1)

            # We'll need the path in two parts (path, filename) for use w/ Jinja.
            template_path, template_name = os.path.split(self.app.config.xwiki_page_template)

            jinja_env = Environment(
                loader=FileSystemLoader(template_path),
                # a few thing in the Jinja environment need to be overridden to avoid conflicts w/
                # XWiki syntax (see the README for more info).
                block_start_string='<%', block_end_string='%>',
                variable_start_string='<<', variable_end_string='>>',
                comment_start_string='<#', comment_end_string='#>')

            # Get the template for rendering pages in write_doc().
            self.page_template = jinja_env.get_template(template_name)


    def write_doc(self, docname: str, doctree: Node) -> None:
        # get the output from the writer
        writer_output = publish_from_doctree(doctree, writer=self.writer)

        # make it easy to write code that uses config values (we're going to do that more than a few
        # times...)
        config = self.app.config

        # choose the output filename (either snake2camel, or through the xwiki_page_name_overrides
        # mapping)
        output_filename = None
        if (hasattr(config, 'xwiki_page_name_overrides')
            and (config.xwiki_page_name_overrides != None)
            and (docname in config.xwiki_page_name_overrides.keys())):
            # if there was an override, then use it.
            output_filename = os.path.join(self.outdir, config.xwiki_page_name_overrides[docname])
        else:
            # otherwise, do the standard snake2camel mapping.
            output_filename = os.path.join(self.outdir, snake2camel(docname) + ".xwiki")

        # check if there's a jinja template. If there is, then pass the page output through that
        # first.
        if hasattr(self, 'page_template'):
            writer_output = self.page_template.render(docname=docname, page_contents=writer_output)

        # write the file.
        output_file = codecs.open(output_filename, 'w', encoding="utf-8")
        output_file.write(writer_output.decode("utf-8"))
        output_file.close()


def setup(app):
    app.add_builder(XWikiBuilder)
    app.add_config_value('xwiki_root_page', '', 'env')
    app.add_config_value('xwiki_page_template', None, 'env')
    app.add_config_value('xwiki_page_name_overrides', None, 'env')
    return {
       'version': '1.0',
       'parallel_read_safe': True,
       'parallel_write_safe': True
    }

