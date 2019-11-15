###########
Markup test
###########

.. contents:: On this page
   :local:

This Sphinx topic has a number of marked-up stuff to test the XWiki Builder. All the elements in
this topic are known to work correctly, so if anything *doesn't* render correctly, then it's a bug.

The XWiki syntax I'm using is `defined here <http://rendering.xwiki.org/xwiki/bin/view/XWiki/XWikiSyntax?syntax=2.1>`__.

----

That was a transition, you see...

Let's get right down to it.

.. _test-inline:

Inline markup
=============

How about some inline markup?

These are implicitly marked-up:

* **bold**
* *italic*
* ``literal``
* ** ``literal-bold`` **

These, on the other hand, use Docutils / Sphinx roles:

* :strong:`strong`
* :emphasis:`emphasis`
* :literal:`literal`
* :subscript:`sub`\ script
* :superscript:`super`\ script
* :title-reference:`title-reference`
* :command:`command`
* :file:`file`
* :guilabel:`guilabel`
* :kbd:`kbd`
* :menuselection:`Start --> Programs`
* :program:`program`
* :samp:`Something {replaceable}`

.. _test-images:

Images
======

An image:

.. image:: _static/heclawte-logo-1000.png

Did you also know that you can put images (like this one: |birdboy|) inline with a substitution?

.. |birdboy| image:: _static/birdboy.png


.. _test-lists:

Lists
=====

Here's some list markup!


.. _test-lists-bullet:

Bullet lists
------------

* This is the first list item

  * Here's a sub-list item.
  * Another sub-list item.

* A second top-level list item, perhaps with a series of steps!

  #. Step 1
  #. Step 2
  #. Step 3

* You can nest lists

  * as deeply

    * as

      * you want

* Lists can have more than one paragraph per item.

  As seen here.

  And this list item can also have sub-lists:

  * Apple
  * Orange
  * Mango
  * Fish

    What's *that* doing there?


.. _test-lists-definition:

Definition lists
----------------

This is a term
    This is its definition.

This is another term
    It has a different definition.


.. _test-headings-inline:

Headings with ``literal``, *emphasis* or **bold**
==================================================

That's also possible in Sphinx.

.. _test-code:

Code
====

We already gave examples of :code:`inline code`, but what about code blocks?

Here's a standard code-block::

   grep -i myterm *.rst

And here's a code-block directive (in Python):

.. code-block:: python

   print("Hello, " + name)

Finally, a parsed-literal:

.. parsed-literal::

   :samp:`print("Hello, {name}")`


.. _test-tables:

Tables
======

Here's a simple table:

+-----+------+-------+
| red | blue | green |
+-----+------+-------+

One with a header:

.. list-table::
   :header-rows: 1

   * - Setting
     - Value

   * - gender
     - male

   * - catname
     - Purr

   * - dogname
     - Grrr

   * - horsename
     - Nhrr

   * - DECGraphics
     - *true*

   * - color
     - *true*


Stub columns:

.. list-table::
   :stub-columns: 1

   * - gender
     - male

   * - catname
     - Purr

   * - dogname
     - Grrr

   * - horsename
     - Nhrr

   * - DECGraphics
     - *true*

   * - color
     - *true*


.. _test-admonitions:

Admonitions
===========

.. note:: This is a normal note.

.. tip:: This is a tip.

   With some content.

.. warning:: This is a warning.


.. _test-block-quotes:

Block quotes
============

In reStructuredText, a block-quote is simply an indented bit in the flow of text.

    This is something a person said once to me.

For example.


See also
========

* :doc:`test-page-2`

