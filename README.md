DocBlockr is a [Sublime Text 2][sublime] package which makes writing [JSDoc comments][jsdoc] and [PHPDoc comments][phpdoc] a breeze.

## Installation ##

### With Package Control ###

If you have the [Package Control][package_control] package installed, you can install DocBlockr from inside Sublime Text itself. Open the Command Palette and select "Package Control: Install Package", then search for DocBlockr and you're done!

### Without Package Control ###

Go to your Sublime Text 2 Packages directory and clone the repository using the command below:

    git clone https://github.com/spadgos/sublime-jsdocs.git DocBlockr

Don't forget to keep updating it, though!

### Without Git ###

Download the latest version from the [tags page][tags]. Unzip to your Sublime Text Packages folder (you can find this by opening ST2 and selecting `Preferences -> Browse Packages...`). You will need to rename the folder from the default (which will be something like `spadgos-sublime-jsdocs-a4bc2a`) to `DocBlockr`. That's it -- you shouldn't even need to restart ST2.

## Feature requests & bug reports ##

You can leave either of these things [here][issues].

## Changelog ##
- **v2.6.4**, *4 June 2012*
  - Better support for indentation using tabs
  - YUI tags are supported by the autocomplete
  - When only whitespace exists on a docblock line, and `trim_automatic_white_space` is set to true, the whitespace is removed.
  - Better support for comment blocks opened with `/*`
- **v2.6.3**, *30 April 2012*
  - Fixes the join-lines command <kbd>Ctrl+J</kbd> for CoffeeScript.
- **v2.6.2**, *22 March 2012*
  - PHP `__destruct` functions don't get a return value *(thanks to [Alex Whitman](https://github.com/whitman))*.
