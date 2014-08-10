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
search_flags = 0
draw_flags = sublime.DRAW_NO_FILL

color_highlight_scopes = ['entity.name.class', 'support.function', 'variable.parameter', 'invalid.deprecated', 'invalid', 'string']

def plugin_loaded():
    get_settings().add_on_change('Preferences-reload', get_settings)

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
        search_flags = 0

    if not draw_outline :
        draw_flags = sublime.DRAW_NO_OUTLINE
    else:
        draw_flags = sublime.DRAW_NO_FILL

    return settings

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

    def find_regions(self, view, regions, string, limited_size):
        search = r'(?<!\w)'+string+r'(?!\w)'
        if not limited_size:
            regions = view.find_all(search, search_flags)
        else:
            chars = search_limit
            visible_region = view.visible_region()
            begin = 0 if visible_region.begin() - chars < 0 else visible_region.begin() - chars
            end = visible_region.end() + chars
            from_point = begin
            while True:
                region = view.find(search, from_point, search_flags)
                if region:
                    regions.append(region)
                    if region.end() > end:
                        break
                    else:
                        from_point = region.end()
                else:
                    break
        return regions

class PersistentHighlightWordsCommand(sublime_plugin.WindowCommand):
    def get_words(self, text):
        return text.split()

    def run(self):
        view = self.window.active_view()
        if not view:
            return
        word_list = self.get_words(view.settings().get('cursor_word_highlighter_persistant_highlight_text', ''))
        for region in view.sel():
            cursor_word = view.substr(view.word(region)).strip()
            if cursor_word:
                if cursor_word in word_list:
                    word_list.remove(cursor_word)
                else:
                    word_list.append(cursor_word)
                break
        display_list = ' '.join(word_list)
        self.highlight(display_list)

    def highlight(self, text):
        self.window.run_command('persistent_unhighlight_words')
        view = self.window.active_view()
        words = self.get_words(text)
        regions = []
        size = 0
        word_set = set()
        for word in words:
            if len(word) < 2 or word in word_set:
                continue
            word_set.add(word)
            search = r'(?<!\w)'+word+r'(?!\w)'
            regions = view.find_all(search, search_flags)
            highlightName = 'cursor_word_highlighter_persistant_highlight_word_%d' % size
            view.add_regions(highlightName, regions, color_highlight_scopes[size % len(color_highlight_scopes)] , '', sublime.DRAW_SOLID_UNDERLINE)
            size += 1
        view.settings().set('cursor_word_highlighter_persistant_highlight_size', size)
        view.settings().set('cursor_word_highlighter_persistant_highlight_text', text)

class PersistentUnhighlightWordsCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if not view:
            return
        size = view.settings().get('cursor_word_highlighter_persistant_highlight_size', 0)
        for i in range(size):
            view.erase_regions('cursor_word_highlighter_persistant_highlight_word_%d' % i)
        view.settings().set('cursor_word_highlighter_persistant_highlight_size', 0)
        view.settings().erase('cursor_word_highlighter_persistant_highlight_text')