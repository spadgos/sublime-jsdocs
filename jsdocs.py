"""
DocBlockr v2.9.3
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
    return str.replace('$', '\$').replace('{', '\{').replace('}', '\}')


def is_numeric(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def getParser(view):
    scope = view.scope_name(view.sel()[0].end())
    res = re.search('\\bsource\\.([a-z+\-]+)', scope)
    sourceLang = res.group(1) if res else 'js'
    viewSettings = view.settings()

    if sourceLang == "php":
        return JsdocsPHP(viewSettings)
    elif sourceLang == "coffee":
        return JsdocsCoffee(viewSettings)
    elif sourceLang == "actionscript":
        return JsdocsActionscript(viewSettings)
    elif sourceLang == "c++" or sourceLang == 'c' or sourceLang == 'cuda-c++':
        return JsdocsCPP(viewSettings)
    elif sourceLang == 'objc' or sourceLang == 'objc++':
        return JsdocsObjC(viewSettings)
    return JsdocsJavascript(viewSettings)


class JsdocsCommand(sublime_plugin.TextCommand):

    def run(self, edit, inline=False):

        self.initialize(self.view, inline)

        # erase characters in the view (will be added to the output later)
        self.view.erase(edit, self.trailingRgn)

        out = None

        if self.parser.isExistingComment(self.line):
            write(self.view, "\n *" + self.indentSpaces)
            return

        # match against a function declaration.
        out = self.parser.parse(self.line)

        snippet = self.generateSnippet(out, inline)

        write(self.view, snippet)

    def initialize(self, v, inline=False):
        point = v.sel()[0].end()

        self.settings = v.settings()

        # trailing characters are put inside the body of the comment
        self.trailingRgn = sublime.Region(point, v.line(point).end())
        self.trailingString = v.substr(self.trailingRgn).strip()
        # drop trailing '*/'
        self.trailingString = escape(re.sub('\\s*\\*\\/\\s*$', '', self.trailingString))

        self.indentSpaces = " " * max(0, self.settings.get("jsdocs_indentation_spaces", 1))
        self.prefix = "*"

        settingsAlignTags = self.settings.get("jsdocs_align_tags", 'deep')
        self.deepAlignTags = settingsAlignTags == 'deep'
        self.shallowAlignTags = settingsAlignTags in ('shallow', True)

        self.parser = parser = getParser(v)
        parser.inline = inline

        # use trailing string as a description of the function
        if self.trailingString:
            parser.setNameOverride(self.trailingString)

        # read the next line
        self.line = parser.getDefinition(v, point + 1)

    def generateSnippet(self, out, inline=False):
        # align the tags
        if out and (self.shallowAlignTags or self.deepAlignTags) and not inline:
            out = self.alignTags(out)

        # fix all the tab stops so they're consecutive
        if out:
            out = self.fixTabStops(out)

        if inline:
            if out:
                return " " + out[0] + " */"
            else:
                return " $0 */"
        else:
            return self.createSnippet(out)

    def alignTags(self, out):
        def outputWidth(str):
            # get the length of a string, after it is output as a snippet,
            # "${1:foo}" --> 3
            return len(string.replace(re.sub("[$][{]\\d+:([^}]+)[}]", "\\1", str), '\$', '$'))

        # count how many columns we have
        maxCols = 0
        # this is a 2d list of the widths per column per line
        widths = []

        # Skip the return tag if we're faking "per-section" indenting.
        lastItem = len(out)
        if (self.settings.get('jsdocs_per_section_indent')):
            if (self.settings.get('jsdocs_return_tag') in out[-1]):
                lastItem -= 1

        #  skip the first one, since that's always the "description" line
        for line in out[1:lastItem]:
            widths.append(map(outputWidth, line.split(" ")))
            maxCols = max(maxCols, len(widths[-1]))

        #  initialise a list to 0
        maxWidths = [0] * maxCols

        if (self.shallowAlignTags):
            maxCols = 1

        for i in range(0, maxCols):
            for width in widths:
                if (i < len(width)):
                    maxWidths[i] = max(maxWidths[i], width[i])

        # Convert to a dict so we can use .get()
        maxWidths = dict(enumerate(maxWidths))

        for index, line in enumerate(out):
            if (index > 0):
                newOut = []
                for partIndex, part in enumerate(line.split(" ")):
                    newOut.append(part)
                    newOut.append(" " + (" " * (maxWidths.get(partIndex, 0) - outputWidth(part))))
                out[index] = "".join(newOut).strip()
        return out

    def fixTabStops(self, out):
        tabIndex = counter()

        def swapTabs(m):
            return "%s%d%s" % (m.group(1), tabIndex.next(), m.group(2))

        for index, outputLine in enumerate(out):
            out[index] = re.sub("(\\$\\{)\\d+(:[^}]+\\})", swapTabs, outputLine)

        return out

    def createSnippet(self, out):
        snippet = ""
        closer = self.parser.settings['commentCloser']
        if out:
            if self.settings.get('jsdocs_spacer_between_sections'):
                lastTag = None
                for idx, line in enumerate(out):
                    res = re.match("^\\s*@([a-zA-Z]+)", line)
                    if res and (lastTag != res.group(1)):
                        lastTag = res.group(1)
                        out.insert(idx, "")
            for line in out:
                snippet += "\n " + self.prefix + (self.indentSpaces + line if line else "")
        else:
            snippet += "\n " + self.prefix + self.indentSpaces + "${0:" + self.trailingString + '}'

        snippet += "\n" + closer
        return snippet


class JsdocsParser(object):

    def __init__(self, viewSettings):
        self.viewSettings = viewSettings
        self.setupSettings()
        self.nameOverride = None

    def isExistingComment(self, line):
        return re.search('^\\s*\\*', line)

    def setNameOverride(self, name):
        """ overrides the description of the function - used instead of parsed description """
        self.nameOverride = name

    def getNameOverride(self):
        return self.nameOverride

    def parse(self, line):
        out = self.parseFunction(line)  # (name, args, retval, options)
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

    def getTypeInfo(self, argType, argName):
        typeInfo = ''
        if self.settings['typeInfo']:
            typeInfo = '%s${1:%s}%s ' % (
                "{" if self.settings['curlyTypes'] else "",
                escape(argType or self.guessTypeFromName(argName) or "[type]"),
                "}" if self.settings['curlyTypes'] else "",
            )

        return typeInfo

    def formatFunction(self, name, args, retval, options={}):
        out = []
        if 'as_setter' in options:
            out.append('@private')
            return out

        description = self.getNameOverride() or ('[%s description]' % escape(name))
        out.append("${1:%s}" % description)

        self.addExtraTags(out)

        # if there are arguments, add a @param for each
        if (args):
            # remove comments inside the argument list.
            args = re.sub("/\*.*?\*/", '', args)
            for argType, argName in self.parseArgs(args):
                typeInfo = self.getTypeInfo(argType, argName)

                out.append("@param %s%s ${1:[description]}" % (
                    typeInfo,
                    escape(argName)
                ))

        # return value type might be already available in some languages but
        # even then ask language specific parser if it wants it listed
        retType = self.getFunctionReturnType(name, retval)
        if retType is not None:
            typeInfo = ''
            if self.settings['typeInfo']:
                typeInfo = ' %s${1:%s}%s' % (
                    "{" if self.settings['curlyTypes'] else "",
                    retType or "[type]",
                    "}" if self.settings['curlyTypes'] else ""
                )
            format_args = [
                self.viewSettings.get('jsdocs_return_tag') or '@return',
                typeInfo
            ]

            if (self.viewSettings.get('jsdocs_return_description')):
                format_str = "%s%s %s${1:[description]}"
                third_arg = ""

                # the extra space here is so that the description will align with the param description
                if args and self.viewSettings.get('jsdocs_align_tags') == 'deep':
                    if not self.viewSettings.get('jsdocs_per_section_indent'):
                        third_arg = " "

                format_args.append(third_arg)
            else:
                format_str = "%s%s"

            out.append(format_str % tuple(format_args))

        for notation in self.getMatchingNotations(name):
            if 'tags' in notation:
                out.extend(notation['tags'])

        return out

    def getFunctionReturnType(self, name, retval):
        """ returns None for no return type. False meaning unknown, or a string """

        if re.match("[A-Z]", name):
            # no return, but should add a class
            return None

        if re.match('[$_]?(?:set|add)($|[A-Z_])', name):
            # setter/mutator, no return
            return None

        if re.match('[$_]?(?:is|has)($|[A-Z_])', name):  # functions starting with 'is' or 'has'
            return self.settings['bool']

        return self.guessTypeFromName(name) or False

    def parseArgs(self, args):
        """ an array of tuples, the first being the best guess at the type, the second being the name """
        out = []

        if not args:
            return out

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
        matches = self.getMatchingNotations(name)
        if len(matches):
            rule = matches[0]
            if ('type' in rule):
                return self.settings[rule['type']] if rule['type'] in self.settings else rule['type']

        if (re.match("(?:is|has)[A-Z_]", name)):
            return self.settings['bool']

        if (re.match("^(?:cb|callback|done|next|fn)$", name)):
            return self.settings['function']

        return False

    def getMatchingNotations(self, name):
        def checkMatch(rule):
            if 'prefix' in rule:
                regex = re.escape(rule['prefix'])
                if re.match('.*[a-z]', rule['prefix']):
                    regex += '(?:[A-Z_]|$)'
                return re.match(regex, name)
            elif 'regex' in rule:
                return re.search(rule['regex'], name)

        return filter(checkMatch, self.viewSettings.get('jsdocs_notation_map', []))

    def getDefinition(self, view, pos):
        """
        get a relevant definition starting at the given point
        returns string
        """
        maxLines = 25  # don't go further than this
        openBrackets = 0

        definition = ''

        def countBrackets(total, bracket):
            return total + (1 if bracket == '(' else -1)

        for i in xrange(0, maxLines):
            line = read_line(view, pos)
            if line is None:
                break

            pos += len(line) + 1
            # strip comments
            line = re.sub("//.*", "", line)
            line = re.sub(r"/\*.*\*/", "", line)
            if definition == '':
                if not self.settings['fnOpener'] or not re.search(self.settings['fnOpener'], line):
                    definition = line
                    break
            definition += line
            openBrackets = reduce(countBrackets, re.findall('[()]', line), openBrackets)
            if openBrackets == 0:
                break
        return definition


class JsdocsJavascript(JsdocsParser):
    def setupSettings(self):
        identifier = '[a-zA-Z_$][a-zA-Z_$0-9]*'
        self.settings = {
            # curly brackets around the type information
            "curlyTypes": True,
            'typeInfo': True,
            "typeTag": "type",
            # technically, they can contain all sorts of unicode, but w/e
            "varIdentifier": identifier,
            "fnIdentifier":  identifier,
            "fnOpener": 'function(?:\\s+' + identifier + ')?\\s*\\(',
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
            + '\s*\(\s*(?P<args>.*)\)',
            line
        )
        if not res:
            return None

        # grab the name out of "name1 = function name2(foo)" preferring name1
        name = res.group('name1') or res.group('name2') or ''
        args = res.group('args')

        return (name, args, None)

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
            'typeInfo': True,
            'typeTag': "var",
            'varIdentifier': '[$]' + nameToken + '(?:->' + nameToken + ')*',
            'fnIdentifier': nameToken,
            'fnOpener': 'function(?:\\s+' + nameToken + ')?\\s*\\(',
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
            + '\\s*\\(\\s*(?P<args>.*)\)',
            line
        )
        if not res:
            return None

        return (res.group('name'), res.group('args'), None)

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
        return re.search("(" + self.settings['varIdentifier'] + ")(?:\\s*=.*)?$", arg).group(1)

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

    def getFunctionReturnType(self, name, retval):
        if (name[:2] == '__'):
            if name in ('__construct', '__destruct', '__set', '__unset', '__wakeup'):
                return None
            if name == '__sleep':
                return 'array'
            if name == '__toString':
                return 'string'
            if name == '__isset':
                return 'boolean'
        return JsdocsParser.getFunctionReturnType(self, name, retval)


class JsdocsCPP(JsdocsParser):
    def setupSettings(self):
        nameToken = '[a-zA-Z_][a-zA-Z0-9_]*'
        identifier = '(%s)(::%s)?' % (nameToken, nameToken)
        self.settings = {
            'typeInfo': False,
            'curlyTypes': False,
            'typeTag': 'param',
            'commentCloser': ' */',
            'fnIdentifier': identifier,
            'varIdentifier': identifier,
            'fnOpener': identifier + '\\s+' + identifier + '\\s*\\(',
            'bool': 'bool',
            'function': 'function'
        }

    def parseFunction(self, line):
        res = re.search(
            '(?P<retval>' + self.settings['varIdentifier'] + ')[&*\\s]+'
            + '(?P<name>' + self.settings['varIdentifier'] + ')'
            # void fnName
            # (arg1, arg2)
            + '\\s*\\(\\s*(?P<args>.*)\)',
            line
        )
        if not res:
            return None

        return (res.group('name'), res.group('args'), res.group('retval'))

    def parseArgs(self, args):
        if args.strip() == 'void':
            return []
        return super(JsdocsCPP, self).parseArgs(args)

    def getArgType(self, arg):
        return None

    def getArgName(self, arg):
        return re.search("(" + self.settings['varIdentifier'] + r")(?:\s*\[\s*\])?(?:\s*=.*)?$", arg).group(1)

    def parseVar(self, line):
        return None

    def guessTypeFromValue(self, val):
        return None

    def getFunctionReturnType(self, name, retval):
        return retval if retval != 'void' else None


class JsdocsCoffee(JsdocsParser):
    def setupSettings(self):
        identifier = '[a-zA-Z_$][a-zA-Z_$0-9]*'
        self.settings = {
            # curly brackets around the type information
            'curlyTypes': True,
            'typeTag': "type",
            'typeInfo': True,
            # technically, they can contain all sorts of unicode, but w/e
            'varIdentifier': identifier,
            'fnIdentifier': identifier,
            'fnOpener': None,  # no multi-line function definitions for you, hipsters!
            'commentCloser': '###',
            'bool': 'Boolean',
            'function': 'Function'
        }

    def parseFunction(self, line):
        res = re.search(
            #   fnName = function,  fnName : function
            '(?:(?P<name>' + self.settings['varIdentifier'] + ')\s*[:=]\s*)?'
            + '(?:\\((?P<args>[^()]*?)\\))?\\s*([=-]>)',
            line
        )
        if not res:
            return None

        # grab the name out of "name1 = function name2(foo)" preferring name1
        name = res.group('name') or ''
        args = res.group('args')

        return (name, args, None)

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


class JsdocsActionscript(JsdocsParser):

    def setupSettings(self):
        nameToken = '[a-zA-Z_][a-zA-Z0-9_]*'
        self.settings = {
            'typeInfo': False,
            'curlyTypes': False,
            'typeTag': '',
            'commentCloser': ' */',
            'fnIdentifier': nameToken,
            'varIdentifier': '(%s)(?::%s)?' % (nameToken, nameToken),
            'fnOpener': 'function(?:\\s+[gs]et)?(?:\\s+' + nameToken + ')?\\s*\\(',
            'bool': 'bool',
            'function': 'function'
        }

    def parseFunction(self, line):
        res = re.search(
            #   fnName = function,  fnName : function
            '(?:(?P<name1>' + self.settings['varIdentifier'] + ')\s*[:=]\s*)?'
            + 'function(?:\s+(?P<getset>[gs]et))?'
            # function fnName
            + '(?:\s+(?P<name2>' + self.settings['fnIdentifier'] + '))?'
            # (arg1, arg2)
            + '\s*\(\s*(?P<args>.*)\)',
            line
        )
        if not res:
            return None

        name = res.group('name1') and re.sub(self.settings['varIdentifier'], r'\1', res.group('name1')) \
            or res.group('name2') \
            or ''

        args = res.group('args')
        options = {}
        if res.group('getset') == 'set':
            options['as_setter'] = True

        return (name, args, None, options)

    def parseVar(self, line):
        return None

    def getArgName(self, arg):
        return re.sub(self.settings['varIdentifier'] + r'(\s*=.*)?', r'\1', arg)

    def getArgType(self, arg):
        # could actually figure it out easily, but it's not important for the documentation
        return None


class JsdocsObjC(JsdocsParser):

    def setupSettings(self):
        identifier = '[a-zA-Z_$][a-zA-Z_$0-9]*'
        self.settings = {
            # curly brackets around the type information
            "curlyTypes": True,
            'typeInfo': True,
            "typeTag": "type",
            # technically, they can contain all sorts of unicode, but w/e
            "varIdentifier": identifier,
            "fnIdentifier":  identifier,
            "fnOpener": '^\s*[-+]',
            "commentCloser": " */",
            "bool": "Boolean",
            "function": "Function"
        }

    def getDefinition(self, view, pos):
        maxLines = 25  # don't go further than this

        definition = ''
        for i in xrange(0, maxLines):
            line = read_line(view, pos)
            if line is None:
                break

            pos += len(line) + 1
            # strip comments
            line = re.sub("//.*", "", line)
            if definition == '':
                if not self.settings['fnOpener'] or not re.search(self.settings['fnOpener'], line):
                    definition = line
                    break
            definition += line
            if line.find(';') > -1 or line.find('{') > -1:
                definition = re.sub(r'\s*[;{]\s*$', '', definition)
                break
        return definition

    def parseFunction(self, line):
        # this is terrible, don't judge me

        typeRE = r'[a-zA-Z_$][a-zA-Z0-9_$]*\s*\**'
        res = re.search(
            '[-+]\s+\\(\\s*(?P<retval>' + typeRE + ')\\s*\\)\\s*'
            + '(?P<name>[a-zA-Z_$][a-zA-Z0-9_$]*)'
            # void fnName
            # (arg1, arg2)
            + '\\s*(?::(?P<args>.*))?',
            line
        )
        if not res:
            return
        name = res.group('name')
        argStr = res.group('args')
        args = []
        if argStr:
            groups = re.split('\\s*:\\s*', argStr)
            numGroups = len(groups)
            for i in xrange(0, numGroups):
                group = groups[i]
                if i < numGroups - 1:
                    result = re.search(r'\s+(\S*)$', group)
                    name += ':' + result.group(1)
                    group = group[:result.start()]

                args.append(group)

            if (numGroups):
                name += ':'
        return (name, '|||'.join(args), res.group('retval'))

    def parseArgs(self, args):
        out = []
        for arg in args.split('|||'):  # lol
            lastParen = arg.rfind(')')
            out.append((arg[1:lastParen], arg[lastParen + 1:]))
        return out

    def getFunctionReturnType(self, name, retval):
        return retval if retval != 'void' and retval != 'IBAction' else None

    def parseVar(self, line):
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
        hasTypes = getParser(self.view).settings['typeInfo']
        extraIndent = '\\s+\\S+' if hasTypes else ''
        res = re.search("^\\s*\\*(?P<fromStar>\\s*@(?:param|property)%s\\s+\\S+\\s+)\\S" % extraIndent, line) \
           or re.search("^\\s*\\*(?P<fromStar>\\s*@(?:returns?|define)%s\\s+\\S+\\s+)\\S" % extraIndent, line) \
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


class JsdocsWrapLines(sublime_plugin.TextCommand):
    """
    Reformat description text inside a comment block to wrap at the correct length.
    Wrap column is set by the first ruler (set in Default.sublime-settings), or 80 by default.
    Shortcut Key: alt+q
    """

    def run(self, edit):
        v = self.view
        settings = v.settings()
        rulers = settings.get('rulers')
        tabSize = settings.get('tab_size')

        wrapLength = rulers[0] or 80
        numIndentSpaces = max(0, settings.get("jsdocs_indentation_spaces", 1))
        indentSpaces = " " * numIndentSpaces
        indentSpacesSamePara = " " * max(0, settings.get("jsdocs_indentation_spaces_same_para", numIndentSpaces))
        spacerBetweenSections = settings.get("jsdocs_spacer_between_sections")

        v.run_command('expand_selection', {'to': 'scope'})

        # find the first word
        startPoint = v.find("\n\\s*\\* ", v.sel()[0].begin()).begin()
        # find the first tag, or the end of the comment
        endPoint = v.find("\\s*\n\\s*\\*(/)", v.sel()[0].begin()).begin()

        # replace the selection with this ^ new selection
        v.sel().clear()
        v.sel().add(sublime.Region(startPoint, endPoint))

        # get the description text
        text = v.substr(v.sel()[0])

        # find the indentation level
        indentation = len(re.sub('\t', ' ' * tabSize, re.search("\n(\\s*\\*)", text).group(1)))
        wrapLength -= indentation - tabSize

        # join all the lines, collapsing "empty" lines
        text = re.sub("\n(\\s*\\*\\s*\n)+", "\n\n", text)

        def wrapPara(para):
            para = re.sub("(\n|^)\\s*\\*\\s*", " ", para)

            # split the paragraph into words
            words = para.strip().split(' ')
            text = '\n'
            line = ' *' + indentSpaces
            lineTagged = False  # indicates if the line contains a doc tag
            paraTagged = False  # indicates if this paragraph contains a doc tag
            lineIsNew = True
            tag = ''

            # join all words to create lines, no longer than wrapLength
            for i, word in enumerate(words):
                if not word and not lineTagged:
                    continue

                if lineIsNew and word[0] == '@':
                    lineTagged = True
                    paraTagged = True
                    tag = word

                if len(line) + len(word) >= wrapLength - 1:
                    # appending the word to the current line whould exceed its
                    # length requirements
                    text += line.rstrip() + '\n'
                    line = ' *' + indentSpacesSamePara + word + ' '
                    lineTagged = False
                    lineIsNew = True
                else:
                    line += word + ' '

                lineIsNew = False

            text += line.rstrip()
            return {'text':       text,
                    'lineTagged': lineTagged,
                    'tagged':     paraTagged,
                    'tag':        tag}

        # split the text into paragraphs, where each paragraph is eighter
        # defined by an empty line or the start of a doc parameter
        paragraphs = re.split('\n{2,}|\n\\s*\\*\\s*(?=@)', text)
        wrappedParas = []
        text = ''
        for p, para in enumerate(paragraphs):
            # wrap the lines in the current paragraph
            wrappedParas.append(wrapPara(para))

        # combine all the paragraphs into a single piece of text
        for i in range(0, len(wrappedParas)):
            para = wrappedParas[i]
            last = i == len(wrappedParas) - 1

            nextIsTagged = not last and wrappedParas[i + 1]['tagged']
            nextIsSameTag = nextIsTagged and para['tag'] == wrappedParas[i + 1]['tag']

            if last or (para['lineTagged'] or nextIsTagged) and \
                    not (spacerBetweenSections and not nextIsSameTag):
                text += para['text']
            else:
                text += para['text'] + '\n *'

        write(v, text)
