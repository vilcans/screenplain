import os


def get_stationery(filename):
    # If the user didn't specify the absolute path
    # Then we'll check our stationery directory.
    if not os.path.exists(filename):
        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        dirname = os.path.join(basedir, 'stationery')
        if not filename.endswith('.fdxt'):
            filename = os.path.join(dirname, filename + ".fdxt")
        else:
            filename = os.path.join(dirname, filename)

    # Read the file into a list.
    try:
        with open(filename) as f:
            content = f.readlines()
            # Find the first match where the <Content> tag ends.
            # We will remove everything up to this tag.
            # This way we only return the formatting section.
            # The way I do this could be a problem if the
            # Final Draft document isn't formatted *exactly* correct
            # with two spaces before the tag. This should
            # not be a problem unless we are using a template
            # generated by something other than Final Draft.
            eoc_indice = content.index('  </Content>\n')
            eoc_indice = eoc_indice + 1
            # Slice the list. Remove everything before that line
            content = content[eoc_indice:]

           # Now remove the last line
            eof_indice = content.index('</FinalDraft>\n')
            content = content[:eof_indice]
    except IOError, e:
        print "\nError reading file: " + filename
        print "Please ensure that the file exists and is readable."
        print "TIP: enclose the name in quotes if the name includes spaces."
        print "\nContinuing without stationery file...\n"
        content = []

    # All is well. Let's convert this sucker to a string.
    return "\n".join(content)


def list_stationery():
    basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    dirname = os.path.join(basedir, 'stationery')
    installed = []
    for files in os.listdir(dirname):
        if files.endswith(".fdxt"):
            installed.append("'" + os.path.splitext(files)[0] + "'")
    return installed
