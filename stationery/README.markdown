STATIONERY
==========

Stationery files are essentially Final Draft template files. They usually have the extension .fdxt.

These files define the way your screenplay looks in Final Draft. They can define whether dialogue should be double-spaced, whether your scene headings should be underlined, what type of font to use, and much more.

Final Draft comes with a number of built-in stationery files, and many more can be downloaded on the Internet.

USAGE
=====

You can use any Final Draft fdx or fdxt file as a stationery with screenplain, even a finished screenplay! Screenplain can filter out the screenplay elements and apply only the formatting and style elements of your existing manuscript to your new document. 

You can use a stationery in one of two ways. The preferred method is to place a file in this directory with the extension .fdxt. We refer to this as "installing" a stationery. Once installed, you can view all of your installed stationery from the help menu in screenplain:

    screenplain -h

_For best results your file should not have any spaces in it's name. If your file has spaces in the name, you will need to enclose the name in quotes ("") when you reference it._

The alternative is to simply specify the absolute path to the fdx or fdxt file on your computer.

You can specify a stationery to use when using the `-f fdx` option with screenplain. To do so, use the `-s` or `--stationery=` option. Here are a few examples:

    screenplain -f fdx -s sitcom in.fountain out.fdx
    # Uses the installed `sitcom.fdxt` file located in this directory.

    screenplain -f fdx -s "my sitcom" in.fountain out.fdx
    # Uses the installed `my sitcom.fdxt` file located in this directory.

    screenplain -f fdx -s "/Users/username/My Old Script.fdx" in.fountain out.fdx
    # The file "/Users/username/My Old Script.fdx" will be treated as a stationery, even though it is not.

_Note that "installed" stationery must have the extension .fdxt or screenplain will not recognize them. If you specify the absolute path to a file outside of this directory, the extension does not matter._
