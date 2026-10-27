The second attempt calculated all consequences and passed 334 checks, but three
original-PDF comparisons failed because the PDF extractor relocates superscripts.
Normal-resolution inspection of original pages 39/40 shows `(1)` on the Level 2
heading and `(2)(3)`/`(3)` on Total. PyMuPDF puts those markers near the footer.
The next attempt splits punctuation for the full token-population comparison and
checks Total's marker separately before comparing that row without its marker.
No number, header, footnote or source assertion is discarded or changed.
