__author__ = 'gicmo'
import sys
import re


def mk_tex_text(text, is_body=False):
    if text is None:
        return u""

    text = re.sub(ur'(?<!(?<!\\)\\)(&)', ur"\&", text)
    text = re.sub(ur'(?<!(?<!\\)\\)(#)', ur"\#", text)
    text = re.sub(ur'(?<!(?<!\\)\\)(%)', ur"\%", text)

    if not is_body:
        text = re.sub(ur'(?<!(?<!\\)\\)(_)', ur"\_", text)

    text = text.replace('', '')

    return text


def check_cur_state(abstract, state):
    if abstract is None:
        return {'cur_chap': None, 'cur_section': None}

    if abstract.conference is None:
        return None, None

    res_chapter, res_section = None, None
    group = abstract.conference.get_group(abstract.sort_id)
    if state['cur_chap'] != group.name:
        state['cur_chap'] = group.name
        res_chapter = group.name

    section = abstract.topic
    if section != state['cur_section']:
        state['cur_section'] = section
        res_section = section

    return res_chapter, res_section

basic_tempate = r"""
<%!
from gca.tex import mk_tex_text, check_cur_state
import os
%>

%if not bare:

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

\usepackage{chapterthumb}

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

\usepackage{hyperref}

\usepackage{multind}
\makeindex{pages}
\makeindex{posterid}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\begin{document}

\frontmatter

%%%%%%%%%%%%%
\mainmatter

%endif


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

<%
cur_state = check_cur_state(None, None)
%>

% for idx, abstract in enumerate(abstracts):
<%
    new_chapter, new_section = check_cur_state(abstract, cur_state)
%>
    %if new_chapter is not None:
    \cleardoublepage \chapter{${new_chapter}} \addtocounter{chapterthumb}{1} \newpage
    %endif
    %if new_section is not None:
    \section*{${new_section}}
    %endif

    ${mk_abstract(idx, abstract, figures is not None)}
% endfor

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% appendix
%if not bare:
\backmatter
\chapter{Index}
\sffamily\footnotesize
\chapter{Index}
\printindex{pages}{Authors}

\end{document}
%endif
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

<%def name="mk_abstract(idx, abstract, include_figures)">
    \subsection*{\textmd{\sffamily [${abstract.poster_id}]} \hspace{1mm} ${mk_tex_text(abstract.title)} }
    \noindent ${mk_authors(abstract.authors)}\\*[0.5ex]
    \small
    ${mk_affiliations(abstract.affiliations)}
    %if abstract.doi:
    doi: \href{http://dx.doi.org/${abstract.doi}}{${abstract.doi}}
    %endif
    %%\normalsize \nopagebreak\\*[-2.0ex]
    \normalsize

    ${abstract.text}
    %if abstract.alt_id > 0 and abstract.conference is not None:


        \textbf{See also Poster}: ${abstract.conference.sort_id_to_string(abstract.alt_id)}
    %endif
    %if len(abstract.figures) and include_figures:
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
  ${author.format_name()}${epi}${sep}\index{pages}{${author.index_name}}\
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
  \item[${idx+1}] ${mk_tex_text(ref.display_text)} ${mk_doi(ref)}
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

<%def name="mk_doi(ref)">
%if ref.doi:
\href{${ref.doi_link}}{${mk_tex_text(ref.doi)}}\
%endif
</%def>

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""