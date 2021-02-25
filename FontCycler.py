import os
import sublime
import sublime_plugin


def next_font_from_settings(delta, user_settings_file, user_settings):
    pkg_settings_file = 'FontCycler.sublime-settings'
    pkg_settings = sublime.load_settings(pkg_settings_file)
    font_list = pkg_settings.get('font_list', [])
    font_index = pkg_settings.get('font_index', 0)
    if not font_list:
        sublime.status_message("FontCycle: There is no font to choose from")
        return

    font_list_length = len(font_list)
    if font_index >= font_list_length or font_index < 0:
        font_index = 0

    font_found = False
    user_font_face = user_settings.get('font_face')
    for i, _ in enumerate(font_list, font_index):
        index = i % font_list_length
        value = font_list[index]
        if not isinstance(value, dict):
            if type(value) != type(''):
                sublime.error_message(
                    "******************* FontCycler *******************\n"
                    "The elements of font_list must be a string or dict.")
            font_list[index] = { 'font_face': value }
        font_face = font_list[index].get('font_face')
        if not font_found and font_face == user_font_face:
            font_index = index
            font_found = True

    font_index += delta
    font_index %= font_list_length

    font = font_list[font_index]
    for key in (
        'font_face',
        'font_size',
        'line_padding_bottom',
        'line_padding_top',
        'word_wrap',
        'wrap_width'
    ):
        if key in font and user_settings.has(key):
            user_settings.set(key, font[key])

    pkg_settings.set('font_index', font_index)
    sublime.save_settings(user_settings_file)
    sublime.save_settings(pkg_settings_file)

    log_view_font(sublime.active_window().active_view().settings())


def log_view_font(view_settings):
    sublime.status_message('Font Face: %s:%d' % (
            view_settings.get('font_face'), view_settings.get('font_size')))

def get_syntax_special_file(view_settings):
    syntax, _ = os.path.splitext(os.path.basename(view_settings.get('syntax')))
    return syntax + '.sublime-settings'


class NextFontCommand(sublime_plugin.WindowCommand):
    def run(self, delta=1):
        view_settings = self.window.active_view().settings()
        syntax_special_file = get_syntax_special_file(view_settings)
        syntax_special = sublime.load_settings(syntax_special_file)
        if syntax_special.has('font_face'):
            next_font_from_settings(delta, syntax_special_file, syntax_special)
        else:
            preferences_file = 'Preferences.sublime-settings'
            preferences = sublime.load_settings(preferences_file)
            next_font_from_settings(delta, preferences_file, preferences)
