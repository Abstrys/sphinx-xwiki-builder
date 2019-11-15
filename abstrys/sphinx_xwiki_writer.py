# -*- coding: utf-8 -*-
#===============================================================================
#
# Sphinx XWiki Writer
#
# A module for docutils that converts from a doctree to XWiki output.
#
# by Eron Hennessey <eron@abstrys.com>
#
# This writer is somewhat based on my Markdown writer:
#
# * https://github.com/Abstrys/rst2db/blob/master/abstrys/docutils_ext/markdown_writer.py
#
# The syntax written is based on the syntax described here:
#
# * http://rendering.xwiki.org/xwiki/bin/view/XWiki/XWikiSyntax?syntax=2.1
#
#===============================================================================

import sys, os
import re
from docutils import nodes, writers

def print_error(text, node=None):
    """
    Prints an error string and optionally, the node being worked on.
    """
    sys.stderr.write("\n%s: %s\n" % (__name__, text))
    if node:
        sys.stderr.write("  node: %s\n" % str(node))

def test_popped_node(expected, popped, list_type="group"):
    """
    Tests two nodes and complains if they're not the same.
    """
    if (expected != popped):
        print_error("A different %s node was popped than expected!\nexpected: %s\npopped: %s" %
           (list_type, expected, popped))


def node_is_inline(node):
    """
    Test if a node is in an "inline" context.
    """
    return node.parent.tagname in ['paragraph']


