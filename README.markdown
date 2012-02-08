About Screenplain
=================

You're a hacker. The command line is your home. You know tools like grep, sed
and Git inside out. You have formed a symbiotic relationship with your text
editor. Those tools are powerful in the right hands. But you're also a
screenwriter. Screenwriting is much like programming. It's about structure and
form, and -- obviously -- about reading, writing and modifying huge amounts of
text. You don't want to use software that lacks the power of your hacking
tools just because you're writing a screenplay instead of a shell script.

Enter Screenplain.

Screenplain allows you to write a screenplay as a plain text file using
a format called [Fountain](http://fountain.io). Text files
are simple and supported by all text manipulation software. It's not just for
hackers, too. The simplicity of plain text allows you to easily view and edit
them on devices such as tablets and phones. No need for specific screenwriting
software.

The magic that Screenplain performs is to take your plain text file and
convert it to a good looking screenplay in an industry standard format.
Send that file off to your producer, agent, director or screenwriting
competition. Currently, the supported output formats are FDX and HTML.
PDF will hopefully be supported in a not too distant future.

Screenplain can be used as a command-line application or a library.
An [Online version of Screenplain](http://www.screenplain.com) is also
available.

Note that Screenplain is under development and is missing features and
the master branch may not always work. I'm currently working on supporting
the whole [Fountain](http://fountain.io) specification. (Fountain
was previously known as "Screenplay Markdown" or "SPMD.")

Credits
=======

Screenplain was coded by [Martin Vilcans](http://www.librador.com).

The CSS code that formats Screenplain's HTML output as something that
looks as much as a printed screenplay as is possible in HTML was
created by [Jonathan Poritsky](http://www.candlerblog.com/).

The [Fountain](http://fountain.io) file format is the result of a
collaboration between [Stu Maschwitz](http://prolost.com) and
[John August](http://johnaugust.com/).


License
=======

Screenplain is released under the [MIT license](http://www.opensource.org/licenses/mit-license.php).


Developing
==========

As it was designed to run under Google App Engine, Screenplain should be
compatible with Python 2.5. Use that version for development to make
sure it works. Python 2.5 is no longer available in Ubuntu at least,
but see
[this link](http://kovshenin.com/archives/installing-python-2-5-on-ubuntu-linux-10-10/)
about how to install it. The Python 2.5 requirement may be relaxed
as the online version no longer uses GAE.

To install reportlab, you'll need Python's development files. In
Ubuntu, just do

    sudo apt-get install python2.5-dev

Set up environment using virtualenvwrapper:

    mkvirtualenv -p python2.5 --no-site-packages screenplain
    pip install -r requirements.txt