- **v2.6.1**, *16 March 2012*
  - Fixes bug whereby the return values of functions which are named `set` or `add`, *etc* were not being guessed correctly.
  - `@return` tags are now given a description field *(thanks to [Nick Dowdell](https://github.com/mikulad13))*.
- **v2.6.0**, *4 March 2012*
  - Added CoffeeScript support

Older history can be found in [the history file](https://github.com/spadgos/sublime-jsdocs/blob/master/HISTORY.md).

## Usage ##

> Below are some examples of what the package does. The pipe (`|`) indicates where the cursor will be after the action has run. Note that there are no keyboard shortcuts required to trigger these completions - just type as normal and it happens for you!

### Docblock completion ###

Pressing **enter** or **tab** after `/**` (or `#***` for Coffee-Script) will yield a new line and will close the comment.

    /**<<enter>>

    -- becomes --

    /**
     * |
     */

Single-asterisk comment blocks behave similarly:

    /*<<enter>

    -- becomes --

    /*
    |
     */

If you press asterisk on the first line, it becomes indented with the line above:

    /*
    |<<*>>
     */
    
    /*
     *|
     */

### Function documentation ###

However, if the line directly afterwards contains a function definition, then its name and parameters are parsed and some documentation is automatically added.

    /**<<enter>>
    function foobar (baz, quux) { }

    -- becomes --

    /**
     * [foobar description]
     * @param  {[type]} baz [description]
     * @param  {[type]} quux [description]
     * @return {[type]}
     */
    function foobar (baz, quux) { }

You can then press `tab` to move between the different fields.

In PHP, if [type hinting][typehinting] or default values are used, then those types are prefilled as the datatypes.

    /**|<<enter>>
    function foo(Array $arr, MyClass $cls, $str = "abc", $i = 0, $b = false) {}

    /**
     * [foo description]
     * @param  Array $arr [description]
     * @param  MyClass $cls [description]
     * @param  string $str [description]
     * @param  int $i [description]
     * @param  bool $b [description]
     * @return [type]
     */
    function foo(Array $arr, MyClass $cls, $str = "abc", $i = 0) {}

DocBlockr will try to make an intelligent guess about the return value of the function.

- If the function name is or begins with "set" or "add", then no `@return` is inserted.
- If the function name is or begins with "is" or "has", then it is assumed to return a `Boolean`.
- In Javascript, if the function begins with an uppercase letter then it is assumed that the function is a class definition. No `@return` tag is added.
- In PHP, some of the [magic methods][magicmethods] have their values prefilled:
  - `__construct`, `__destruct`, `__set`, `__unset`, `__wakeup` have no `@return` tag.
  - `__sleep` returns an `Array`.
  - `__toString` returns a `string`.
  - `__isset` returns a `bool`.

### Variable documentation ###

If the line following your docblock contains a variable declaration, DocBlockr will try to determine the data type of the variable and insert that into the comment.

    /**<<enter>>
    foo = 1

    -- becomes --

    /**
     * [foo description]
     * @type {Number}
     */
    foo = 1

If you press `shift+enter` after the opening `/**` then the docblock will be inserted inline.

    /**<<shift+enter>>
    bar = new Module();

    -- becomes --
    /** @type {Module} [bar description] */
    bar = new Module();

DocBlockr will also try to determine the type of the variable from its name. Variables starting with `is` or `has` are assumed to be booleans, and `callback`, `cb`, `done`, `fn`, and `next` are assumed to be functions. If you use your own variable naming system (eg: hungarian notation: booleans all start with `b`, arrays start with `arr`), you can define these rules yourself. Modify the `jsdocs_notation_map` setting *(in `Base File.sublime-settings`)* like so:

```javascript
{
    "jsdocs_notation_map": [
        {
            "prefix": "b", // a prefix, matches only if followed by an underscore or A-Z
            "type": "bool" // translates to "Boolean" in javascript, "bool" in PHP
        },
        {
            "regex": "tbl_?[Rr]ow", // any arbitrary regex to test against the variable name
            "type": "TableRow"      // you can add your own types
        }
    ]
}
```

### Comment extension ###

Pressing enter inside a docblock will automatically insert a leading asterisk and maintain your indentation.

    /**
     *  Foo bar<<enter>>
     */

    -- becomes --

    /**
     *  Foo bar
     *  |
     */
    
    -- and --

    /**
     *  @param foo Lorem ipsum dolor sit amet, consectetur
     *             adipisicing elit, sed do eiusmod tempor<<enter>>
     */
    
    -- becomes --

    /**
     *  @param foo Lorem ipsum dolor sit amet, consectetur
     *             adipisicing elit, sed do eiusmod tempor
     *             |
     */

This applies to docblock comments `/** like this */` as well as inline double-slash comments `// like this`

    //   foo<<enter>>

    -- becomes

    //   foo
    //   |

In either case, you can press `shift+enter` to stop the automatic extension.

Oftentimes, when documenting a parameter, or adding a description to a tag, your description will cover multiple lines. If the line you are on is directly following a tag line, pressing `tab` will move the indentation to the correct position.

    /**
     * @param {String} foo Lorem ipsum dolor sit amet
     * |<<tab>>
     */

     -- becomes

    /**
     * @param {String} foo Lorem ipsum dolor sit amet
     *                     |
     */

### Comment decoration ###

If you write a double-slash comment and then press `Ctrl+Enter`, DocBlockr will 'decorate' that line for you.

    // Foo bar baz<<Ctrl+Enter>>

    -- becomes

    /////////////////
    // Foo bar baz //
    /////////////////

### Reparsing a DocBlock ###

Sometimes, you'll perform some action which clears the fields (sections of text which you can navigate through using `tab`). This leaves you with a number of placeholders in the DocBlock with no easy way to jump to them.

With DocBlockr, you can reparse a comment and reactivate the fields by pressing the hotkey `Ctrl+Alt+Tab`.
    
### Adding extra tags ###

Finally, typing `@` inside a docblock will show a completion list for all tags supported by [JSDoc][jsdoc], the [Google Closure Compiler][closure], [YUIDoc][yui] or [PHPDoc][phpdoc]. Extra help is provided for each of these tags by prefilling the arguments each expects. Pressing `tab` will move the cursor to the next argument.

## Configuration ##

You can access the configuration settings by selecting `Preferences -> Package Settings -> DocBlockr`.

*The `jsdocs_*` prefix is a legacy from days gone by...*

- `jsdocs_indentation_spaces` *(Number)* The number of spaces to indent after the leading asterisk.

        // jsdocs_indentation_spaces = 1
        /**
         * foo
         */

        // jsdocs_indentation_spaces = 5
        /**
         *     foo
         */

- `jsdocs_align_tags` *(String)* Whether the words following the tags should align. Possible values are `'no'`, `'shallow'` and `'deep'`
   
    > For backwards compatibility, `false` is equivalent to `'no'`, `true` is equivalent to `'shallow'`
  
    `'shallow'` will align only the first words after the tag. eg:

        @param    {MyCustomClass} myVariable desc1
        @return   {String} foo desc2
        @property {Number} blahblah desc3
  
    `'deep'` will align each component of the tags, eg:

        @param    {MyCustomClass} myVariable desc1
        @return   {String}        foo        desc2
        @property {Number}        blahblah   desc3
  

- `jsdocs_extra_tags` *(Array.String)* An array of strings, each representing extra boilerplate comments to add to *functions*. These can also include arbitrary text (not just tags).

        // jsdocs_extra_tags = ['This is a cool function', '@author nickf', '@version ${1:version}']
        /**<<enter>>
        function foo (x) {}

        /**
         * [foo description]
         * This is a cool function
         * @author nickf
         * @version [version]
         * @param  {[type]} x [description]
         * @return {[type]}
         */
        function foo (x) {}

- `jsdocs_extend_double_slash` *(Boolean)* Whether double-slash comments should be extended. An example of this feature is described above.

- `jsdocs_deep_indent` *(Boolean)* Whether pressing tab at the start of a line in docblock should indent to match the previous line's description field. An example of this feature is described above.

- `jsdocs_notation_map` *(Array)* An array of notation objects. Each notation object must define either a `prefix` OR a `regex` property, and a `type` property.

- `jsdocs_return_tag` *(String)* The text which should be used for a `@return` tag. By default, `@return` is used, however this can be changed to `@returns` if you use that style.

- `jsdocs_spacer_between_sections` *(Boolean)* If true, then extra blank lines are inserted between the sections of the docblock. Default: `false`.

This is my first package for Sublime Text, and the first time I've written any Python, so I heartily welcome feedback and [feature requests or bug reports][issues].

## Show your love ##

[![Click here to lend your support to: DocBlockr and make a donation at www.pledgie.com !](https://www.pledgie.com/campaigns/16316.png?skin_name=chrome)](http://www.pledgie.com/campaigns/16316)

[closure]: http://code.google.com/closure/compiler/docs/js-for-compiler.html
[issues]: https://github.com/spadgos/sublime-jsdocs/issues
[jsdoc]: http://code.google.com/p/jsdoc-toolkit/wiki/TagReference
[magicmethods]: http://www.php.net/manual/en/language.oop5.magic.php
[package_control]: http://wbond.net/sublime_packages/package_control
[phpdoc]: http://phpdoc.org/
[sublime]: http://www.sublimetext.com/
[svenax]: https://github.com/svenax
[tags]: https://github.com/spadgos/sublime-jsdocs/tags
[typehinting]: http://php.net/manual/en/language.oop5.typehinting.php
[yui]: http://yui.github.com/yuidoc/syntax/index.html
