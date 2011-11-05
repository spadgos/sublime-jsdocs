"""
JSDocs v1.3.0
by Nick Fisher
https://github.com/spadgos/sublime-jsdocs
"""
import sublime
import sublime_plugin
import re
import string


def read_line(view, point):
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


def counter():
    count = 0
    while True:
        count += 1
        yield(count)


def escape(str):
    return string.replace(str, '$', '\$')


def is_numeric(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def guessType(val):
    if not val or val == '':  # quick short circuit
        return '[type]'
    if is_numeric(val):
        return "Number"
    if val[0] == '"' or val[0] == "'":
        return "String"
    if val[0] == '[':
        return "Array"
    if val[0] == '{':
        return "Object"
    if val == 'true' or val == 'false':
        return 'Boolean'
    if re.match('RegExp\\b|\\/[^\\/]', val):
        return 'RegExp'
    if val[:4] == 'new ':
        res = re.search('new ([a-zA-Z_$][a-zA-Z_$0-9]*)', val)
        return res.group(1)
    return '[type]'


class JsdocsCommand(sublime_plugin.TextCommand):

    def run(self, edit, inline=False):
        v = self.view
        settings = v.settings()
        point = v.sel()[0].end()
        indentSpaces = max(0, settings.get("jsdocs_indentation_spaces", 1))
        alignTags = settings.get("jsdocs_align_tags", True)
        prefix = "\n*" + (" " * indentSpaces)

        self.inline = inline

        # part of a regex. this detects a valid identifier
        self.identifier = '[a-zA-Z_$][a-zA-Z_$0-9]*'

        # read the next line
        line = read_line(v, point + 1)
        out = None

        # if there is a line following this
        if line:
            if self.isExistingComment(line):
                write(v, "\n *" + (" " * indentSpaces))
                return
            # match against a javascript function declaration. TODO: extend for other languages
            out = self.parseFunction(line) \
                or self.parseVar(line)

        if out and alignTags and not self.inline:
            maxWidth = 0
            regex = re.compile("(@\S+)")
            for line in out:
                res = regex.match(line)
                if res:
                    maxWidth = max(maxWidth, res.end())

            for index, line in enumerate(out):
                res = regex.match(line)
                if res:
                    out[index] = line[:res.end()] \
                        + (" " * (1 + maxWidth - res.end())) \
                        + line[res.end():].strip(' \t')

        if self.inline:
            if out:
                write(v, " " + out[0] + " */")
            else:
                write(v, " $0 */")
        else:
            # write the first linebreak and star. this sets the indentation for the following snippets
            write(v, "\n *" + (" " * indentSpaces))
            if out:
                write(v, prefix.join(out) + "\n*/")
            else:
                write(v, "$0\n*/")

    def parseFunction(self, line):

        res = re.search(
            #   fnName = function,  fnName : function
            '(?:(?P<name1>' + self.identifier + ')\s*[:=]\s*)?'
            + 'function'
            # function fnName
            + '(?:\s+(?P<name2>' + self.identifier + '))?'
            # (arg1, arg2)
            + '\s*\((?P<args>.*)\)',
            line
        )
        if not res:
            return None

        self.inline = False  # because wtf is an inline function docblock?

        settings = self.view.settings()
        extraTags = settings.get('jsdocs_extra_tags', [])

        # grab the name out of "name1 = function name2(foo)" preferring name1
        name = escape(res.group('name1') or res.group('name2') or '')
        args = res.group('args')
        isClass = re.match("[A-Z]", name)
        tabIndex = counter()
        out = []

        out.append("${%d:[%s description]}" % (tabIndex.next(), name))
        if isClass:
            out.append("@class ${%d:[description]}" % (tabIndex.next()))

        def replaceUserTabs(m):
            return "%s%d%s" % (m.group(1), tabIndex.next(), m.group(2))

        for index, extra in enumerate(extraTags):
            extraTags[index] = re.sub("(\$\{)\d*(:[^}]+})", replaceUserTabs, extra)
        out.extend(extraTags)

        # if there are arguments, add a @param for each
        if (args):
            # remove comments inside the argument list.
            args = re.sub("/\*.*?\*/", '', args)
            for arg in re.split('\s*,\s*', args):
                out.append("@param {${%d:[type]}} %s ${%d:[description]}" % (
                    tabIndex.next(),
                    escape(arg.strip()),
                    tabIndex.next()
                ))

        if not isClass:
            # unless the function starts with 'set' or 'add', add a @return tag
            if not re.match('[$_]?(?:set|add)[A-Z_]', name):
                retType = '[type]'
                if re.match('[$_]?(?:is|has)[A-Z_]', name):  # functions starting with 'is' or 'has'
                    retType = 'Boolean'
                out.append("@return {${%d:%s}}" % (tabIndex.next(), retType))

        return out

    def parseVar(self, line):
        res = re.search(
            #   var foo = blah,
            #       foo = blah;
            #   baz.foo = blah;
            #   baz = {
            #        foo : blah
            #   }

            '\\b(?P<name>' + self.identifier + ')\s*[=:]\s*(?P<val>.*?)(?:[;,]|$)',
            line
        )
        if not res:
            return None

        out = []
        name = res.group('name')
        val = res.group('val').strip()
        tabIndex = counter()

        valType = guessType(val)
        if self.inline:
            out.append("@type {${%d:%s}} ${%d:[description]}" % (tabIndex.next(), valType, tabIndex.next()))
        else:
            out.append("${%d:[%s description]}" % (tabIndex.next(), name))
            out.append("@type {${%d:%s}}" % (tabIndex.next(), valType))

        return out

    def isExistingComment(self, line):
        return re.search('^\\s*\\*', line)


class JsdocsIndentCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        currPos = v.sel()[0].begin()
        currLineRegion = v.line(currPos)
        currCol = currPos - currLineRegion.begin()  # which column we're currently in
        prevLine = v.substr(v.line(v.line(currPos).begin() - 1))
        spaces = self.getIndentSpaces(prevLine)
        toStar = len(re.search("^(\\s*\\*)", prevLine).group(1))
        toInsert = spaces - currCol + toStar
        if spaces is None or toInsert <= 0:
            v.run_command(
                'insert_snippet', {
                    'contents': "\t"
                }
            )
            return

        v.insert(edit, currPos, " " * toInsert)

    def getIndentSpaces(self, line):
        res = re.search("^\\s*\\*(?P<fromStar>\\s*@(?:param|property)\\s+\\{[^}]+\\}\\s+\\S+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*@(?:return|define)\\s+\\{[^}]+\\}\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*@[a-z]+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*)", line)
        if res:
            return len(res.group('fromStar'))
        return None
