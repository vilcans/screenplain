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
convert it to a good looking PDF in standard screenplay format. Send that file
off to your producer, agent, director or screenwriting competition.

Thanks for the inspiration goes to:

  * [Stu Maschwitz](http://prolost.com) for the [Screenplay Markdown](http://prolost.com/spmd)
    post that got me around to actually publish this work when far from finished. Screenplain
    does not use Markdown that his post is about, but the idea is similar.

  * [John August](http://johnaugust.com/) for the [Scrippets](http://scrippets.org/) project.
    The idea for that is similar, as it converts plain text to a formatted output. The focus of
    Scrippets is on presenting snippets of screenplays online, specificially in blog posts and
    comments. Screenplain's format is very similar to Scrippets.

Input format
============

The format of the text input is very much like how you would write a
screenplay on and old typewriter, only that you don't have to worry about tab
stops and line breaks.

Here's an example:

    EXT. CASTLE WALLS - DAY

    Mist. Several seconds of it swirling about.
    Silence possibly, atmospheric music. SUPERIMPOSE "England AD 787".
    After a few more seconds we hear hoofbeats in
    the distance.
    They come slowly closer. Then out of the mist comes KING ARTHUR
    followed by a SERVANT who is banging two half coconuts
    together. ARTHUR raises his hand.

    ARTHUR
    Whoa there!


    SERVANT makes noises of horses halting, with a flourish. ARTHUR
    peers through the mist. CUT TO shot from over his shoulder:
    castle (e.g. Bodium) rising out of the mist. On the castle
    battlements a SOLDIER is dimly seen. He peers down.

     SOLDIER
     Halt! Who goes there?

     ARTHUR
     It is I, Arthur, son of Uther Pendragon,
     from the castle
    of Camelot.
      King of all Britons, defeator of the Saxons,
    sovereign of all England!

Note the free (that is, pretty ugly) format of this input.
After Screenplain has digested it, it will appear correctly formatted like this:

    EXT. CASTLE WALLS - DAY

    Mist. Several seconds of it swirling about. Silence possibly,
    atmospheric music. SUPERIMPOSE "England AD 787". After a few more
    seconds we hear hoofbeats in the distance. They come slowly closer.
    Then out of the mist comes KING ARTHUR followed by a SERVANT who is
    banging two half coconuts together. ARTHUR raises his hand.

                          ARTHUR
              Whoa there!

    SERVANT makes noises of horses halting, with a flourish. ARTHUR
    peers through the mist. CUT TO shot from over his shoulder: castle
    (e.g. Bodium) rising out of the mist. On the castle battlements a
    SOLDIER is dimly seen. He peers down.

                           SOLDIER
              Halt! Who goes there?

                           ARTHUR
              It is I, Arthur, son of Uther
              Pendragon, from the castle of
              Camelot. King of all Britons,
              defeator of the Saxons, sovereign
              of all England!

As you can see, you can write your screenplay without keeping formatting rules in your head.
As Screenplain is just a piece of software, and not a mind-reading robot, it does have rules,
but they are designed to be intuitive and shouldn't distract from the writing.

Basically, what Screenplain does with your plain text file is to split it into paragraphs.
A paragraph is simply one or more lines of text. Paragraphs are separated by one or
more empty lines. The example above contains six paragraphs.

After splitting the text into paragraphs, Screenplain decides what type each paragraph has.
It can be one of:

  * Slug line
  * Dialogue
  * Action

The paragraph type decides how the paragraph will look in the output. See
below for how Screenplain figures out which one of these types each paragraph has.

Slug lines
----------

If a paragraph contains *one single line* written in *capital letters*, Screenplain
assumes it is a slug line.

A slug line is a line that starts a scene. An example of a slug line is `EXT.
EIFFEL TOWER - DAY`, but Screenplain does not care about the format. Screenplain
assumes `SOMEWHERE IN SPACE` is a slug line too.

Dialogue
--------

If a paragraph consists of two or more lines, and the first line is written
only in *capital letters*, Screenplain assumes it is a piece of dialogue. The
first line should contain the name of the speaking character. The rest is
whatever that character says. Simple isn't it? Well, there is an exception: If
a line starts with an opening parenthesis, "(", it starts a parenthetical
block, which is a screenwriter's way of telling the actor how the line is to
be delivered (something that pisses directors off). Parentheticals are
formatted differently from the spoken lines.

Action
------

Any paragraph that is not one of the other types contains descriptions about
what happens in the scene.

TO DO
=====

  * Specify options on the command line. Duh.

  * Installation package.

  * Margins in PDF output.

  * Support for transitions. A `CUT TO:` line is interpreted as a slug line.
    Fixing this should be simple: any single-line paragraph that starts with one
    or more spaces and does not contain lower-case characters should be a
    transition. Any pitfalls with that? What about left-aligned transitions like
    `FADE IN:`?

  * Good support for national characters. It works on my system, but I'm not so
    sure if it will work for everyone. Should we just support UTF-8, or allow
    other encodings?
