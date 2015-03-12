clean:

	rm -f PowerShell.docset/Contents/Resources/Documents/*.html
	rm -f PowerShell.docset/Contents/Resources/docSet.dsidx
	touch PowerShell.docset/Contents/Resources/Documents/.gitkeep

.PHONY: clean
