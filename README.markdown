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

Screenplain allows you to write a screenplay as a plain text file. Text files
are simple and supported by all text manipulation software. It's not just for
hackers, too. The simplicity of plain text allows you to easily view and edit
them on devices such as tablets and phones. No need for specific screenwriting
software.

The magic that Screenplain performs is to take your plain text file and
convert it to a good looking screenplay in an industry standard format.
Send that file off to your producer, agent, director or screenwriting
competition. Currently, the supported output formats are FDX and HTML.
PDF will hopefully be supported in a not too distant future.

An [Online version of Screenplain](http://screenplain.appspot.com) is
available, running on Google App Engine.

Note that Screenplain is under development and is missing features and
the master branch may not always work.

Thanks for the inspiration goes to:

  * [Stu Maschwitz](http://prolost.com) for the [Screenplay Markdown](http://prolost.com/spmd)
    post that got me around to actually publish this work when far from finished.
  * [John August](http://johnaugust.com/) for the [Scrippets](http://scrippets.org/) project.
    The idea for that is similar, as it converts plain text to a formatted output. The focus of
    Scrippets is on presenting snippets of screenplays online, specificially in blog posts and
    comments. Screenplain's format is similar to Scrippets.

Input format
============

The input to Screenplain is *Screenplay Markdown* as [proposed by Stu Maschwitz](http://prolost.com/storage/downloads/spmd/SPMD_proposal.html).


License
=======

Screenplain is released under the [MIT license](http://www.opensource.org/licenses/mit-license.php).


Developing
==========

As it should run under Google App Engine, Screenplain should be
compatible with Python 2.5. Use that version for development to make
sure it works. Python 2.5 is no longer available in Ubuntu at least,
but see
[this link](http://kovshenin.com/archives/installing-python-2-5-on-ubuntu-linux-10-10/)
about how to install it.

To install reportlab, you'll need Python's development files. In
Ubuntu, just do

    sudo apt-get install python2.5-dev

Set up environment using virtualenvwrapper:

    mkvirtualenv -p python2.5 --no-site-packages screenplain
    pip install -r requirements.txt

