import sublime
import sublime_plugin
import re


def read_next_line(view, point):
    if (point >= view.size()):
        return

    next_line = view.line(point)
    return view.substr(next_line)


def write(view, strng):
    view.run_command(
        'insert_snippet', {
            'contents': strng
        }
    )


class PrefillParamsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        settings = sublime.load_settings("jsdocs.sublime-settings")
        point = v.sel()[0].end()
        indentSpaces = max(0, settings.get("indentation_spaces", 1))
        prefix = "\n*" + (" " * indentSpaces)
        out = []

        """ read the next line """
        line = read_next_line(v, point + 1)

        """ write the first linebreak and star. this sets the indentation for the following snippets """
        write(v, "\n *" + (" " * indentSpaces))

        """ if there is a line following this """
        if (line):
            """ match against a javascript function declaration. TODO: extend for other languages """
            res = re.search(
                #   fnName = function,  fnName : function
                '(?:(?P<name1>[a-zA-Z_$][a-zA-Z_$0-9]*)\s*[:=]\s*)?'
                + 'function'
                # function fnName
                + '(?:\s+(?P<name2>[a-zA-Z_$][a-zA-Z_$0-9]*))?'
                # (arg1, arg2)
                + '\s*\((?P<args>.*)\)',
                line
            )
            if (res):
                """ grab the name out of "name1 = function name2(foo)" preferring name1 """
                name = res.group('name1') or res.group('name2')
                out.append("${1:%s description}" % (name))

                """ if there are arguments, add a @param for each """
                args = res.group('args')
                if (args):
                    """ remove comments inside the argument list. """
                    args = re.sub("/\*.*?\*/", '', args)
                    for count, arg in enumerate(re.split('\s*,\s*', args)):
                        index = (count + 1) * 2
                        out.append("@param {${%d:type}} %s ${%d:description}" % (index, arg, index + 1))

                """ unless the function starts with 'set' or 'add', add a @return tag """
                if not re.match('[$_]?(?:set|add)[A-Z_]', name):
                    out.append("@return {${%d:type}}" % (index + 2))

                write(v, prefix.join(out) + "\n*/")

        """ if there was no line, or no match, then just close the comment and carry on"""
        if not line or not res:
            write(v, "$0\n*/")
