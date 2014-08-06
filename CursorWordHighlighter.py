import re
import sublime, sublime_plugin


# Global variables
search_limit = 20000
file_size_limit = 4194304
settings = {}
word_separators = ''
highlighter_enabled = True
case_sensitive = True
draw_outline = True
color_scope = 'comment'
highlight_on_gutter = False
gutter_icon_type = ''
search_flags = sublime.LITERAL
draw_flags = sublime.DRAW_NO_FILL

def get_settings():
    global settings, highlighter_enabled, case_sensitive, draw_outline, color_scope
    global highlight_on_gutter, gutter_icon_type, search_flags, draw_flags, word_separators

    settings = sublime.load_settings('Preferences.sublime-settings')
    word_separators = settings.get('word_separators')
    highlighter_enabled = bool(settings.get('cursor_word_highlighter_enabled', True))
    case_sensitive = bool(settings.get('cursor_word_highlighter_case_sensitive', True))
    draw_outline = bool(settings.get('cursor_word_highlighter_draw_outlined', True))
    color_scope = settings.get('cursor_word_highlighter_color_scope_name', 'comment')
    highlight_on_gutter = bool(settings.get('cursor_word_highlighter_mark_occurrences_on_gutter', False))
    
    if highlight_on_gutter :
        gutter_icon_type = settings.get('cursor_word_highlighter_icon_type_on_gutter', 'dot')
    else:
        gutter_icon_type = ''

    if not case_sensitive :
        search_flags = sublime.IGNORECASE
    else:
        search_flags = sublime.LITERAL

    if not draw_outline :
        draw_flags = sublime.DRAW_NO_OUTLINE
    else:
        draw_flags = sublime.DRAW_NO_FILL

    return settings

def plugin_loaded():
    get_settings().add_on_change('Preferences-reload', get_settings)

class CursorWordHighlighterListener(sublime_plugin.EventListener):

    def on_post_text_command(self, view, command_name, args):
        if not highlighter_enabled:
            view.erase_regions("CursorWordHighlighter")
            return

        if view.size() <= file_size_limit :
            is_limited_size = False
        else:
            is_limited_size = True

        regions = []
        processedWords = []
        occurrencesMessage = []
        occurrencesCount = 0
        if command_name == 'drag_select' or command_name == 'move' or (command_name == 'set_motion' and "move" in args['motion']):
            for sel in view.sel():
                if sel.empty():
                    string = view.substr(view.word(sel)).strip()
                    if string not in processedWords:
                        processedWords.append(string)
                        if string and all([not c in word_separators for c in string]):
                                regions = self.find_regions(view, regions, string, is_limited_size)
                elif not sel.empty():
                    word = view.word(sel)
                    if word.end() == sel.end() and word.begin() == sel.begin():
                        string = view.substr(word).strip()
                        if string not in processedWords:
                            processedWords.append(string)
                            if string and all([not c in word_separators for c in string]):
                                    regions = self.find_regions(view, regions, string, is_limited_size)

                occurrences = len(regions)-occurrencesCount;
                if occurrences > 0:
                    occurrencesMessage.append(str(occurrences) + ' occurrence' + ('s' if occurrences != 1 else '') + ' of "' + string + '"')
                    occurrencesCount = occurrencesCount + occurrences

            view.erase_regions("CursorWordHighlighter")
            if regions:
                view.add_regions("CursorWordHighlighter", regions, color_scope, gutter_icon_type, draw_flags)
            else:
                view.erase_status("CursorWordHighlighter")

    def escape_regex(self, str):
        # Sublime text chokes when regexes contain \', \<, \>, or \`.
        # Call re.escape to escape everything, and then unescape these four.
        str = re.escape(str)
        for c in "'<>`":
            str = str.replace('\\' + c, c)
        return str

    def find_regions(self, view, regions, string, limited_size):
        # It seems as if \b doesn't pay attention to word_separators, but
        # \w does. Hence we use lookaround assertions instead of \b.
        # search = r'(?<!\w)'+self.escape_regex(string)+r'(?!\w)'
        search = self.escape_regex(string)
        if not limited_size:
            regions += view.find_all(search, search_flags)
        else:
            chars = search_limit
            visible_region = view.visible_region()
            begin = 0 if visible_region.begin() - chars < 0 else visible_region.begin() - chars
            end = visible_region.end() + chars
            from_point = begin
            while True:
                region = view.find(search, from_point)
                if region:
                    regions.append(region)
                    if region.end() > end:
                        break
                    else:
                        from_point = region.end()
                else:
                    break
        return regions