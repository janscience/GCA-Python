__author__ = 'gicmo'
import sys
import re


def mk_tex_text(text, is_body=False):
    if text is None:
        return u""

    text = re.sub(r'(?<!(?<!\\)\\)(&)', r"\&", text)
    text = re.sub(r'(?<!(?<!\\)\\)(#)', r"\#", text)
    text = re.sub(r'(?<!(?<!\\)\\)(%)', r"\%", text)

    if not is_body:
        text = re.sub(r'(?<!(?<!\\)\\)(_)', r"\_", text)

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

\documentclass[a4paper,10pt,oneside]{book}

\usepackage{ucs}
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

\usepackage[english]{babel}

\usepackage{mathtools}
\usepackage{amssymb}

%%\usepackage{chapterthumb}

% if figures is not None:
\usepackage{caption}
\usepackage{graphicx}
\graphicspath{ {${figures}/} }
%endif

\usepackage[top=20mm, bottom=20mm, left=20mm, right=20mm]{geometry}
\setcounter{secnumdepth}{-1}

\usepackage{xcolor}
\usepackage[breaklinks=true,colorlinks=true,citecolor=blue!30!black,urlcolor=blue!30!black,linkcolor=blue!30!black]{hyperref}

\usepackage{multind}
\makeindex{pages}
\makeindex{posterid}

\newenvironment{abstractblock}{\newpage\noindent\begin{minipage}[t]{1.\textwidth}}{\end{minipage}\vskip \glueexpr\smallskipamount + 0pt plus 10ex minus 3ex\relax
    \pagebreak[3]}
\newenvironment{authors}{}{}
\newenvironment{affiliations}{\footnotesize\itshape\begin{enumerate}}{\end{enumerate}}
\newenvironment{abstracttext}{}{}
\newenvironment{acknowledgements}{\small}{}
\newenvironment{references}{\footnotesize\begin{list}{}{\leftmargin=1.5em \listparindent=0pt \rightmargin=0pt \topsep=0.5ex \parskip=0pt \partopsep=0pt \itemsep=0pt \parsep=0pt}
}{\end{list}}

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
    \section{${new_section}}
    %endif

    ${mk_abstract(idx, abstract, figures is not None, show_meta)}
    %if single_page:
    \clearpage
    %endif
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

<%def name="mk_abstract(idx, abstract, include_figures, print_meta)">
\begin{abstractblock}
\subsection[${abstract.poster_id}]{${mk_tex_text(abstract.title)}}
${mk_authors(abstract.authors)}
${mk_affiliations(abstract.affiliations)}
%if abstract.doi:
doi: \href{http://dx.doi.org/${abstract.doi}}{${abstract.doi}}
%endif

\begin{abstracttext}
${abstract.text}
\end{abstracttext}
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
%if print_meta:
\small
Topic: ${abstract.topic}
%if abstract.is_talk:
Talk: ${mk_tex_text(abstract.reason_for_talk)}\\*[-0.5ex]
%endif
\normalsize
%endif
\end{abstractblock}
</%def>

<%def name="mk_authors(authors)">
\begin{authors}
% for idx, author in enumerate(authors):
  <%
     sep = ', ' if idx+1 < len(authors) else ''
     aff = author.format_affiliation()
     epi = '$^{%s}$' % aff if aff else ''
  %> ${author.format_name()}${epi}${sep}\index{pages}{${author.index_name}}
% endfor
\end{authors}
</%def>

<%def name="mk_affiliations(affiliations)">
\begin{affiliations}
% for idx, affiliation in enumerate(affiliations):
  \item[${idx+1}.] ${mk_tex_text(affiliation.format_affiliation())}
% endfor
\end{affiliations}
</%def>

<%def name="mk_acknowledgements(acknowledgements)">
\subsubsection{Acknowledgements}
\begin{acknowledgements}
${mk_tex_text(acknowledgements)}
\end{acknowledgements}
</%def>

<%def name="mk_references(references)">
\subsubsection{References}
\begin{references}
%for idx, ref in enumerate(references):
  \item[${idx+1}] ${mk_tex_text(ref.display_text)} ${mk_doi(ref)}
%endfor
\end{references}
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
