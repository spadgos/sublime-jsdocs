"""
DocBlockr v2.6.3
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


def write(view, str):
    view.run_command(
        'insert_snippet', {
            'contents': str
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


def getParser(view):
    scope = view.scope_name(view.sel()[0].end())
    viewSettings = view.settings()

    if re.search("source\\.php", scope):
        return JsdocsPHP(viewSettings)
    elif re.search("source\\.coffee", scope):
        return JsdocsCoffee(viewSettings)

    return JsdocsJavascript(viewSettings)


class JsdocsCommand(sublime_plugin.TextCommand):

    def run(self, edit, inline=False):
        v = self.view

        settings = v.settings()
        point = v.sel()[0].end()

        indentSpaces = max(0, settings.get("jsdocs_indentation_spaces", 1))
        prefix = "*" + (" " * indentSpaces)

        alignTags = settings.get("jsdocs_align_tags", 'deep')
        deepAlignTags = alignTags == 'deep'
        shallowAlignTags = alignTags in ('shallow', True)

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

        # align the tags
        if out and (shallowAlignTags or deepAlignTags) and not inline:
            def outputWidth(str):
                # get the length of a string, after it is output as a snippet,
                # "${1:foo}" --> 3
                return len(string.replace(re.sub("[$][{]\\d+:([^}]+)[}]", "\\1", str), '\$', '$'))

            # count how many columns we have
            maxCols = 0
            # this is a 2d list of the widths per column per line
            widths = []
            #  skip the first one, since that's always the "description" line
            for line in out[1:]:
                widths.append(map(outputWidth, line.split(" ")))
                maxCols = max(maxCols, len(widths[-1]))

            #  initialise a list to 0
            maxWidths = [0] * maxCols

            if (shallowAlignTags):
                maxCols = 1

            for i in range(0, maxCols):
                for width in widths:
                    if (i < len(width)):
                        maxWidths[i] = max(maxWidths[i], width[i])

            for index, line in enumerate(out):
                if (index > 0):
                    newOut = []
                    for partIndex, part in enumerate(line.split(" ")):
                        newOut.append(part)
                        newOut.append(" " + (" " * (maxWidths[partIndex] - outputWidth(part))))
                    out[index] = "".join(newOut).strip()

        # fix all the tab stops so they're consecutive
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
            snippet = "\n " + prefix
            closer = parser.settings['commentCloser']
            if out:
                if settings.get('jsdocs_spacer_between_sections'):
                    lastTag = None
                    for idx, line in enumerate(out):
                        res = re.match("^\\s*@([a-zA-Z]+)", line)
                        if res and (lastTag != res.group(1)):
                            lastTag = res.group(1)
                            out.insert(idx, "")
                snippet += ("\n " + prefix).join(out)
            else:
                snippet += "$0"

            snippet += "\n" + closer
            write(v, snippet)


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

        out = self.parseVar(line)
        if out:
            return self.formatVar(*out)

        return None

    def formatVar(self, name, val):
        out = []
        if not val or val == '':  # quick short circuit
            valType = "[type]"
        else:
            valType = self.guessTypeFromValue(val) or self.guessTypeFromName(name) or "[type]"

        if self.inline:
            out.append("@%s %s${1:%s}%s ${1:[description]}" % (
                self.settings['typeTag'],
                "{" if self.settings['curlyTypes'] else "",
                valType,
                "}" if self.settings['curlyTypes'] else ""
            ))
        else:
            out.append("${1:[%s description]}" % (escape(name)))
            out.append("@%s %s${1:%s}%s" % (
                self.settings['typeTag'],
                "{" if self.settings['curlyTypes'] else "",
                valType,
                "}" if self.settings['curlyTypes'] else ""
            ))

        return out

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
                    escape(arg[0] or self.guessTypeFromName(arg[1]) or "[type]"),
                    "}" if self.settings['curlyTypes'] else "",
                    escape(arg[1])
                ))

        retType = self.getFunctionReturnType(name)
        if retType is not None:
            # the extra space here is so that the description will align with the param description
            out.append("%s %s${1:%s}%s %s${2:[description]}" % (
                self.viewSettings.get('jsdocs_return_tag') or '@return',
                "{" if self.settings['curlyTypes'] else "",
                retType or "[type]",
                "}" if self.settings['curlyTypes'] else "",
                " " if args else ""
            ))

        return out

    def getFunctionReturnType(self, name):
        """ returns None for no return type. False meaning unknown, or a string """
        name = re.sub("^[$_]", "", name)

        if re.match("[A-Z]", name):
            # no return, but should add a class
            return None

        if re.match('(?:set|add)($|[A-Z_])', name):
            # setter/mutator, no return
            return None

        if re.match('(?:is|has)($|[A-Z_])', name):  # functions starting with 'is' or 'has'
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

    def guessTypeFromName(self, name):
        name = re.sub("^[$_]", "", name)
        hungarian_map = self.viewSettings.get('jsdocs_notation_map', [])
        if len(hungarian_map):
            for rule in hungarian_map:
                print rule
                matched = False
                if 'prefix' in rule:
                    matched = re.match(rule['prefix'] + "[A-Z_]", name)
                elif 'regex' in rule:
                    matched = re.search(rule['regex'], name)

                if matched:

                    return self.settings[rule['type']] if rule['type'] in self.settings else rule['type']

        if (re.match("(?:is|has)[A-Z_]", name)):
            return self.settings['bool']

        if (re.match("^(?:cb|callback|done|next|fn)$", name)):
            return self.settings['function']

        return False


class JsdocsJavascript(JsdocsParser):
    def setupSettings(self):
        self.settings = {
            # curly brackets around the type information
            "curlyTypes": True,
            "typeTag": "type",
            # technically, they can contain all sorts of unicode, but w/e
            "varIdentifier": '[a-zA-Z_$][a-zA-Z_$0-9]*',
            "fnIdentifier": '[a-zA-Z_$][a-zA-Z_$0-9]*',

            "commentCloser": " */",
            "bool": "Boolean",
            "function": "Function"
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

    def parseVar(self, line):
        res = re.search(
            #   var foo = blah,
            #       foo = blah;
            #   baz.foo = blah;
            #   baz = {
            #        foo : blah
            #   }

            '(?P<name>' + self.settings['varIdentifier'] + ')\s*[=:]\s*(?P<val>.*?)(?:[;,]|$)',
            line
        )
        if not res:
            return None

        return (res.group('name'), res.group('val').strip())

    def guessTypeFromValue(self, val):
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
            res = re.search('new (' + self.settings['fnIdentifier'] + ')', val)
            return res and res.group(1) or None
        return None


class JsdocsPHP(JsdocsParser):
    def setupSettings(self):
        nameToken = '[a-zA-Z_\\x7f-\\xff][a-zA-Z0-9_\\x7f-\\xff]*'
        self.settings = {
            # curly brackets around the type information
            'curlyTypes': False,
            'typeTag': "var",
            'varIdentifier': '[$]' + nameToken + '(?:->' + nameToken + ')*',
            'fnIdentifier': nameToken,
            'commentCloser': ' */',
            'bool': "boolean",
            'function': "function"
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
        #  function add($x, $y = 1)
        res = re.search(
            '(?P<name>' + self.settings['varIdentifier'] + ")\\s*=\\s*(?P<val>.*)",
            arg
        )
        if res:
            return self.guessTypeFromValue(res.group('val'))

        #  function sum(Array $x)
        if re.search('\\S\\s', arg):
            return re.search("^(\\S+)", arg).group(1)
        else:
            return None

    def getArgName(self, arg):
        return re.search("(\\S+)(?:\\s*=.*)?$", arg).group(1)

    def parseVar(self, line):
        res = re.search(
            #   var $foo = blah,
            #       $foo = blah;
            #   $baz->foo = blah;
            #   $baz = array(
            #        'foo' => blah
            #   )

            '(?P<name>' + self.settings['varIdentifier'] + ')\\s*=>?\\s*(?P<val>.*?)(?:[;,]|$)',
            line
        )
        if res:
            return (res.group('name'), res.group('val').strip())

        res = re.search(
            '\\b(?:var|public|private|protected|static)\\s+(?P<name>' + self.settings['varIdentifier'] + ')',
            line
        )
        if res:
            return (res.group('name'), None)

        return None

    def guessTypeFromValue(self, val):
        if is_numeric(val):
            return "float" if '.' in val else "integer"
        if val[0] == '"' or val[0] == "'":
            return "string"
        if val[:5] == 'array':
            return "array"
        if val.lower() in ('true', 'false', 'filenotfound'):
            return 'boolean'
        if val[:4] == 'new ':
            res = re.search('new (' + self.settings['fnIdentifier'] + ')', val)
            return res and res.group(1) or None
        return None

    def getFunctionReturnType(self, name):
        if (name[:2] == '__'):
            if name in ('__construct', '__destruct', '__set', '__unset', '__wakeup'):
                return None
            if name == '__sleep':
                return 'array'
            if name == '__toString':
                return 'string'
            if name == '__isset':
                return 'boolean'
        return JsdocsParser.getFunctionReturnType(self, name)


class JsdocsCoffee(JsdocsParser):
    def setupSettings(self):
        self.settings = {
            # curly brackets around the type information
            'curlyTypes': True,
            'typeTag': "type",
            # technically, they can contain all sorts of unicode, but w/e
            'varIdentifier': '[a-zA-Z_$][a-zA-Z_$0-9]*',
            'fnIdentifier': '[a-zA-Z_$][a-zA-Z_$0-9]*',
            'commentCloser': '###',
            'bool': 'Boolean',
            'function': 'Function'
        }

    def parseFunction(self, line):
        print line
        print '(?:(?P<name>' + self.settings['varIdentifier'] + ')\s*[:=]\s*)?\\((?P<args>[^()]*?)\\)?\\s*([=-]>)'
        res = re.search(
            #   fnName = function,  fnName : function
            '(?:(?P<name>' + self.settings['varIdentifier'] + ')\s*[:=]\s*)?'
            + '(?:\\((?P<args>[^()]*?)\\))?\\s*([=-]>)',
            line
        )
        print res
        if not res:
            return None

        # grab the name out of "name1 = function name2(foo)" preferring name1
        name = escape(res.group('name') or '')
        args = res.group('args')

        return (name, args)

    def parseVar(self, line):
        res = re.search(
            #   var foo = blah,
            #       foo = blah;
            #   baz.foo = blah;
            #   baz = {
            #        foo : blah
            #   }

            '(?P<name>' + self.settings['varIdentifier'] + ')\s*[=:]\s*(?P<val>.*?)(?:[;,]|$)',
            line
        )
        if not res:
            return None

        return (res.group('name'), res.group('val').strip())

    def guessTypeFromValue(self, val):
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
            res = re.search('new (' + self.settings['fnIdentifier'] + ')', val)
            return res and res.group(1) or None
        return None


############################################################33

class JsdocsIndentCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        currPos = v.sel()[0].begin()
        currLineRegion = v.line(currPos)
        currCol = currPos - currLineRegion.begin()  # which column we're currently in
        prevLine = v.substr(v.line(v.line(currPos).begin() - 1))
        spaces = self.getIndentSpaces(prevLine)
        if spaces:
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
        else:
            v.insert(edit, currPos, "\t")

    def getIndentSpaces(self, line):
        res = re.search("^\\s*\\*(?P<fromStar>\\s*@(?:param|property)\\s+\\S+\\s+\\S+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*@(?:returns?|define)\\s+\\S+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*@[a-z]+\\s+)\\S", line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*)", line)
        if res:
            return len(res.group('fromStar'))
        return None


class JsdocsJoinCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        for sel in v.sel():
            for lineRegion in reversed(v.lines(sel)):
                v.replace(edit, v.find("[ \\t]*\\n[ \\t]*((?:\\*|//|#)[ \\t]*)?", lineRegion.begin()), ' ')


class JsdocsDecorateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        re_whitespace = re.compile("^(\\s*)//")
        v.run_command('expand_selection', {'to': 'scope'})
        for sel in v.sel():
            maxLength = 0
            lines = v.lines(sel)
            for lineRegion in lines:
                leadingWS = len(re_whitespace.match(v.substr(lineRegion)).group(1))
                maxLength = max(maxLength, lineRegion.size())

            lineLength = maxLength - leadingWS
            leadingWS = " " * leadingWS
            v.insert(edit, sel.end(), leadingWS + "/" * (lineLength + 3) + "\n")

            for lineRegion in reversed(lines):
                line = v.substr(lineRegion)
                rPadding = 1 + (maxLength - lineRegion.size())
                v.replace(edit, lineRegion, leadingWS + line + (" " * rPadding) + "//")
                # break

            v.insert(edit, sel.begin(), "/" * (lineLength + 3) + "\n")


class JsdocsDeindent(sublime_plugin.TextCommand):
    """
    When pressing enter at the end of a docblock, this takes the cursor back one space.
    /**
     *
     */|   <-- from here
    |      <-- to here
    """
    def run(self, edit):
        v = self.view
        lineRegion = v.line(v.sel()[0])
        line = v.substr(lineRegion)
        v.insert(edit, lineRegion.end(), re.sub("^(\\s*)\\s\\*/.*", "\n\\1", line))


class JsdocsReparse(sublime_plugin.TextCommand):
    """
    Reparse a docblock to make the fields 'active' again, so that pressing tab will jump to the next one
    """
    def run(self, edit):
        tabIndex = counter()

        def tabStop(m):
            return "${%d:%s}" % (tabIndex.next(), m.group(1))

        v = self.view
        v.run_command('clear_fields')
        v.run_command('expand_selection', {'to': 'scope'})
        sel = v.sel()[0]

        # strip out leading spaces, since inserting a snippet keeps the indentation
        text = re.sub("\\n\\s+\\*", "\n *", v.substr(sel))

        # replace [bracketed] [text] with a tabstop
        text = re.sub("(\\[.+?\\])", tabStop, text)

        v.erase(edit, sel)
        write(v, text)


class JsdocsTrimAutoWhitespace(sublime_plugin.TextCommand):
    """
    Trim the automatic whitespace added when creating a new line in a docblock.
    """
    def run(self, edit):
        v = self.view
        lineRegion = v.line(v.sel()[0])
        line = v.substr(lineRegion)
        spaces = max(0, v.settings().get("jsdocs_indentation_spaces", 1))
        v.replace(edit, lineRegion, re.sub("^(\\s*\\*)\\s*$", "\\1\n\\1" + (" " * spaces), line))
