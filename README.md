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
- **v2.4.1**, *2 February 2012*
  - Fixed bug [#36](https://github.com/spadgos/sublime-jsdocs/issues/36) whereby docblocks were not being properly extended inside of `<script>` tags in a HTML document.
- **v2.4.0**, *29 January 2012*
  - `Enter` at the end of a comment block (ie: after the closing `*/`) will insert a newline and de-indent by one space.
- **v2.3.0**, *15 January 2012*
  - `Ctrl+Enter` on a double-slash comment will now decorate that comment.
  - Added a setting (`jsdocs_spacer_between_sections`) to add spacer lines between sections of a docblock.
- **v2.2.2**, *12 January 2012*
  - Separated JS and PHP completions files. PHP completions don't have brackets around type information any more.
  - PHP now uses `@var` (instead of `@type`) for documenting variable declarations.
  - *Both of these changes are thanks to [svenax][svenax]*
- **v2.2.1**, *11 January 2012*
  - DocBlocks can be triggered by pressing `tab` after `/**`
  - Some bugfixes due to auto-complete changes in Sublime Text.
  - Fixed bug where indenting would not work on the first line of a comment.
- **v2.2.0**, *5 January 2012*
  - A configuration option can be set so that either `@return` or `@returns` is used in your documentation. 
  - Language-specific tags now will only show for that language (eg: PHP has no `@interface` tag).
- **v2.1.3**, *31 December 2011*
  - Changed path for macro file to point to `Packages/DocBlockr`. If you are having issues, make sure that the plugin is installed in that location (**not** the previous location `Packages/JSDocs`).
- **v2.1.2**, *31 December 2011*
  - Renamed from *JSDocs* to *DocBlockr*, since it now does more than just Javascript.
- **v2.1.1**, *23 November 2011*
  - Fixed bug which broke the completions list
- **v2.1.0**, *19 November 2011*
  - Added a command to join lines inside a docblock which is smart to leading asterisks
  - Variable types are guessed from their name. `is` and `has` are assumed to be Booleans, and `callback`, `cb`, `done`, `fn` and `next` are assumed to be Functions.
  - You can now define your own patterns for mapping a variable name to a type.
  - Autocomplete works better now. `@` will also insert the "@" character, allowing you to add any tag you like, even if it isn't in the autocomplete list.
  - Added the full set of [PHPDoc][phpdoc] tags.
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
  - DocBlockr parses the line following the comment to automatically prefill some documentation for you.
  - Settings available via menu
- **v1.0.0**, *28 September 2011*
  - Initial release
  - Comments are automatically closed, extended and indented.

## Usage ##

> Below are some examples of what the package does. The pipe (`|`) indicates where the cursor will be after the action has run. Note that there are no keyboard shortcuts required to trigger these completions - just type as normal and it happens for you!

### Docblock completion ###

Pressing **enter** or **tab** after `/**` will yield a new line and will close the comment.

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

DocBlockr will try to make an intelligent guess about the return value of the function.

- If the function name begins with "set" or "add", then no `@return` is inserted.
- If the function name beings with "is" or "has", then it is assumed to return a `Boolean`.
- In Javascript, if the function begins with an uppercase letter then it is assumed that the function is a class definition. No `@return` tag is added.
- In PHP, some of the [magic methods][magicmethods] have their values prefilled:
  - `__construct`, `__set`, `__unset`, `__wakeup` have no `@return` tag.
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
    
### Adding extra tags ###

Finally, typing `@` inside a docblock will show a completion list for all tags supported by [JSDoc][jsdoc], the [Google Closure Compiler][closure] or [PHPDoc][phpdoc]. Extra help is provided for each of these tags by prefilling the arguments each expects. Pressing `tab` will move the cursor to the next argument.

Exhaustively, these tags are:

    @param @return @returns @author
    @abstract @access @augments
    @borrows
    @category @class @const @constant @constructor @constructs @copyright
    @default @define @deprecated @description
    @enum @event @example @extends
    @field @fileOverview @filesource @final @function
    @global
    @ignore @implements @inheritDoc @inner @interface @internal
    @lends @license @link
    @memberOf @method
    @name @namespace @nosideeffects
    @override
    @package @preserve @private @property @protected @public
    @requires
    @see @since @static @staticvar @subpackage
    @this @throws @todo @tutorial @type @typedef
    @uses
    @var @version


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
