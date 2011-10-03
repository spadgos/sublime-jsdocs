This is a [Sublime Text][sublime] package which makes writing [JSDoc comments][jsdoc] a little bit easier.

## Installation ##

### With Package Control ###

If you have the [Package Control][package_control] package installed, you can install JSDocs from inside Sublime Text itself. Open the Command Palette and select "Package Control: Install Package", then search for JSDocs and you're done!

### Without Package Control ###

Go to your Sublime Text 2 Packages directory and clone the repository using the command below:

    git clone https://github.com/spadgos/sublime-jsdocs.git JSDocs

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

### Writing extra documentation ###

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
