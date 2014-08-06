CursorWordHighlighter
=====================

A Word Highlighter plug-in for Sublime Text 3
What it does
------------
With this plugin you will have automatically word highlighted with cursor, you don't need any hotkey and it works on Vim mode, non-Vim mode and mouse selecting.

Only available for Sublime Text 3
Install
-------
Use `Ctrl+Shift+P`(or `Cmd+Shift+P` on Mac) to open command palette, input `Browse Packages` to open the packages folder, or via menu `Preferences` > `Browse Packages`

Under the `Packages` folder, either copy files to `User` folder or create a new `CursorWordHighlighter` folder.
Options
-------
*   `"cursor_word_highlighter_enabled" : true`

    Enable or disable this plugin
*	`"cursor_word_highlighter_case_sensitive" : true`

	Case sensitive or not
*	`"cursor_word_highlighter_draw_outlined" : true`

	2 sytle of highlight has been provided, with draw outlined, plugin will only draw a outline instead of filling the words, vice versa.
*	`"cursor_word_highlighter_color_scope_name" : "comment"`

    This decide the color of highlight, options are `comment`, `string`, `invalid`, etc. You can reach them in your .tmTheme file.
*	`"cursor_word_highlighter_mark_occurrences_on_gutter" : false`

	If this comes true, it also marks all occurrences of highlighted words on the gutter bar.
	To customize the icons, the property `cursor_word_highlighter_icon_type_on_gutter` is helpful.

*	`"cursor_word_highlighter_icon_type_on_gutter" : dot`

	4 valid types: dot, circle, bookmark and cross.
Thanks
-------
Official `WordHighlight` plugin seems to do the similar job, but I couldn't get it work on mine, neither ST2 nor ST3, so I read its code and make this plugin, so you might also wanna check [WordHighlight][1]


  [1]: https://github.com/SublimeText/WordHighlight