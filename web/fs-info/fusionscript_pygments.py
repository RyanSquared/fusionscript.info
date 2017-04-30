from pygments.lexer import RegexLexer
from pygments.token import (Comment, Keyword, Name, Number, Operator,
                            Punctuation, String, Text)


class FusionScriptLexer(RegexLexer):
    name = "FusionScript"
    aliases = ["fuse", "fusion"]
    filenames = ["*.fuse"]

    tokens = {
        "root": [
            (r"--.*$", Comment),
            (r"\b(fnl|itr|class|ternary|re)\b", Keyword),
            (r"\b(local|class|interface|extends|implements|using)\b", Keyword),
            (r"\b(break|return|yield)\b", Keyword),
            (r"\b(if|else|elseif|while|for|in|async)\b", Keyword),
            (r"\b(true|false)\b", Name.Constant),
            (r"@[A-Za-z]*", Name.Variable.Class),  # @value_here
            (r"\b[A-Z_]+\b", Name.Constant),  # MACRO_HERE
            (r"[A-Z][A-Za-z]*", Name.Class),  # ClassNameHere
            (r"self", Name.Builtin.Pseudo),  # self
            (r"[A-Za-z_][A-Za-z_0-9]*", Name.Variable),  # Name_goes0here
            (r"/(\.|[^/])*/", String.Regex),  # /{(&('.'%d/%d))%d*[.]%d*}/
            (r'"(\.|[^"])*"', String.Double),  # "test"
            (r"'(\.|[^'])*'", String.Single),  # 'test'
            (r"(?s)\[(=*)\[((?!\]\1\]).)*?\]\1\]", String.Heredoc),  # [[test]]
            (r"[\[\]:.();{}]", Punctuation),  # test[x]
            (r"&&|\|\||<<|>>|\?:", Operator),
            (r"[#!~*&%<>^\|=,+-/]", Operator),
            (r"0[xX][0-9A-Fa-f]+([pP][-+]?[0-9]+)?", Number),  # hex
            (r"(?=(\.\d|\d))\d*\.?\d*([eE][-+]?[0-9]+)?", Number),  # decimal
            (r"\s+", Text.Whitespace),
        ]
    }
