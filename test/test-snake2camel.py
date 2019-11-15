#!/usr/bin/env python3

import sys, re
from abstrys.sphinx_xwiki_builder import snake2camel

if __name__ == "__main__":
   print("Testing abstrys.sphinx_xwiki_builder.snake2camel:")

   test_data = [
       ("this-is-some-snake-cased-stuff", "ThisIsSomeSnakeCasedStuff"),
       ("this_is_some_snake_cased_stuff", "ThisIsSomeSnakeCasedStuff"),
       ("this-is_some-snake_cased-stuff", "ThisIsSomeSnakeCasedStuff"),
       ("This-Is_Some-Snake_Cased-Stuff", "ThisIsSomeSnakeCasedStuff"),
       ("ThisIsSomeSnakeCasedStuff", "Thisissomesnakecasedstuff"),
   ]

   for cur_test in test_data:
      in_str = cur_test[0]
      out_str = cur_test[1]
      test_out = snake2camel(in_str)
      test_result = "failed"
      if test_out == out_str:
         test_result = "passed"

      print("Input: %s, Expected: %s, Output: %s -- %s" % (in_str, out_str, test_out, test_result))

      if test_result == "failed":
         sys.exit(1)

   sys.exit(0)

