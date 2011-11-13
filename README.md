This is a [Sublime Text 2][sublime] package which makes writing [JSDoc comments][jsdoc] and [PHPDoc comments][phpdoc] a little bit easier.

## Installation ##

### With Package Control ###

If you have the [Package Control][package_control] package installed, you can install JSDocs from inside Sublime Text itself. Open the Command Palette and select "Package Control: Install Package", then search for JSDocs and you're done!

### Without Package Control ###

Go to your Sublime Text 2 Packages directory and clone the repository using the command below:

    git clone https://github.com/spadgos/sublime-jsdocs.git JSDocs

Don't forget to keep updating it, though!


### Without Git ###

Download the latest version from the [tags page][tags]. Unzip to your Sublime Text Packages folder (you can find this by opening ST2 and selecting `Preferences -> Browse Packages...`). I'd recommend renaming the folder from the default (which will be something like `spadgos-sublime-jsdocs-a4bc2a`) to `JSDocs`. That's it -- you shouldn't even need to restart ST2.

## Feature requests & bug reports ##

You can leave either of these things [here][issues].

## Changelog ##

- **v2.1.0**
  - Added a command to join lines inside a docblock which is smart to leading asterisks
- **v2.0.0**, *6 November 2011*
  - PHP support added!
  - (Almost) complete rewrite to allow for any new languages to be added easily
    - *Please send feature requests or pull requests for new languages you'd like to add*
  - More options for aligning tags
- **v1.3.0**, *5 November 2011*
  - Improvements to handling of single-line comments
  - Functions beginning with `is` or `has` are assumed to return Booleans
  - Consolidated settings files into `Base File.sublime-settings`. **If you had configured your settings in `jsdocs.sublime-settings`, please move them to the Base File settings.**
  - Setting `jsdocs_extend_double_slashes` controls whether single-line comments are extended.
  - Pressing `tab` in a docblock will tab to match the description block of the previous tag. Use `jsdocs_deep_indent` to toggle this behaviour.
- **v1.2.0**, *6 October 2011*
  - Variable declarations can be documented. `Shift+enter` to make these inline
  - Double slash comments (`// like this`) are extended when `enter` is pressed
  - Class definitions detected and treated slightly differently (no return values pre-filled)
- **v1.1.0**, *3 October 2011*
  - JSDocs parses the line following the comment to automatically prefill some documentation for you.
  - Settings available via menu
- **v1.0.0**, *28 September 2011*
  - Initial release
  - Comments are automatically closed, extended and indented.

## Usage ##

> Below are some examples of what the package does. The pipe (`|`) indicates where the cursor will be after the action has run. Note that there are no keyboard shortcuts required to trigger these completions - just type as normal and it happens for you!

### Docblock completion ###

Pressing enter after `/**` will yield a new line and will close the comment.

    /**<<enter>>

    -- becomes --

    /**
     * |
     */

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

JSDocs will try to make an intelligent guess about the return value of the function.

- If the function name begins with "set" or "add", then no `@return` is inserted.
- If the function name beings with "is" or "has", then it is assumed to return a `Boolean`.
- In Javascript, if the function begins with an uppercase letter then it is assumed that the function is a class definition. No `@return` tag is added.
- In PHP, some of the [magic methods][magicmethods] have their values prefilled:
  - `__construct`, `__set`, `__unset`, `__wakeup` have no `@return` tag.
  - `__sleep` returns an `Array`.
  - `__toString` returns a `string`.
  - `__isset` returns a `bool`.

### Variable documentation ###

If the line following your docblock contains a variable declaration, JSDocs will try to determine the data type of the variable and insert that into the comment.

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

### Adding extra tags ###

Finally, typing `@` inside a docblock will show a completion list for all tags supported by [JSDoc][jsdoc] or the [Google Closure Compiler][closure]. Extra help is provided for each of these tags by prefilling the arguments each expects. Pressing `tab` will move the cursor to the next argument.

Exhaustively, these tags are:

    @param, @return, @author,
    @augments,
    @borrows,
    @class, @const, @constant, @constructor, @constructs,
    @default, @define, @deprecated, @description,
    @enum, @event, @example, @extends,
    @field, @fileOverview, @function,
    @ignore, @implements, @inheritDoc, @inner, @interface,
    @lends, @license, {@link}
    @memberOf,
    @name, @namespace, @nosideeffects,
    @override,
    @preserve, @private, @property, @protected, @public,
    @requires,
    @see, @since, @static,
    @this, @throws, @type, @typedef,
    @version

## Configuration ##

You can access the configuration settings by selecting `Preferences -> Package Settings -> JSDocs`.

- **`jsdocs_indentation_spaces`** *(Number)* The number of spaces to indent after the leading asterisk.

        // jsdocs_indentation_spaces = 1
        /**
         * foo
         */

        // jsdocs_indentation_spaces = 5
        /**
         *     foo
         */

- **`jsdocs_align_tags`** *(String)* Whether the words following the tags should align. Possible values are `'no'`, `'shallow'` and `'deep'`
   
    > For backwards compatibility, `false` is equivalent to `'no'`, `true` is equivalent to `'shallow'`
  
    `'shallow'` will align only the first words after the tag. eg:

        @param    {MyCustomClass} myVariable desc1
        @return   {String} foo desc2
        @property {Number} blahblah desc3
  
    `'deep'` will align each component of the tags, eg:

        @param    {MyCustomClass} myVariable desc1
        @return   {String}        foo        desc2
        @property {Number}        blahblah   desc3
  

- **`jsdocs_extra_tags`** *(Array.String)* An array of strings, each representing extra boilerplate comments to add to *functions*. These can also include arbitrary text (not just tags).

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

- **`jsdocs_extend_double_slash`** *(Boolean)* Whether double-slash comments should be extended. An example of this feature is described above.

- **`jsdocs_deep_indent`** *(Boolean)* Whether pressing tab at the start of a line in docblock should indent to match the previous line's description field. An example of this feature is described above.

This is my first package for Sublime Text, and the first time I've written any Python, so I heartily welcome feedback and [feature requests or bug reports][issues].


[sublime]: http://www.sublimetext.com/
[jsdoc]: http://code.google.com/p/jsdoc-toolkit/wiki/TagReference
[phpdoc]: http://phpdoc.org/
[closure]: http://code.google.com/closure/compiler/docs/js-for-compiler.html
[issues]: https://github.com/spadgos/sublime-jsdocs/issues
[package_control]: http://wbond.net/sublime_packages/package_control
[typehinting]: http://php.net/manual/en/language.oop5.typehinting.php
[tags]: https://github.com/spadgos/sublime-jsdocs/tags
[magicmethods]: http://www.php.net/manual/en/language.oop5.magic.php
