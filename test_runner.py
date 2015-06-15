import sublime
import sublime_plugin
import unittest

class __docblockr_test_replace_cursor_position(sublime_plugin.TextCommand):
    def run(self, edit):
        cursor_placeholder = self.view.find('\|', 0)

        if not cursor_placeholder or cursor_placeholder.empty():
            return

        self.view.sel().clear()
        self.view.sel().add(cursor_placeholder.begin())
        self.view.replace(edit, cursor_placeholder, '')

class ViewTestCase(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.view.set_scratch(True)

        # TODO there's probably a better way to initialise the testcase default settings
        settings = self.view.settings()
        settings.set('auto_indent', False)
        settings.set('jsdocs_lower_case_primitives', False)
        settings.set('jsdocs_param_description', True)
        settings.set('jsdocs_per_section_indent', False)
        settings.set('jsdocs_return_description', True)
        settings.set('jsdocs_short_primitives', False)
        settings.set('jsdocs_spacer_between_sections', False)
        settings.set('jsdocs_function_description', True)

        if int(sublime.version()) < 3000:
            self.edit = self.view.begin_edit()

    def tearDown(self):
        if int(sublime.version()) < 3000:
            self.view.sel().clear()
            self.view.end_edit(self.edit)
            self.window.run_command('close')
        else:
            self.view.close()

    def set_view_content(self, content):
        if isinstance(content, list):
            content = '\n'.join(content)
        self.view.run_command('insert', {'characters': content})
        self.view.run_command('__docblockr_test_replace_cursor_position')
        self.view.set_syntax_file(self.get_syntax_file())

    def get_syntax_file(self):
        raise NotImplementedError('Must be implemented')

    def get_view_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def run_doc_blockr(self):
        self.view.run_command('jsdocs')

    def assertDocBlockrResult(self, expected):
        if isinstance(expected, list):
            expected = '\n'.join(expected)

        # TODO test selections; for now just removing the placeholders
        expected = expected.replace('|CURSOR|', '')
        expected = expected.replace('|SELECTION_BEGIN|', '')
        expected = expected.replace('|SELECTION_END|', '')

        self.assertEquals(expected, self.get_view_content())

class TestJavaScript(ViewTestCase):

    def get_syntax_file(self):
        return 'Packages/JavaScript/JavaScript.tmLanguage'

    def test_basic(self):
        self.set_view_content("\n/**|\nbasic")
        self.run_doc_blockr()
        self.assertDocBlockrResult('\n/**\n * \n */\nbasic')

    def test_empty_doc_blocks_are_created(self):
        self.set_view_content('/**')
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "/**",
            " * |CURSOR|",
            " */"
        ])

    def test_that_function_template_is_added(self):
        self.set_view_content('/**|\nfunction foo () {')
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * |SELECTION_BEGIN|[foo description]|SELECTION_END|',
            ' * @return {[type]} [description]',
            ' */',
            'function foo () {'
        ])

    def test_parameters_are_added_to_function_templates(self):
        self.set_view_content('/**|\nfunction foo (bar, baz) {')
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * |SELECTION_BEGIN|[foo description]|SELECTION_END|',
            ' * @param  {[type]} bar [description]',
            ' * @param  {[type]} baz [description]',
            ' * @return {[type]}     [description]',
            ' */',
            'function foo (bar, baz) {'
        ])

    def test_parameters_are_added_to_function_template_with_description_disabled(self):
        self.set_view_content('/**|\nfunction foo (bar, baz) {')
        self.view.settings().set('jsdocs_function_description', False)
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * @param  |SELECTION_BEGIN|{[type]}|SELECTION_END| bar [description]',
            ' * @param  {[type]} baz [description]',
            ' * @return {[type]}     [description]',
            ' */',
            'function foo (bar, baz) {'
        ])

    def test_parameters_are_added_to_function_template_with_description_disabled_and_spacers_between_sections(self):
        self.set_view_content('/**|\nfunction foo (bar, baz) {')
        self.view.settings().set('jsdocs_function_description', False)
        self.view.settings().set('jsdocs_spacer_between_sections', True)
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * @param  |SELECTION_BEGIN|{[type]}|SELECTION_END| bar [description]',
            ' * @param  {[type]} baz [description]',
            ' *',
            ' * @return {[type]}     [description]',
            ' */',
            'function foo (bar, baz) {'
        ])

    def test_parameters_are_added_to_function_template_with_description_disabled_and_spacer_after_description_isset(self):
        self.set_view_content('/**|\nfunction foo (bar, baz) {')
        self.view.settings().set('jsdocs_function_description', False)
        self.view.settings().set('jsdocs_spacer_between_sections', 'after_description')
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * @param  |SELECTION_BEGIN|{[type]}|SELECTION_END| bar [description]',
            ' * @param  {[type]} baz [description]',
            ' * @return {[type]}     [description]',
            ' */',
            'function foo (bar, baz) {'
        ])

    def test_params_across_multiple_lines_should_be_identified(self):
        self.set_view_content([
            '/**|',
            'function foo(bar,',
            '             baz,',
            '             quux',
            '             ) {'
        ])
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * |SELECTION_BEGIN|[foo description]|SELECTION_END|',
            ' * @param  {[type]} bar  [description]',
            ' * @param  {[type]} baz  [description]',
            ' * @param  {[type]} quux [description]',
            ' * @return {[type]}      [description]',
            ' */',
            'function foo(bar,',
            '             baz,',
            '             quux',
            '             ) {'
        ])

    def test_vars_initialised_to_number_get_placeholders(self):
        self.set_view_content([
            '/**|',
            'var foo = 1;'
        ])
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * |SELECTION_BEGIN|[foo description]|SELECTION_END|',
            ' * @type {Number}',
            ' */',
            'var foo = 1;'
        ])

    def test_vars_string_double_quotes(self):
        self.set_view_content([
            '/**|',
            'var foo = "a";'
        ])
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * |SELECTION_BEGIN|[foo description]|SELECTION_END|',
            ' * @type {String}',
            ' */',
            'var foo = "a";'
        ])

    def test_vars_string_single_quotes(self):
        self.set_view_content([
            '/**|',
            'var foo = \'a\';'
        ])
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * |SELECTION_BEGIN|[foo description]|SELECTION_END|',
            ' * @type {String}',
            ' */',
            'var foo = \'a\';'
        ])

    def test_vars_unknown_type(self):
        self.set_view_content([
            '/**|',
            'var foo = bar;'
        ])
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            '/**',
            ' * |SELECTION_BEGIN|[foo description]|SELECTION_END|',
            ' * @type {[type]}',
            ' */',
            'var foo = bar;'
        ])

