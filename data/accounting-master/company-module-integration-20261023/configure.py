"""Reuse the established preservation verifier with explicit successor changes."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
old=HERE.parent/'company-language-integration-20261023'
text=(old/'verify.py').read_text()
text=text.replace("allowed={'accounting-product-proposal.tex','chapters/06-language.tex','chapters/07-execution.tex','sections/company-path-authoring.tex'}",
    "allowed={'accounting-product-proposal.tex','chapters/06-language.tex','chapters/07-execution.tex','sections/company-family-language.tex'}")
text=text.replace("if added!={'sections/company-family-language.tex'}:","if added!={'sections/company-module-language.tex'}:")
text=text.replace('Version 3.54','Version 3.55').replace("'candidate_version':'3.54'","'candidate_version':'3.55'")
old_phrases="phrases=['Keeping company choices and their consequences together','A policy expression has units and dependencies','Available inputs do not establish a saved past calculation','Interrupted work differs from incomplete accounting']"
new_phrases="phrases=['Preserving a model before extending its accounts','Different bytes can express the same instruction','A module uses a company','Returned goods need their own carrying value','Tax history changes the cash needed at the close','The statement bridge must retain opening obligations','What the native extension must carry']"
assert old_phrases in text;text=text.replace(old_phrases,new_phrases)
assert not (HERE/'verify.py').exists();(HERE/'verify.py').write_text(text)
print('Successor verifier configured')
