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

\documentclass[a4paper,11pt,oneside]{book}

%% customize the abstracts using the environments and commands
%% provided at the end of the header!

%% math support:
\usepackage{amsmath}    % needs to be included before the wasysym package
\usepackage{mathtools}

%% encoding and fonts:
\usepackage[LGR,T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{newunicodechar}

\usepackage{textcomp}
\usepackage{textgreek}
\usepackage{amssymb}
\usepackage{wasysym}
\usepackage[squaren]{SIunits}

\usepackage{microtype}

%% add missing definitions of unicode characters:
\newunicodechar{³}{$^3$}
\newunicodechar{µ}{\micro}
\newunicodechar{°}{\degree}
\newunicodechar{♀}{\female}
\newunicodechar{♂}{\male}
\newunicodechar{´}{'}
\newunicodechar{−}{\text{--}}

\DeclareUnicodeCharacter{8208}{-}    % HYPHEN
\DeclareUnicodeCharacter{8210}{-}    % DASH
\DeclareUnicodeCharacter{8239}{\,}   % NARROW SPACE
\DeclareUnicodeCharacter{8288}{}
%%\DeclareUnicodeCharacter{700}{'}
\DeclareUnicodeCharacter{FB00}{ff}
\DeclareUnicodeCharacter{FB01}{fi}
\DeclareUnicodeCharacter{FB02}{fl}
\DeclareUnicodeCharacter{FB03}{ffi}
\DeclareUnicodeCharacter{FB04}{ffl}
\DeclareUnicodeCharacter{FB05}{ft}
%%\usepackage{tipa}
%%\DeclareUnicodeCharacter{57404}{\textiota}

%%%%% basic layout %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% language:
\usepackage[english]{babel}

%% graphics and figures:
\usepackage{xcolor}
% if figures is not None:
\usepackage{graphicx}
\graphicspath{ {${figures}/} }
\usepackage[format=plain,singlelinecheck=off,labelfont=bf,font={small,sf}]{caption}
%endif

%% layout:
\usepackage[top=20mm, bottom=20mm, left=23mm, right=23mm]{geometry}

\usepackage{setspace}

%% customize header and footer:
%% (you may want to add the conference title, the abstract number, etc.)
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\renewcommand{\headrulewidth}{0pt}

%% customize chapter and sections appearance:
%% use commands of the titlesec package to modify the layout of the abstract's title:
\usepackage[sf,bf]{titlesec}
\titleformat{\section}{\sffamily\bfseries\Large\raggedright}{\thesection}{1em}{}

%% number the abstracts, but do not number acknowledgements and references:
\setcounter{secnumdepth}{1}
%% abstract number without chapter number:
\renewcommand{\thesection}{\arabic{section}}
%%\renewcommand{\thesection}{P\arabic{section}}  % indicate poster

%% generate author index:
\usepackage{imakeidx}
\makeindex[name=authors, title={Author index}]

%% make nice clickable links:
\usepackage[breaklinks=true,colorlinks=true,citecolor=blue!30!black,urlcolor=blue!30!black,linkcolor=blue!30!black]{hyperref}

%%%%% abstract specific layout %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Each element of the abstract (title, authors, affiliations, text, ... is encapsulated
%% in an environment or command as defined in the following.
%% Change their definition to modify the appaerance of the abstracts.

%% Environment for formatting the whole abstract:
\newenvironment{abstractblock}
  {}
  {}

%% Command for separating subsequent abstracts:
%if single_page:
\newcommand{\newabstract}{\clearpage}
%else:
\newcommand{\newabstract}{}
%endif

%% Command for setting the abstract's title. It gets four arguments:
%% 1. some optional string (user supplied by manual editing the latex file)
%% 2. poster ID
%% 3. last name of first author
%% 4. title of abstract
\newcommand{\abstracttitle}[4][]{\section[#3: #4]{#4}}
%%\newcommand{\abstracttitle}[4][]{\section[#2]{#4}}

%% Environment for formatting the authors block:
\newenvironment{authors}
  {\begin{flushleft}\setstretch{1.2}\sffamily}
  {\end{flushleft}\vspace{-3ex}}

%% Command for formatting of author names. Five arguments:
%% 1. first name
%% 2. middle name
%% 3. initial of first name
%% 4. initial of middle name
%% 5. last name
\newcommand{\authorname}[5]{\mbox{#1#2 \textbf{#5}}}  %% first and middle name plus bold last name
%% \newcommand{\authorname}[5]{\mbox{\textbf{#5}, #3#4}}  %% bold last name, first and middle initials
%% \newcommand{\authorname}[5]{\mbox{\textbf{#5}, #1#4}}  %% bold last name, full first name and middle initials

%% Environment for formatting the affiliations:
%% each affiliation is provided as an \item
\newenvironment{affiliations}
  {\begin{flushleft}\begin{enumerate}\setlength{\itemsep}{-0.5ex}\footnotesize\sffamily}
  {\end{enumerate}\end{flushleft}}

\usepackage{xstring}
%% Command for formatting each affiliation. Four arguments:
%% 1. department
%% 2. section
%% 3. address
%% 4. country
%% Each of the arguments are either empty strings or preceded by ', '.
\newcommand{\affiliation}[4]{\StrGobbleLeft{#1#2#3#4}{2}}

%% Environment for formatting the abstract's main text:
\newenvironment{abstracttext}
  {\noindent\hspace*{-0.8ex}}
  {}

%% Environment for formatting the figure block:
\newenvironment{afigure}
  {\begin{center}\begin{minipage}{0.9\textwidth}}
  {\end{minipage}\end{center}}
  
%% Maximum height of a figure:
\newlength{\figureheight}
\setlength{\figureheight}{0.35\textheight}

%% Environment for formatting the acknowledgements block:
\newenvironment{acknowledgements}
  {\subsubsection{Acknowledgements}\small}
  {}

%% Environment for formatting the references:
\newenvironment{references}
  {\subsubsection{References}\footnotesize\begin{list}{}{\leftmargin=1.5em \listparindent=0pt \rightmargin=0pt \topsep=0.5ex \parskip=0pt \partopsep=0pt \itemsep=0pt \parsep=0pt}}
  {\end{list}}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\begin{document}

\frontmatter

%%%%%%%%%%%%%
\mainmatter
%endif

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
<%
cur_state = check_cur_state(None, None)
%>

% for idx, abstract in enumerate(abstracts):
<%
    new_chapter, new_section = check_cur_state(abstract, cur_state)
%>
    %if new_chapter is not None:
    \cleardoublepage \chapter{${new_chapter}} \newpage
    %endif
    %if new_section is not None:
    \section{${new_section}}
    %endif

    ${mk_abstract(idx, abstract, figures is not None, show_meta)}
% endfor
%if not bare:
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% appendix
\backmatter

\printindex[authors]

\end{document}
%endif
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

<%def name="mk_abstract(idx, abstract, include_figures, print_meta)">
\begin{abstractblock}
\abstracttitle[]{${abstract.poster_id}}{${abstract.authors[0].last_name}}{${mk_tex_text(abstract.title)}}
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

\newabstract
</%def>

<%def name="mk_authors(authors)">
\begin{authors}
% for idx, author in enumerate(authors):
  <%
     sep = ', ' if idx+1 < len(authors) else ''
     aff = author.format_affiliation()
     epi = '$^{%s}$' % aff if aff else ''
  %> ${author.latex_format_name()}${epi}${sep}\index[authors]{${author.index_name}}
% endfor
\end{authors}
</%def>

<%def name="mk_affiliations(affiliations)">
\begin{affiliations}
% for idx, affiliation in enumerate(affiliations):
  \item[${idx+1}.] ${mk_tex_text(affiliation.latex_format_affiliation())}
% endfor
\end{affiliations}
</%def>

<%def name="mk_acknowledgements(acknowledgements)">
\begin{acknowledgements}
${mk_tex_text(acknowledgements)}
\end{acknowledgements}
</%def>

<%def name="mk_references(references)">
\begin{references}
%for idx, ref in enumerate(references):
  \item[${idx+1}] ${mk_tex_text(ref.display_text)} ${mk_doi(ref)}
%endfor
\end{references}
</%def>

<%def name="mk_figure(figure)">
\begin{afigure}
    \centerline{\includegraphics[width=1\linewidth, height=1\figureheight, keepaspectratio]{${figure.uuid}}}
    \captionof*{figure}{\small ${mk_tex_text(figure.caption)}}
\end{afigure}
</%def>

<%def name="mk_doi(ref)">
%if ref.doi:
\href{${ref.doi_link}}{${mk_tex_text(ref.doi)}}\
%endif
</%def>

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""
