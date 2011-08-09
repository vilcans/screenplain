About Screenplain
-----------------

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
------------

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
