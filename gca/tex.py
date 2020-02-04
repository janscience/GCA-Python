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
\newunicodechar{³}{^3}
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

%% language:
\usepackage[english]{babel}

%%\usepackage{chapterthumb}

%% graphics and figures:
\usepackage{xcolor}

%% UT primary colors:
\definecolor{red}{RGB}{165,30,55}
\definecolor{gray}{RGB}{50,65,75}
\definecolor{gold}{RGB}{180,160,105}

%% UT secondary colors:
\definecolor{darkblue}{RGB}{65,90,140}
\definecolor{blue}{RGB}{0,105,170}
\definecolor{lightblue}{RGB}{80,170,200}
\definecolor{turquoise}{RGB}{130,185,160}
\definecolor{lightgreen}{RGB}{125,165,75}
\definecolor{green}{RGB}{50,110,30}
\definecolor{lightred}{RGB}{200,80,60}
\definecolor{purple}{RGB}{175,110,150}
\definecolor{lightpurple}{RGB}{180,160,150}
\definecolor{lightbrown}{RGB}{215,180,105}
\definecolor{orange}{RGB}{210,150,0}
\definecolor{brown}{RGB}{145,105,70}

% if figures is not None:
\usepackage{graphicx}
\graphicspath{ {${figures}/} }
\usepackage[format=plain,singlelinecheck=off,labelfont=bf,font={small,sf}]{caption}
%endif

%% layout:
\usepackage[top=20mm, bottom=20mm, left=23mm, right=23mm, headsep=9mm, marginparsep=5mm]{geometry}

\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\setlength{\fboxsep}{0pt}
\setlength{\unitlength}{1mm}
\newcommand{\headertext}{Poster}
\newcommand{\headercolor}{green}
\fancyhead[RO]{\begin{picture}(0,0)\put(0,3){\colorbox{\headercolor}{\makebox[23mm][c]{\sffamily\Large \rule[-1.5ex]{0pt}{5ex}\textcolor{white}{\headertext}}}}\end{picture}}
\fancyhead[LE]{\begin{picture}(0,0)\put(-23,3){\colorbox{\headercolor}{\makebox[23mm][c]{\sffamily\Large \rule[-1.5ex]{0pt}{5ex}\textcolor{white}{\headertext}}}}\end{picture}}
\fancyhead[LO,RE]{15. Annual Meeting of the Ethological Society, T\"ubingen, 2020}
\fancyfoot[LE,RO]{\thepage}
\renewcommand{\headrulewidth}{0pt}

\usepackage{marginnote}

\usepackage[sf,bf]{titlesec}
\setcounter{secnumdepth}{1}
\titleformat{\section}{\sffamily\Large\bfseries}{}{0em}{\marginnote{\huge P\arabic{section}}[-2.4ex]}

\usepackage{imakeidx}
\makeindex[name=authors, title={Author index}]

\usepackage[breaklinks=true,colorlinks=true,citecolor=blue!30!black,urlcolor=blue!30!black,linkcolor=blue!30!black]{hyperref}

%% environment for formatting the whole abstract:
\newenvironment{abstractblock}{}{}
%if single_page:
\newcommand{\newabstract}{\clearpage}
%else:
\newcommand{\newabstract}{}
%endif
\newcommand{\newabstract}{}
\newcommand{\abstractsection}[3][]{\section[#2]{#3}}

%% environment for formatting the authors block:
\newenvironment{authors}{\begin{flushleft}\setstretch{1.2}\sffamily}{\end{flushleft}\vspace{-3ex}}
\newcommand{\authorname}[1]{\mbox{#1}}
\newcommand{\firstname}[1]{#1}
\newcommand{\lastname}[1]{\textbf{#1}}

%% environment for formatting the affiliations:
\newenvironment{affiliations}{\begin{flushleft}\begin{enumerate}\setlength{\itemsep}{-0.5ex}\footnotesize\sffamily}{\end{enumerate}\end{flushleft}}

%% environment for formatting the abstract main text:
\newenvironment{abstracttext}{\noindent\hspace*{-0.8ex}}{}

%% environment for formatting the figure block:
\newenvironment{afigure}{\begin{center}\begin{minipage}{0.9\textwidth}}{\end{minipage}\end{center}}
%% the maximum height of a figure:
\newlength{\figureheight}
\setlength{\figureheight}{0.35\textheight}

%% environment for formatting the acknowledgements block:
\newenvironment{acknowledgements}{\small}{}

%% environment for formatting the references:
\newenvironment{references}%
  {\footnotesize\begin{list}{}{\leftmargin=1.5em \listparindent=0pt \rightmargin=0pt \topsep=0.5ex \parskip=0pt \partopsep=0pt \itemsep=0pt \parsep=0pt}}%
  {\end{list}}


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
% endfor

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% appendix
%if not bare:
\renewcommand{\headertext}{Index}
\renewcommand{\headercolor}{white}
\backmatter

\printindex[authors]

\end{document}
%endif
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

<%def name="mk_abstract(idx, abstract, include_figures, print_meta)">
\begin{abstractblock}
\abstractsection[Gwinner]{${abstract.poster_id}}{${mk_tex_text(abstract.title)}}
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
