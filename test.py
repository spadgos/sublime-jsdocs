import sublime
import sublime_plugin
import unittest

class DocBlockrTestReplaceCursorPosition(sublime_plugin.TextCommand):
    def run(self, edit):
        cursor_placeholder = self.view.find('\|', 0)
        if cursor_placeholder.empty():
            return

        self.view.sel().clear()
        self.view.sel().add(cursor_placeholder.begin())
        self.view.replace(edit, cursor_placeholder, '')

class ViewTestCase(unittest.TestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        if self.view:
            if int(sublime.version()) < 3000:
                self.view.window().run_command('close')
            else:
                self.view.close()

    def set_view_content(self, content):
        self.view.run_command('insert', {'characters': content})
        self.view.run_command('doc_blockr_test_replace_cursor_position')

        # The reason for this is that if a uses a different syntax other
        # than the default then setting the default syntax won't nothing.
        php_syntax_file = self.view.settings().get('doc_blockr_tests_php_syntax_file')
        if not php_syntax_file:
            self.view.set_syntax_file('Packages/PHP/PHP.tmLanguage')
        else:
            self.view.set_syntax_file(php_syntax_file)

    def get_view_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def run_doc_blockr(self):
        self.view.run_command('jsdocs')

    def assertDocBlockrResult(self, expected):
        if isinstance(expected, list):
            expected = '\n'.join(expected)

        # TODO test selections; for now just removing the placeholders
        expected = expected.replace('|SELECTION_BEGIN|', '')
        expected = expected.replace('|SELECTION_END|', '')

        self.assertEquals(expected, self.get_view_content())

class TestPHP(ViewTestCase):

    def test_basic(self):
        self.set_view_content("/**|\nbasic")
        self.run_doc_blockr()
        self.assertDocBlockrResult('/**\n * \n */\nbasic')

    def test_issue_292_php_args_pass_by_reference_missing_ampersand_char(self):
        self.set_view_content("/**|\nfunction function_name($a1,  $a2 = 'x', array $a3, &$b1, &$b2 = 'x', array &$b3) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
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
        self.set_view_content("/**|\nfunction function_name(A\\NS\\ClassName $class) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "/**",
            " * |SELECTION_BEGIN|[function_name description]|SELECTION_END|",
            " * @param  A\\NS\\ClassName $class [description]",
            " * @return [type]                [description]",
            " */",
            "function function_name(A\\NS\\ClassName $class) {}"
        ])

    def test_issue_312_array_type_missing_when_param_is_null(self):
        self.set_view_content("/**|\nfunction fname(array $a, array $b = null) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "/**",
            " * |SELECTION_BEGIN|[fname description]|SELECTION_END|",
            " * @param  array      $a [description]",
            " * @param  array|null $b [description]",
            " * @return [type]        [description]",
            " */",
            "function fname(array $a, array $b = null) {}"
        ])

    def test_issue_312_qualified_namespace_type_missing_when_param_is_null(self):
        self.set_view_content("/**|\nfunction fname(NS\\ClassA $a, NS\\ClassB $b = null) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "/**",
            " * |SELECTION_BEGIN|[fname description]|SELECTION_END|",
            " * @param  NS\\ClassA      $a [description]",
            " * @param  NS\\ClassB|null $b [description]",
            " * @return [type]            [description]",
            " */",
            "function fname(NS\\ClassA $a, NS\\ClassB $b = null) {}"
        ])

    def test_issue_312_fully_qualified_namespace_type_missing_when_param_is_null(self):
        self.set_view_content("/**|\nfunction fname(\\NS\\ClassA $a, \\NS\\ClassB $b = null) {}")
        self.run_doc_blockr()
        self.assertDocBlockrResult([
            "/**",
            " * |SELECTION_BEGIN|[fname description]|SELECTION_END|",
            " * @param  \\NS\\ClassA      $a [description]",
            " * @param  \\NS\\ClassB|null $b [description]",
            " * @return [type]             [description]",
            " */",
            "function fname(\\NS\\ClassA $a, \\NS\\ClassB $b = null) {}"
        ])

class RunDocBlockrTests(sublime_plugin.WindowCommand):

    def run(self):
        print('---------------')
        print('DocBlockr Tests')
        print('---------------')

        self.window.run_command('show_panel', {'panel': 'console'})

        unittest.TextTestRunner(verbosity=1).run(
            unittest.TestLoader().loadTestsFromTestCase(TestPHP)
        )

        self.window.focus_group(self.window.active_group())
