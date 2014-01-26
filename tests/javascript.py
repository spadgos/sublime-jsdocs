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
