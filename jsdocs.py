"""
JSDocs v1.3.0
by Nick Fisher
https://github.com/spadgos/sublime-jsdocs
"""
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


def getParser(view):
    scope = view.scope_name(view.sel()[0].end())
    viewSettings = view.settings()

    if re.search("source\\.php", scope):
        return JsdocsPHP(viewSettings)

    return JsdocsJavascript(viewSettings)


class JsdocsCommand(sublime_plugin.TextCommand):

    def run(self, edit, inline=False):
        v = self.view

        settings = v.settings()
        point = v.sel()[0].end()
        indentSpaces = max(0, settings.get("jsdocs_indentation_spaces", 1))
        alignTags = settings.get("jsdocs_align_tags", True)
        prefix = "\n*" + (" " * indentSpaces)

        parser = getParser(v)
        parser.inline = inline

        # read the next line
        line = read_line(v, point + 1)
        out = None

        # if there is a line following this
        if line:
            if parser.isExistingComment(line):
                write(v, "\n *" + (" " * indentSpaces))
                return
            # match against a function declaration.
            out = parser.parse(line)

        if out and alignTags and not inline:
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

        if out:
            tabIndex = counter()

            def swapTabs(m):
                return "%s%d%s" % (m.group(1), tabIndex.next(), m.group(2))

            for index, outputLine in enumerate(out):
                out[index] = re.sub("(\\$\\{)\\d+(:[^}]+\\})", swapTabs, outputLine)

        if inline:
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


class JsdocsParser:

    def __init__(self, viewSettings):
        self.viewSettings = viewSettings
        self.setupSettings()

    def isExistingComment(self, line):
        return re.search('^\\s*\\*', line)

    def parse(self, line):
        out = self.parseFunction(line)  # (name, args)
        if (out):
            return self.formatFunction(*out)

        #  out = self.parseVar(line)
        #  if out:
        #      return out

        return None

    def formatFunction(self, name, args):
        out = []

        out.append("${1:[%s description]}" % (name))

        self.addExtraTags(out)

        # if there are arguments, add a @param for each
        if (args):
            # remove comments inside the argument list.
            args = re.sub("/\*.*?\*/", '', args)
            for arg in self.parseArgs(args):
                out.append("@param %s${1:%s}%s %s ${1:[description]}" % (
                    "{" if self.settings['curlyTypes'] else "",
                    escape(arg[0] or "[type]"),
                    "}" if self.settings['curlyTypes'] else "",
                    escape(arg[1])
                ))

        retType = self.getFunctionReturnType(name)
        if retType is not None:
            out.append("@return %s${1:%s}%s" % (
                "{" if self.settings['curlyTypes'] else "",
                retType or "[type]",
                "}" if self.settings['curlyTypes'] else ""
            ))

        return out

    def getFunctionReturnType(self, name):
        """ returns None for no return type. False meaning unknown, or a string """
        name = re.sub("^[$_]", "", name)

        if re.match("[A-Z]", name):
            # no return, but should add a class
            return None

        if re.match('(?:set|add)[A-Z_]', name):
            # setter/mutator, no return
            return None

        if re.match('(?:is|has)[A-Z_]', name):  # functions starting with 'is' or 'has'
            return self.settings['bool']

        return False

    def parseArgs(self, args):
        """ an array of tuples, the first being the best guess at the type, the second being the name """
        out = []
        for arg in re.split('\s*,\s*', args):
            arg = arg.strip()
            out.append((self.getArgType(arg), self.getArgName(arg)))
        return out

    def getArgType(self, arg):
        return None

    def getArgName(self, arg):
        return arg

    def addExtraTags(self, out):
        extraTags = self.viewSettings.get('jsdocs_extra_tags', [])
        if (len(extraTags) > 0):
            out.extend(extraTags)


class JsdocsJavascript(JsdocsParser):
    def setupSettings(self):
        self.settings = {
            # curly brackets around the type information
            "curlyTypes": True,
            # technically, they can contain all sorts of unicode, but w/e
            "varIdentifier": '[a-zA-Z_$][a-zA-Z_$0-9]*',
            "fnIdentifier": '[a-zA-Z_$][a-zA-Z_$0-9]*',

            "bool": "Boolean"
        }

    def parseFunction(self, line):
        res = re.search(
            #   fnName = function,  fnName : function
            '(?:(?P<name1>' + self.settings['varIdentifier'] + ')\s*[:=]\s*)?'
            + 'function'
            # function fnName
            + '(?:\s+(?P<name2>' + self.settings['fnIdentifier'] + '))?'
            # (arg1, arg2)
            + '\s*\((?P<args>.*)\)',
            line
        )
        if not res:
            return None

        # grab the name out of "name1 = function name2(foo)" preferring name1
        name = escape(res.group('name1') or res.group('name2') or '')
        args = res.group('args')

        return (name, args)

"""    def parseVar(self, line):
        res = re.search(
            #   var foo = blah,
            #       foo = blah;
            #   baz.foo = blah;
            #   baz = {
            #        foo : blah
            #   }

            '\\b(?P<name>' + self.settings['varIdentifier'] + ')\s*[=:]\s*(?P<val>.*?)(?:[;,]|$)',
            line
        )
        if not res:
            return None

        out = []
        name = res.group('name')
        val = res.group('val').strip()

        valType = guessType(val)
        if self.inline:
            out.append("@type {${%d:%s}} ${%d:[description]}" % (tabIndex.next(), valType, tabIndex.next()))
        else:
            out.append("${%d:[%s description]}" % (tabIndex.next(), name))
            out.append("@type {${%d:%s}}" % (tabIndex.next(), valType))

        return out
"""


class JsdocsPHP(JsdocsParser):
    def setupSettings(self):
        self.settings = {
            # curly brackets around the type information
            'curlyTypes': False,
            'varIdentifier': '\\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*',
            'fnIdentifier': '[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*',
            "bool": "bool"
        }

    def parseFunction(self, line):
        res = re.search(
            'function\\s+'
            + '(?P<name>' + self.settings['fnIdentifier'] + ')'
            # function fnName
            # (arg1, arg2)
            + '\\s*\\((?P<args>.*)\)',
            line
        )
        if not res:
            return None

        return (res.group('name'), res.group('args'))

    def getArgType(self, arg):
        if re.search('\\S\\s', arg):
            return re.search("^(\\S+)", arg).group(1)
        else:
            return None

    def getArgName(self, arg):
        return re.search("(\\S+)$", arg).group(1)


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
        res = re.search("^\\s*\\*(?P<fromStar>\\s*@(?:param|property)\\s+\\S+\\s+\\S+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*@(?:returns?|define)\\s+\\S+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*@[a-z]+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*)", line)
        if res:
            return len(res.group('fromStar'))
        return None
