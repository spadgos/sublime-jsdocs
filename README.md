This is a [Sublime Text][sublime] package which makes writing [JSDoc comments][jsdoc] a little bit easier.

## Installation ##

### With Package Control ###

If you have the [Package Control][package_control] package installed, you can install JSDocs from inside Sublime Text itself. Open the Command Palette and select "Package Control: Install Package", then search for JSDocs and you're done!

### Without Package Control ###

Go to your Sublime Text 2 Packages directory and clone the repository using the command below:

    git clone https://github.com/spadgos/sublime-jsdocs.git JSDocs

## Changelog ##

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

If the function name begins with "set" or "add", then no `@return` is inserted.

If the function name begins with an uppercase letter `[A-Z]`, then it is assumed that the function is a class definition. No `@return` tag is added - instead replaced with `@class`.

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

You can access the configuration settings by selecting `Prefences -> Package Settings -> JSDocs`. Currently there are three settings:

- **`indentation_spaces`** *(Number)* The number of spaces to indent after the leading asterisk.

        // indentation_spaces = 1
        /**
         * foo
         */

        // indentation_spaces = 5
        /**
         *     foo
         */

- **`align_tags`** *(Boolean)* Whether to align the text following the tags.

        // align_tags = false
        /**
         * @param {Number} x
         * @return {Number}
         */
        
        // align_tags = true
        /**
         * @param  {Number} x
         * @return {Number}
         */

- **`extra_tags`** *(Array.String)* An array of strings, each representing extra boilerplate comments to add to *functions*. These can also include arbitrary text (not just tags).

        // extra_tags = ['This is a cool function', '@author nickf', '@version ${1:version}']
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


This is my first package for Sublime Text, and the first time I've written any Python, so I heartily welcome feedback and [feature requests or bug reports][issues].


[sublime]: http://www.sublimetext.com/
[jsdoc]: http://code.google.com/p/jsdoc-toolkit/wiki/TagReference
[closure]: http://code.google.com/closure/compiler/docs/js-for-compiler.html
[issues]: https://github.com/spadgos/sublime-jsdocs/issues
[package_control]: http://wbond.net/sublime_packages/package_control
