This is a [Sublime Text][1] plugin which makes writing [JSDoc comments][2] a little bit easier.

The installing the plugin will assist by automatically adding code as you type:

Below are some examples of what the plugin does. The pipe (`|`) indicates where the cursor will be after the action has run.

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
     *             adipisicing elit, sed do eiusmod tempor<<enter>>
     *             |
     */

Finally, typing `@` inside a docblock will show a completion list for all tags supported by [JSDoc][2] or the [Google Closure Compiler][3]. Extra help is provided for each of these tags by prefilling the arguments each expects. Pressing tab will move the cursor to the next argument.

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

This is my first package for Sublime Text, so I heartily welcome feedback and [feature requests or bug reports][4].

[1]: http://www.sublimetext.com/
[2]: http://code.google.com/p/jsdoc-toolkit/wiki/TagReference
[3]: http://code.google.com/closure/compiler/docs/js-for-compiler.html
[4]: https://github.com/spadgos/sublime-jsdocs/issues
