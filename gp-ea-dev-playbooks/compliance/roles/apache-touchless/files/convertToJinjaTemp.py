#!/usr/bin/env python2

""" Utility to convert erb to jinja template for apache touchless configuration for app specific conf files """

def main(filename):

    tag_space_dict = {
        "<%if": "<% if",
        "<%for": "<% for",
        "<%else":"<% else",
        "else%>":"else %>",
        "<%end":"<% end",
        "end%>":"end %>",
    }

    output = []
    with open(filename) as stream:
        IF_LOOP = False
        FOR_LOOP = False
        for row in stream.readlines():
            # Add spaces in case they are not there
            for key in tag_space_dict:
                row = row.replace(key, tag_space_dict[key])

            if "<%=" in row:
                row = row.replace("<%= @", "{{ ")
                row = row.replace("<%=", "{{")
                row = row.replace("%>", "}}")
            elif "<% if" in row:
                row = row.replace("<% if", "{% if ")
                row = row.replace("%>", "%}")
                IF_LOOP = True
            elif "<% for " in row:
                row = row.replace("<% for", "{% for ")
                row = row.replace("%>", "%}")
                FOR_LOOP = True
            elif "<% else %>" in row:
                row = row.replace("<% else %>", "{% else %}")
            elif "<% end %>" in row:
                if IF_LOOP is True:
                    row = row.replace("<% end %>", "{% endif %}")
                    IF_LOOP = False
                elif FOR_LOOP is True:
                    row = row.replace("<% end %>", "{% endfor %}")
                    FOR_LOOP = False
            output.append(row)

    print "".join(output)
    with open(filename + ".j2", "w") as stream:
        stream.write("".join(output))