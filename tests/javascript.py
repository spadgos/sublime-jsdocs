syntax = "Packages/JavaScript/JavaScript.tmLanguage"

def test_basic_block_opening(helper):
    "Test that empty doc blocks are created"

    helper.insert('/**')
    helper.run()
    return [
        "/**",
        " * |",
        " */"
    ]

def test_basic_function(helper):
    "Test that function template is added"

    helper.insert('/**|\nfunction foo () {')
    helper.run()

    return [
        '/**',
        ' * |[foo description]|',
        ' * @return {[type]}',
        ' */',
        'function foo () {'
    ]

def test_parameters(helper):
    "Parameters are added to function templates"

    helper.insert('/**|\nfunction foo (bar, baz) {')
    helper.run()

    return [
        '/**',
        ' * |[foo description]|',
        ' * @param {[type]} bar [description]',
        ' * @param {[type]} baz [description]',
        ' * @return {[type]}',
        ' */',
        'function foo (bar, baz) {'
    ]

def test_multi_line_parameters(helper):
    "Parameters across multiple lines should be identified"

    helper.insert([
        '/**|',
        'function foo(bar,',
        '             baz,',
        '             quux',
        '  ) {'
    ])
    helper.run()

    return [
        '/**',
        ' * |[foo description]|',
        ' * @param {[type]} bar  [description]',
        ' * @param {[type]} baz  [description]',
        ' * @param {[type]} quux [description]',
        ' * @return {[type]}',
        ' */',
        'function foo(bar,',
        '             baz,',
        '             quux',
        '  ) {'
    ]

def test_vars_number(helper):
    "Variables initialised to number get placeholders"

    helper.insert([
        '/**|',
        'var foo = 1;'
    ])
    helper.run()
    return [
        '/**',
        ' * |[foo description]|',
        ' * @type {Number}',
        ' */',
        'var foo = 1;'
    ]

def test_vars_string_double_quotes(helper):
    "Variables initialised to string get placeholders"

    helper.insert([
        '/**|',
        'var foo = "a";'
    ])
    helper.run()
    return [
        '/**',
        ' * |[foo description]|',
        ' * @type {String}',
        ' */',
        'var foo = "a";'
    ]

def test_vars_string_single_quotes(helper):
    "Variables initialised to string get placeholders"

    helper.insert([
        '/**|',
        'var foo = \'a\';'
    ])
    helper.run()
    return [
        '/**',
        ' * |[foo description]|',
        ' * @type {String}',
        ' */',
        'var foo = \'a\';'
    ]

def test_vars_unknown_type(helper):
    "Variables initialised to unknown variables get placeholders"

    helper.insert([
        '/**|',
        'var foo = bar;'
    ])
    helper.run()
    return [
        '/**',
        ' * |[foo description]|',
        ' * @type {[type]}',
        ' */',
        'var foo = bar;'
    ]
