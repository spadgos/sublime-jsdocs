syntax = "Packages/PHP/PHP.tmLanguage"

def test_for_issue_292_php_args_pass_by_reference_missing_ampersand_char(helper):
    "PHP pass by reference https://github.com/spadgos/sublime-jsdocs/issues/292"

    helper.insert("/**|\nfunction function_name($a1,  $a2 = 'x', array $a3, &$b1, &$b2 = 'x', array &$b3) {}")
    helper.run()

    return [
        "/**",
        " * |[function_name description]|",
        " * @param  {[type]} $a1  [description]",
        " * @param  string $a2  [description]",
        " * @param  array  $a3  [description]",
        " * @param  {[type]} &$b1 [description]",
        " * @param  string &$b2 [description]",
        " * @param  array  &$b3 [description]",
        " * @return {[type]}      [description]",
        " */",
        "function function_name($a1,  $a2 = 'x', array $a3, &$b1, &$b2 = 'x', array &$b3) {}"
    ]

def test_for_issue_286_php_args_namespace_char_is_missing(helper):
    "PHP namespaces are 'mutilated' for namespaced params https://github.com/spadgos/sublime-jsdocs/issues/286"

    helper.insert("/**|\nfunction function_name(A\NS\ClassName $class) {}")
    helper.run()

    return [
        "/**",
        " * |[function_name description]|",
        " * @param  A\NS\ClassName $class [description]",
        " * @return {[type]}                [description]",
        " */",
        "function function_name(A\NS\ClassName $class) {}"
    ]

def test_issue_312_array_type_missing_when_param_is_null(helper):

    helper.insert("/**|\nfunction fname(array $a, array $b = null) {}")
    helper.run()

    return [
        "/**",
        " * |[fname description]|",
        " * @param  array      $a [description]",
        " * @param  array|null $b [description]",
        " * @return [type]        [description]",
        " */",
        "function fname(array $a, array $b = null) {}"
    ]

def test_issue_312_qualified_namespace_type_missing_when_param_is_null(helper):

    helper.insert("/**|\nfunction fname(NS\ClassA $a, NS\ClassB $b = null) {}")
    helper.run()

    return [
        "/**",
        " * |[fname description]|",
        " * @param  NS\ClassA      $a [description]",
        " * @param  NS\ClassB|null $b [description]",
        " * @return [type]            [description]",
        " */",
        "function fname(NS\ClassA $a, NS\ClassB $b = null) {}"
    ]

def test_issue_312_fully_qualified_namespace_type_missing_when_param_is_null(helper):

    helper.insert("/**|\nfunction fname(\NS\ClassA $a, \NS\ClassB $b = null) {}")
    helper.run()

    return [
        "/**",
        " * |[fname description]|",
        " * @param  \NS\ClassA      $a [description]",
        " * @param  \NS\ClassB|null $b [description]",
        " * @return [type]             [description]",
        " */",
        "function fname(\NS\ClassA $a, \NS\ClassB $b = null) {}"
    ]
