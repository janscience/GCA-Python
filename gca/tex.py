__author__ = 'gicmo'
import sys
import re


def mk_tex_text(text, is_body=False):
    if text is None:
        return u""

    text = re.sub(ur'(?<!(?<!\\)\\)(&)', ur"\&", text)
    text = re.sub(ur'(?<!(?<!\\)\\)(#)', ur"\#", text)

    if not is_body:
        text = re.sub(ur'(?<!(?<!\\)\\)(_)', ur"\_", text)

    text = text.replace('', '')

    return text


basic_tempate = r"""
<%!
from gca.tex import mk_tex_text
import os
%>

%%!TEX TS-program = lualatex
%%!TEX encoding = UTF-8 Unicode

\documentclass[%%
a5paper,
9pt,%%
twoside,%%
final%%
]{scrbook}

\usepackage{ucs}
\usepackage[greek, french, spanish, english]{babel}
\usepackage[utf8x]{inputenc}
\usepackage[LGR, T1]{fontenc}
\usepackage{textcomp}
\usepackage{textgreek}
\usepackage{microtype}
\DeclareUnicodeCharacter{8208}{-}
\DeclareUnicodeCharacter{8210}{-}
\DeclareUnicodeCharacter{8239}{ }
\DeclareUnicodeCharacter{8288}{}
\DeclareUnicodeCharacter{57404}{t}
\DeclareUnicodeCharacter{700}{'}

\usepackage{mathtools}
\usepackage{amssymb}

% if figures is not None:
\usepackage{caption}
\usepackage{graphicx}
\graphicspath{ {${figures}/} }
%endif

\usepackage{needspace}

\parskip0.5ex

\setlength{\parindent}{0in}

\setlength{\topmargin}{-23mm}
\setlength{\oddsidemargin}{-8mm}
\setlength{\evensidemargin}{-12mm}
\setlength{\textwidth}{117mm}
\setlength{\textheight}{185mm}
\setlength{\footskip}{20pt}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\begin{document}


\frontmatter

%%%%%%%%%%%%%
\mainmatter


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% for idx, abstract in enumerate(abstracts):
    ${mk_abstract(idx, abstract)}
% endfor

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
<%def name="mk_abstract(idx, abstract)">
    \subsection*{\textmd{\sffamily [${idx}]} \hspace{1mm} ${mk_tex_text(abstract.title)} }
    \noindent ${mk_authors(abstract.authors)}\\*[0.5ex]
    \small
    ${mk_affiliations(abstract.affiliations)}
    %%\normalsize \nopagebreak\\*[-2.0ex]
    \normalsize

    ${abstract.text}
    %if len(abstract.figures) and figures_path is not None:
        ${mk_figure(abstract.figures[0])}
    %endif
    %if abstract.acknowledgements:
        ${mk_acknowledgements(abstract.acknowledgements)}
    %endif
    %if abstract.references:
        ${mk_references(abstract.references)}
    %endif
    \small
    Topic: ${abstract.topic}
    %if abstract.is_talk:
    Talk: ${mk_tex_text(abstract.reason_for_talk)}\\*[-0.5ex]
    %endif
    \normalsize
    \vskip \glueexpr\smallskipamount + 0pt plus 10ex minus 3ex\relax
    %%\pagebreak[3]
    \clearpage
</%def>

<%def name="mk_authors(authors)">
% for idx, author in enumerate(authors):
  <%
     sep = ', ' if idx+1 < len(authors) else ''
     aff = author.format_affiliation()
     epi = '$^{%s}$' % aff if aff else ''
  %>
  ${author.format_name()}${epi}${sep}\
% endfor
</%def>

<%def name="mk_affiliations(affiliations)">
% for idx, affiliation in enumerate(affiliations):
  \emph{${idx+1}. ${mk_tex_text(affiliation.format_affiliation())}}\\*[-0.5ex]
% endfor
</%def>

<%def name="mk_acknowledgements(acknowledgements)">
\vspace{1ex}\renewcommand{\baselinestretch}{0.9}\footnotesize \textbf{Acknowledgements} \\*[0em]
${mk_tex_text(acknowledgements)}\
\par\renewcommand{\baselinestretch}{1.0}\normalsize
</%def>

<%def name="mk_references(references)">
\vspace{1ex}
\renewcommand{\baselinestretch}{0.9}\footnotesize \needspace{3\baselineskip}\textbf{References}\nopagebreak
\begin{list}{}{\leftmargin=1.5em \listparindent=0pt \rightmargin=0pt \topsep=0.5ex \parskip=0pt \partopsep=0pt \itemsep=0pt \parsep=0pt}
%for idx, ref in enumerate(references):
  \item[${idx+1}] ${mk_tex_text(ref.text)}
%endfor
\end{list}
\par\renewcommand{\baselinestretch}{1.0}\normalsize
</%def>

<%def name="mk_figure(figure)">
\vspace{1mm}\makebox[\textwidth][c]{\begin{minipage}[c]{0.9\linewidth}
    \centering
    \includegraphics[width=0.50\textwidth]{${figure.uuid}}
    \captionof*{figure}{\small ${mk_tex_text(figure.caption)}}
\end{minipage}
\vspace{1em}
}
</%def>

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\end{document}
"""