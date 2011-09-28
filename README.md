This is a [Sublime Text][sublime] package which makes writing [JSDoc comments][jsdoc] a little bit easier.

Installing the package will assist by automatically adding code as you type:

Below are some examples of what the package does. The pipe (`|`) indicates where the cursor will be after the action has run.

Pressing enter after `/**` will yield a new line and will close the comment for you.

    /**<<enter>>

    -- becomes --

    /**
     * |
     */

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

Finally, typing `@` inside a docblock will show a completion list for all tags supported by [JSDoc][jsdoc] or the [Google Closure Compiler][closure]. Extra help is provided for each of these tags by prefilling the arguments each expects. Pressing `tab` will move the cursor to the next argument.

Exhaustively, these tags are:

- `@param`
- `@return`
- `@author`
- `@augments`
- `@borrows`
- `@class`
- `@const`
- `@constant`
- `@constructor`
- `@constructs`
- `@default`
- `@define`
- `@deprecated`
- `@description`
- `@enum`
- `@event`
- `@example`
- `@extends`
- `@field`
- `@fileOverview`
- `@function`
- `@ignore`
- `@implements`
- `@inheritDoc`
- `@inner`
- `@interface`
- `@lends`
- `@license`
- `@memberOf`
- `@name`
- `@namespace`
- `@nosideeffects`
- `@override`
- `@preserve`
- `@private`
- `@property`
- `@protected`
- `@public`
- `@requires`
- `@see`
- `@since`
- `@static`
- `@this`
- `@throws`
- `@type`
- `@typedef`
- `@version`
- `{@link}`

This is my first package for Sublime Text, so I heartily welcome feedback and [feature requests or bug reports][issues].

## Installation ##

### With Package Control ###

If you have the [Package Control][package_control] package installed, you can install JSDocs from inside Sublime Text itself. Open the Command Palette and select "Package Control: Install Package", then search for JSDocs and you're done!

### Without Package Control ###

Go to your Sublime Text 2 Packages directory and clone the repository using the command below:

    git clone https://github.com/spadgos/sublime-jsdocs.git JSDocs


[sublime]: http://www.sublimetext.com/
[jsdoc]: http://code.google.com/p/jsdoc-toolkit/wiki/TagReference
[closure]: http://code.google.com/closure/compiler/docs/js-for-compiler.html
[issues]: https://github.com/spadgos/sublime-jsdocs/issues
[package_control]: http://wbond.net/sublime_packages/package_control