class TestPHP(ViewTestCase):

    def get_syntax_file(self):
        # Allows overriding with custom syntax
        php_syntax_file = self.view.settings().get('doc_blockr_tests_php_syntax_file')
        if not php_syntax_file:
            return 'Packages/PHP/PHP.tmLanguage'
        else:
            return php_syntax_file

    def test_basic(self):
        self.set_view_content("<?php\n/**|\nbasic")
        self.run_doc_blockr()
        self.assertDocBlockrResult('<?php\n/**\n * \n */\nbasic')

    def test_issue_292_php_args_pass_by_reference_missing_ampersand_char(self):
        self.set_view_content("<?php\n/**|\nfunction function_name($a1,  $a2 = 'x', array $a3, &$b1, &$b2 = 'x', array &$b3) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[function_name description]|SELECTION_END|",
            " * @param  [type] $a1  [description]",
            " * @param  string $a2  [description]",
            " * @param  array  $a3  [description]",
            " * @param  [type] &$b1 [description]",
            " * @param  string &$b2 [description]",
            " * @param  array  &$b3 [description]",
            " * @return [type]      [description]",
            " */",
            "function function_name($a1,  $a2 = 'x', array $a3, &$b1, &$b2 = 'x', array &$b3) {}"
        ])

    def test_issue_286_php_args_namespace_char_is_missing(self):
        self.set_view_content("<?php\n/**|\nfunction function_name(A\\NS\\ClassName $class) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[function_name description]|SELECTION_END|",
            " * @param  A\\NS\\ClassName $class [description]",
            " * @return [type]                [description]",
            " */",
            "function function_name(A\\NS\\ClassName $class) {}"
        ])

    def test_issue_312_array_type_missing_when_param_is_null(self):
        self.set_view_content("<?php\n/**|\nfunction fname(array $a, array $b = null) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[fname description]|SELECTION_END|",
            " * @param  array      $a [description]",
            " * @param  array|null $b [description]",
            " * @return [type]        [description]",
            " */",
            "function fname(array $a, array $b = null) {}"
        ])

    def test_issue_312_qualified_namespace_type_missing_when_param_is_null(self):
        self.set_view_content("<?php\n/**|\nfunction fname(NS\\ClassA $a, NS\\ClassB $b = null) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[fname description]|SELECTION_END|",
            " * @param  NS\\ClassA      $a [description]",
            " * @param  NS\\ClassB|null $b [description]",
            " * @return [type]            [description]",
            " */",
            "function fname(NS\\ClassA $a, NS\\ClassB $b = null) {}"
        ])

    def test_issue_312_fully_qualified_namespace_type_missing_when_param_is_null(self):
        self.set_view_content("<?php\n/**|\nfunction fname(\\NS\\ClassA $a, \\NS\\ClassB $b = null) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[fname description]|SELECTION_END|",
            " * @param  \\NS\\ClassA      $a [description]",
            " * @param  \\NS\\ClassB|null $b [description]",
            " * @return [type]             [description]",
            " */",
            "function fname(\\NS\\ClassA $a, \\NS\\ClassB $b = null) {}"
        ])

    def test_issue_371_with_long_array_syntax(self):
        self.set_view_content("<?php\n/**|\npublic function test(array $foo = array()) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[test description]|SELECTION_END|",
            " * @param  array  $foo [description]",
            " * @return [type]      [description]",
            " */",
            "public function test(array $foo = array()) {}"
        ])

    def test_issue_371_method_with_short_array_syntax(self):
        self.set_view_content("<?php\n/**|\npublic function test(array $foo = []) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[test description]|SELECTION_END|",
            " * @param  array  $foo [description]",
            " * @return [type]      [description]",
            " */",
            "public function test(array $foo = []) {}"
        ])

    def test_issue_371_method_with_short_array_syntax_with_whitespace(self):
        self.set_view_content("<?php\n/**|\npublic function test(  array   $foo    =     [      ]       ) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[test description]|SELECTION_END|",
            " * @param  array  $foo [description]",
            " * @return [type]      [description]",
            " */",
            "public function test(  array   $foo    =     [      ]       ) {}"
        ])

    def test_issue_372_property_with_short_array_syntax(self):
        self.set_view_content("<?php\n/**|\nprotected $test = [];")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * |SELECTION_BEGIN|[$test description]|SELECTION_END|",
            " * @var array",
            " */",
            "protected $test = [];"
        ])

    def test_optional_function_description(self):
        self.set_view_content("<?php\n/**|\nfunction fname($a) {}")
        self.view.settings().set('jsdocs_function_description', False)
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * @param  |SELECTION_BEGIN|[type]|SELECTION_END| $a [description]",
            " * @return [type]    [description]",
            " */",
            "function fname($a) {}"
        ])

    def test_optional_function_description_with_spacers_between_sections(self):
        self.set_view_content("<?php\n/**|\nfunction fname($a) {}")
        self.view.settings().set('jsdocs_function_description', False)
        self.view.settings().set('jsdocs_spacer_between_sections', True)
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * @param  |SELECTION_BEGIN|[type]|SELECTION_END| $a [description]",
            " *",
            " * @return [type]    [description]",
            " */",
            "function fname($a) {}"
        ])

    def test_optional_function_description_with_spacer_after_description_set_to_true(self):
        self.set_view_content("<?php\n/**|\nfunction fname($a) {}")
        self.view.settings().set('jsdocs_function_description', False)
        self.view.settings().set('jsdocs_spacer_between_sections', 'after_description')
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "<?php",
            "/**",
            " * @param  |SELECTION_BEGIN|[type]|SELECTION_END| $a [description]",
            " * @return [type]    [description]",
            " */",
            "function fname($a) {}"
        ])

class RunDocBlockrTests(sublime_plugin.WindowCommand):

    def run(self):

        self.window.run_command('show_panel', {'panel': 'console'})

        print('')
        print('DocBlockr Tests')
        print('===============')

        suite = unittest.TestSuite()
        test_loader = unittest.TestLoader()

        # TODO move all test cases into tests directory and make test loader auto load testcases from the folder

        suite.addTests(test_loader.loadTestsFromTestCase(TestJavaScript))
        suite.addTests(test_loader.loadTestsFromTestCase(TestPHP))

        # TODO toggle test verbosity
        unittest.TextTestRunner(verbosity=1).run(suite)

        self.window.focus_group(self.window.active_group())
