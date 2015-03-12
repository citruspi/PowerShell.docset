all: docset

dependencies:

	pip install -r requirements.txt

clean:

	rm -f PowerShell.docset/Contents/Resources/Documents/*.html
	rm -f PowerShell.docset/Contents/Resources/docSet.dsidx
	touch PowerShell.docset/Contents/Resources/Documents/.gitkeep

docset: clean

	python build.py

.PHONY: clean docset dependencies