class XWikiWriter(writers.Writer):
    """
    A docutils writer for XWiki.
    """

    # class data
    supported = ('markdown',)
    output = None

    def __init__(self, sphinx_config=None):
        """
        Initialize the writer. Takes the root element of the resulting XWiki output as its sole
        argument.
        """
        writers.Writer.__init__(self)
        self.translator_class = XWikiTranslator
        self.sphinx_config = sphinx_config

    def translate(self):
        visitor = self.translator_class(self.document, self.sphinx_config)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class XWikiTranslator(nodes.NodeVisitor):
    """
    A docutils translator for XWiki.
    """

    def __init__(self, document, sphinx_config=None):
        """
        Initialize the translator.
        """
        nodes.NodeVisitor.__init__(self, document)
        self.body_content = ""
        self.para_text = ""
        self.para_level = 0
        self.group_stack = [] # a list of group nodes
        self.list_glyph_stack = [] # a stack of list glyphs.
        self.section_level = 0
        self.sphinx_config = sphinx_config
        self.force_inline = False


    def _add_text(self, text):
        """
        Called to add text to the document.
        """
        if self.para_level > 0:
            self.para_text += text
        elif len(self.group_stack) > 0:
            self._add_text_block_to_group(text)
        else:
            self.body_content += text


    #
    # group handling methods
    #
    def _push_group(self, node, prefix=""):
        """
        pushes a new group (groups can be nested) on the group stack, and starts a new group.
        """
        self.group_stack.append({'node': node, 'prefix': prefix, 'blocks': []})


    def _add_text_block_to_group(self, block_text):
        """
        Adds a block of text to the group. It will be added to the body_content when popped.
        """
        block_text = block_text.strip()
        if len(block_text) > 0:
            self.group_stack[-1]['blocks'].append(block_text)


    def _pop_group(self, postfix=""):
        """
        pops the current group off the group stack, and ends the group.
        """
        popped_group = self.group_stack.pop()
        group_text = popped_group['prefix'] + "((( "
        for block in popped_group['blocks']:
            group_text += block
            # only add newlines to the blocks *before* the last one.
            if group_text.endswith(")))") or group_text.endswith('%)'):
                group_text += "\n"
            elif block != popped_group['blocks'][-1]:
                group_text += "\n\n"
        # end the group.
        group_text += (" )))" + postfix)
        self._add_text(group_text)
        return popped_group['node']


    # different types of admonitions are set up similarly.
    def _start_admonition(self, node, title, color):
        self._add_text('(% class="admonition {0}" style="border-style:solid;border-color:{1};border-width:2px 2px 2px 8px;margin:16px;padding:16px 16px 8px 16px" %)'.format(title.lower(), color))
        self._push_group(node)
        self._add_text('**%s**\n' % title)

    def _end_admonition(self, node):
        # don't test the popped node here (in some cases, we need to start the
        # admonition on a different node, such as the title).
        self._pop_group(postfix="\n\n")

    #
    # Overrides of Nodevisitor methods.
    #

    def astext(self):
        """
        Return the entire document as text.
        """
        return self.body_content


    # handle unknown nodes...
    def unknown_visit(self, node):
        print_error("WARNING:: Visiting unknown node!", node)

    def unknown_departure(self, node):
        print_error("WARNING:: Departing unknown node!", node)


    # handle "problematic" nodes...
    def visit_problematic(self, node):
        print_error("found problematic node!", node)

    def depart_problematic(self, node):
        pass


    #
    # the document itself
    #
    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    #
    # document parts
    #
    def visit_Text(self, node):
        text = node.astext()
        if (node.parent != None) and (node.parent.tagname == "paragraph") and ('\n' in text):
            # strip any newlines from within a paragraph...
            text = ' '.join(text.split('\n'))
        self._add_text(text)

    def depart_Text(self, node):
        pass


    def visit_raw(self, node):
        # raw elements are identified by their 'format'. XWiki handles these as:
        # {{format}}
        # .. content in that format ..
        # {{/format}}
        if 'format' in node:
            self._add_text("\n{{%s}}\n" % node['format'])

    def depart_raw(self, node):
        if 'format' in node:
            self._add_text("\n{{/%s}}\n\n" % node['format'])


    def visit_paragraph(self, node):
        self.para_level += 1
        if (self.para_level > 1):
            print_error("nested paragraph!", node)
            sys.stderr.write("  parent: %s\n" % str(node.parent))


    def depart_paragraph(self, node):
        self.para_level -= 1
        # don't add a newline when:
        # * the last para in a group.
        # add two newlines when:
        # * any para except the last in a group.
        # * the end of paras not in a group.
        if len(self.group_stack) > 0:
            # if in a group, just add it to the blocks within the group.
            self._add_text_block_to_group(self.para_text)
        else:
            # otherwise, just add it to the document.
            self._add_text(self.para_text + "\n\n")
        # do this in all cases.
        self.para_text = ""


    def visit_section(self, node):
        self.section_level += 1
        # if the section has any IDs, write them here.
        # Yes, Sphinx allows multiple IDs per section: the automatic ID created
        # from the section title and possibly another defined by the writer and
        # used in :ref: links.
        for section_id in node['ids']:
            # adding a blank line between these definitions (but none before the
            # following title) allows multiple IDs to refer to the same section.
            self._add_text('\n(% id="{}" %)\n'.format(section_id))

    def depart_section(self, node):
        self.section_level -= 1


    def visit_compound(self, node):
        # This is just like a group.
        self._push_group(node)

    def depart_compound(self, node):
        test_popped_node(node, self._pop_group())


    def visit_line_block(self, node):
        # this is just like a group.
        self._push_group(node)

    def depart_line_block(self, node):
        test_popped_node(node, self._pop_group())


    def visit_line(self, node):
        # a line within a line block. Nothing to do here.
        pass

    def depart_line(self, node):
        self._add_text('\n')


    def visit_caption(self, node):
        self.visit_paragraph(node)

    def depart_caption(self, node):
        self.depart_paragraph(node)


    def visit_rubric(self, node):
        print_error("visit_rubric", node)
        self.visit_paragraph(node)

    def depart_rubric(self, node):
        print_error("depart_rubric", node)
        self.depart_paragraph(node)


    def visit_meta(self, node):
        if 'name' in node:
            if node['name'] == 'keywords':
                self.page_keywords = node['content'].split(', ')
            elif node['name'] == 'description':
                raise nodes.SkipNode
            else:
                print_error("Unknown meta", node)
        else:
            print_error("Unknown meta", node)

    def depart_meta(self, node):
        pass


    #
    # standard (bulleted/numbered) lists
    #

    def visit_bullet_list(self, node):
        self.list_glyph_stack.append("* ")
        self.first_list_item = True

    def depart_bullet_list(self, node):
        self.list_glyph_stack.pop()
        self._add_text("\n")


    def visit_enumerated_list(self, node):
        self.list_glyph_stack.append("1. ")
        self.first_list_item = True

    def depart_enumerated_list(self, node):
        self.list_glyph_stack.pop()
        self._add_text("\n")


    def visit_list_item(self, node):
        self._push_group(node, prefix=(self.list_glyph_stack[-1]))

    def depart_list_item(self, node):
        test_popped_node(node, self._pop_group("\n"))


    #
    # hlist: this acts like a single-row table in which each column is a table
    # cell.
    #
    def visit_hlist(self, node):
        # each hlist is a table row.
        self.table_in_thead = False
        self.visit_row(node)

    def depart_hlist(self, node):
        self.depart_row(node)

    def visit_hlistcol(self, node):
        # each column is an "entry"
        self.visit_entry(node)

    def depart_hlistcol(self, node):
        self.depart_entry(node)


    #
    # definition lists and associated nodes
    #

    def visit_definition_list(self, node):
        """
        This is handled by the visit_term, then visit_definition elements.
        """
        pass

    def depart_definition_list(self, node):
        """
        This is handled by the depart_term, then depart_definition elements.
        """
        pass

    def visit_definition_list_item(self, node):
        """
        This is handled by the visit_term, then visit_definition elements.
        """
        pass

    def depart_definition_list_item(self, node):
        """
        This is handled by the depart_term, then depart_definition elements.
        """
        self._add_text("\n\n")


    def visit_term(self, node):
        self._add_text("; ")

    def depart_term(self, node):
        self._add_text("\n")


    def visit_definition(self, node):
        self._push_group(node, prefix=": ")

    def depart_definition(self, node):
        test_popped_node(node, self._pop_group())


    # emphasis
    def visit_emphasis(self, node):
        self._add_text("//")

    def depart_emphasis(self, node):
        self._add_text("//")

    # strong
    def visit_strong(self, node):
        self._add_text("**")

    def depart_strong(self, node):
        self._add_text("**")


    # subscript
    def visit_subscript(self, node):
        self._add_text(",,")

    def depart_subscript(self, node):
        self._add_text(",,")


    # superscript
    def visit_superscript(self, node):
        self._add_text("^^")

    def depart_superscript(self, node):
        self._add_text("^^")


    # transition
    def visit_transition(self, node):
        self._add_text("----\n\n")
        raise nodes.SkipNode

    def depart_transition(self, node):
        # does nothing.
        pass

    #
    # images and figures
    #

    def _add_image(self, uri, alt_text="", caption=None, inline=False):
        # strip local paths out of the URI if they exist.
        if not re.match('^htt[p|ps]:\/\/', uri):
            # must be local, then. Grab only the second part of os.path.split (the filename itself).
            uri = os.path.split(uri)[1]
        # set the postfix depending on whether it's inline or not.
        if caption:
            text = '[[image:%s||alt="%s" title="%s")]]' % (uri, alt_text, caption)
        else:
            text = '[[image:%s||alt="%s"]]' % (uri, alt_text)
        self._add_text(text + ("" if inline else "\n\n"))


    def _get_image_attrs(self, node):
        """
        Returns a tuple: (uri, alt)
        """
        alt_text = ""
        uri = ""
        if 'alt' in node:
            alt_text = node['alt']
        if 'uri' in node:
            uri = node['uri']
        return (uri, alt_text)


    def visit_image(self, node):
        (uri, alt_text) = self._get_image_attrs(node)
        self._add_image(uri, alt_text, inline=node_is_inline(node))

    def depart_image(self, node):
        # does nothing.
        pass


    def visit_figure(self, node):
        caption = ""
        alt_text = ""
        uri = ""
        for c in node.children:
            if type(c).__name__ == 'caption':
                caption = c.astext()
            elif type(c).__name__ == 'image':
                (uri, alt_text) = self._get_image_attrs(c)
        self._add_image(uri, alt_text, caption=caption, inline=node_is_inline(node))

    def depart_figure(self, node):
        # does nothing.
        pass


    #
    # notes and various other admonitions
    #

    # generic admonition - this always contains a title.
    def visit_admonition(self, node):
        # we'll defer this to visit_title.
        pass

    def depart_admonition(self, node):
        # but deal w/ ending the admonition here.
        self._end_admonition(node)


    # hint
    def visit_hint(self, node):
        self._start_admonition(node, "Hint", 'green')

    def depart_hint(self, node):
        self._end_admonition(node)


    # important
    def visit_important(self, node):
        self._start_admonition(node, "Important", "red")

    def depart_important(self, node):
        self._end_admonition(node)


    # note
    def visit_note(self, node):
        self._start_admonition(node, "Note", "blue")

    def depart_note(self, node):
        self._end_admonition(node)


    # tip
    def visit_tip(self, node):
        self._start_admonition(node, "Tip", "green")

    def depart_tip(self, node):
        self._end_admonition(node)

    # warning
    def visit_warning(self, node):
        self._start_admonition(node, "Warning", "orange")

    def depart_warning(self, node):
        self._end_admonition(node)


    # topics (can be a number of things)
    def visit_topic(self, node):
        # add whatever classes come w/ the topic ("contents", etc.).
        classes = ' '.join(node['classes']).strip()
        if 'contents local' in classes:
            # float local contents to the right.
            self._add_text('(% class="{0}" style="border-style:solid;background-color:white;border-color:gray;border-width:2px;margin:16px;padding:16px 16px 8px 16px;float:right;clear:right;" %)\n'.format(classes))
        elif classes == '':
            self._add_text('(% class="topic {0}" style="border-style:solid;border-color:gray;border-width:2px;margin:16px;padding:16px 16px 8px 16px" %)\n'.format(classes))
        else:
            self._add_text('(% class="{0}" style="border-style:solid;border-color:gray;border-width:2px;margin:16px;padding:16px 16px 8px 16px" %)\n'.format(classes))
        self._push_group(node)


    def depart_topic(self, node):
        test_popped_node(node, self._pop_group(postfix="\n\n"))


    # literal inlines
    def visit_literal(self, node):
        # a literal, by definition, cannot have any markup within it, so convert it to regular text
        # and add '##' around it.
        self._add_text("##%s##" % node.astext())
        raise nodes.SkipNode

    def depart_literal(self, node):
        # nothing happens here.
        pass


    def visit_literal_strong(self, node):
        # not a normal reST element; this is added by Sphinx.
        self._add_text("**##%s##**" % node.astext())
        raise nodes.SkipNode

    def depart_literal_strong(self, node):
        # nothing happens here.
        pass


    def visit_inline(self, node):
        # general role handling (if it doesn't map to a standard inline).
        # this depends on the type of "class" the inline is.
        if 'guilabel' in node['classes']:
            self.visit_strong(node) # treat it like a **strong** element.
        elif 'menuselection' in node['classes']:
            self.visit_strong(node) # treat it like a **strong** element.
        elif 'std-ref' in node['classes']:
            self.visit_emphasis(node) # treat it like an **italic** element.
        elif 'doc' in node['classes']:
            self.visit_emphasis(node) # treat it like an **italic** element.
        else:
            # don't do anything special
            pass

    def depart_inline(self, node):
        if 'guilabel' in node['classes']:
            self.depart_strong(node) # treat it like a **strong** element.
        elif 'menuselection' in node['classes']:
            self.depart_strong(node) # treat it like a **strong** element.
        elif 'std-ref' in node['classes']:
            self.depart_emphasis(node) # treat it like an **italic** element.
        elif 'doc' in node['classes']:
            self.depart_emphasis(node) # treat it like an **italic** element.
        else:
            # don't do anything special
            pass


    def visit_literal_block(self, node):
        #print_error("literal_block" % node.parent, node)
        #if hasattr(node, 'get_children'):
        #    print_error("literal block has children! %s" % node.get_children())
        code_class = ""
        if ('classes' in node) and ('code' in node['classes']):
            code_class = node['classes'][1]
        elif ('language' in node):
            code_class = node['language']
        self._add_text('(% style="background:gainsboro;margin:16px;padding:16px" %)\n')
        self._add_text("{{{\n")

    def depart_literal_block(self, node):
        self._add_text("\n}}}\n\n")


    # option_list
    def visit_option(self, node):
        self._add_text("<option>")

    def depart_option(self, node):
        self._add_text("</option>")


    def visit_option_argument(self, node):
        self._add_text("<optionarg>")

    def depart_option_argument(self, node):
        self._add_text("</optionarg>")


    def visit_option_group(self, node):
        self._add_text("<optiongroup>")

    def depart_option_group(self, node):
        self._add_text("</optiongroup>")


    def visit_option_list(self, node):
        self._add_text("<optionlist>")

    def depart_option_list(self, node):
        self._add_text("</optionlist>")


    def visit_option_list_item(self, node):
        self._add_text("<optionlistitem>")

    def depart_option_list_item(self, node):
        self._add_text("</optionlistitem>")


    def visit_option_string(self, node):
        self._add_text("<optionstring>")

    def depart_option_string(self, node):
        self._add_text("</optionstring>")

    #
    # links and references
    #
    def visit_reference(self, node):
        self.force_inline = True
        self._add_text("[[")

    def depart_reference(self, node):
        if 'refuri' in node:
            refuri = node['refuri']
            link_contents = ''
            if ('internal' in node) and (node['internal'] == True):
                # links to another page in this doc set. Make sure to add the
                # xwiki_root_page to the reference, if set.
                xwiki_root_page = ''
                if hasattr(self.sphinx_config, 'xwiki_root_page'):
                    xwiki_root_page = self.sphinx_config.xwiki_root_page
                if '#' in refuri:
                    # here, we need to split any anchor reference from the link
                    # so it can be formatted xwiki-style.
                    page_name, refid = refuri.split('#')
                    if (xwiki_root_page != '') and (page_name == 'Index'): # special case for the index page.
                        page_name = xwiki_root_page # the root page *is* the "index".
                    else:
                        # make it a sub-page of the root.
                        page_name = '.'.join([xwiki_root_page, page_name])
                    link_contents = '{0}||anchor="{1}"'.format(page_name,  refid)
                else:
                    if (xwiki_root_page != '') and (refuri == 'Index'): # special case for the index page.
                        link_contents = xwiki_root_page # the root page *is* the "index".
                    else:
                        # make it a sub-page of the root.
                        link_contents = '.'.join([xwiki_root_page, refuri])
            else:
                # an external link. Just use the refuri as-is.
                link_contents = refuri

            # write the link
            if link_contents == node.astext():
                # special case where the link text and URI are the same.
                self._add_text(']]')
            else:
                # add the destination for the link.
                self._add_text('>>{0}]]'.format(link_contents))
        elif 'refid' in node:
            # this is a link on the current page.
            self._add_text('>>||anchor="{0}"]]'.format(node['refid']))
        else:
            print_error("depart reference: what is this?", node)
        self.force_inline = False
        self.ref_title = None


    def visit_target(self, node):
        # These are the equivalent of <a id="target-id"/> elements in HTML.
        # However, the "refid" that is provided here is also added to the list
        # of "ids" in the section that will invariably follow this, so
        # processing is deferred to the section
        pass

    def depart_target(self, node):
        pass


    # table
    def visit_table(self, node):
        # nothing to do here presently.
        #print_error('visit_table', node)
        #sys.stderr.write('  parent: %s\n' % node.parent)
        pass

    def depart_table(self, node):
        self._add_text("\n\n")


    def visit_tgroup(self, node):
        self.table_cols = int(node['cols'])
        self.table_col_widths = []
        self.table_stub_cols = []
        self.table_in_thead = False

    def depart_tgroup(self, node):
        pass


    def visit_colspec(self, node):
        self.table_col_widths.append(int(node['colwidth']))
        if node.has_key('stub') and (node['stub'] == '1'):
            self.table_stub_cols.append(True)
        else:
            self.table_stub_cols.append(False)

    def depart_colspec(self, node):
        pass


    def visit_tbody(self, node):
        pass

    def depart_tbody(self, node):
        pass


    def visit_thead(self, node):
        # deferred to visit_entry
        self.table_in_thead = True

    def depart_thead(self, node):
        self.table_in_thead = False


    def visit_entry(self, node):
        if self.table_in_thead:
            self._push_group(node, prefix="|= ")
        else:
            self._push_group(node, prefix="| ")

    def depart_entry(self, node):
        test_popped_node(node, self._pop_group(postfix=" "))


    def visit_row(self, node):
        pass

    def depart_row(self, node):
        self._add_text("\n")


    # title
    def visit_title(self, node):
        # some titles aren't section headings...
        if (node.parent.tagname in ['topic']):
            self._add_text("**%s**" % node.astext())
            raise nodes.SkipNode
        if (node.parent.tagname in ['admonition']):
            self._start_admonition(node, node.astext(), 'blue')
            raise nodes.SkipNode
        else: # but others are...
            self._add_text(("=" * self.section_level) + " ")

    def depart_title(self, node):
        self._add_text(" " + ("=" * self.section_level))
        self._add_text("\n\n")


    def visit_substitution_definition(self, node):
        # ignore these...
        raise nodes.SkipNode

    def depart_substitution_definition(self, node):
        pass


    def visit_comment(self, node):
        # ignore comments.
        raise nodes.SkipNode

    def depart_comment(self, node):
        pass


    def visit_compact_paragraph(self, node):
        # we need to determine if this compact para is used for grouping or if
        # it's an actual para.
        if node.parent.tagname in ['compound']:
            self._push_group(node)
        else:
            self.visit_paragraph(node)

    def depart_compact_paragraph(self, node):
        if node.parent.tagname in ['compound']:
            test_popped_node(node, self._pop_group())
        else:
            self.depart_paragraph(node)


    def visit_block_quote(self, node):
        # block quotes are styled block elements that may contain paras, tables, etc.
        # We consider it to be a styled group.
        self._add_text('(% style="border-left:solid gainsboro 8px;margin:16px;padding:16px 16px 8px 16px" %)\n')
        self._push_group(node)

    def depart_block_quote(self, node):
        test_popped_node(node, self._pop_group(postfix="\n\n"))


    # title_reference
    def visit_title_reference(self, node):
        self.visit_emphasis(node)

    def depart_title_reference(self, node):
        self.depart_emphasis(node)

