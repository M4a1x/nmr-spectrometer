\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ethpresentation}[2023/04/13 ETH Zurich modern inofficial presentation class]

% This is LuaTex only. Fail early
\RequirePackage{iftex}
\RequireLuaTeX{}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Configure base class
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Default base class options
\newcommand{\@baseclass}{beamer}  % KOMA-script
\PassOptionsToClass{aspectratio=169}{\@baseclass}

% Declare own options with kvoptions
\RequirePackage{kvoptions}
\SetupKeyvalOptions{
  family=ETH,
  prefix=ETH@
} % user shorter prefix ETH
\DeclareStringOption[english]{language}  % Passed to polyglossia, e.g. english or german
\DeclareDefaultOption{%
  \ifx\CurrentOptionValue\relax
  \PackageWarningNoLine{\@currname}{
    Unknown option '\CurrentOption'\MessageBreak
    is passed to base class '\@baseclass'
  }
  % Pass through any option (overwriting defaults) and load it
  \expandafter\PassOptionsToClass{\expandafter\CurrentOption}{\@baseclass}
}
\ProcessKeyvalOptions*
\LoadClass{\@baseclass}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Colour
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Load this before unicode-math font specifications to make colors available there
\RequirePackage{xcolor}

% ETH color scheme
% https://ethz.ch/staffnet/en/service/communication/corporate-design/farbe.html

% ETH Blue
\definecolor{blue}{HTML}{215CAF}
\definecolor{blue8}{HTML}{4D7DBF}
\definecolor{blue6}{HTML}{7A9DCF}
\definecolor{blue4}{HTML}{A6BEDF}
\definecolor{blue2}{HTML}{D3DEEF}
\definecolor{blue1}{HTML}{E9EFF7}
\definecolor{blued}{HTML}{08407E}

% ETH Petrol
\definecolor{petrol}{HTML}{007894}
\definecolor{petrol8}{HTML}{3395AB}
\definecolor{petrol6}{HTML}{66AFC0}
\definecolor{petrol4}{HTML}{99CAD5}
\definecolor{petrol2}{HTML}{CCE4EA}
\definecolor{petrol1}{HTML}{E7F4F7}
\definecolor{petrold}{HTML}{00596D}

% ETH Green
\definecolor{green}{HTML}{627313}
\definecolor{green8}{HTML}{818F42}
\definecolor{green6}{HTML}{A1AB71}
\definecolor{green4}{HTML}{C0C7A1}
\definecolor{green2}{HTML}{E0E3D0}
\definecolor{green1}{HTML}{EFF1E7}
\definecolor{greend}{HTML}{365213}

% ETH Bronze
\definecolor{bronze}{HTML}{8E6713}
\definecolor{bronze8}{HTML}{A58542}
\definecolor{bronze6}{HTML}{BBA471}
\definecolor{bronze4}{HTML}{D2C2A1}
\definecolor{bronze2}{HTML}{E8E1D0}
\definecolor{bronze1}{HTML}{F4F0E7}
\definecolor{bronzed}{HTML}{956013}

% ETH Red
\definecolor{red}{HTML}{B7352D}
\definecolor{red8}{HTML}{C55D57}
\definecolor{red6}{HTML}{D48681}
\definecolor{red4}{HTML}{E2AEAB}
\definecolor{red2}{HTML}{F1D7D5}
\definecolor{red1}{HTML}{F8EBEA}
\definecolor{redd}{HTML}{96272D}

% ETH Purple
\definecolor{purple}{HTML}{A30774}
\definecolor{purple8}{HTML}{B73B92}
\definecolor{purple6}{HTML}{CA6CAE}
\definecolor{purple4}{HTML}{DC9EC9}
\definecolor{purple2}{HTML}{EFD0E3}
\definecolor{purple1}{HTML}{F8E8F3}
\definecolor{purpled}{HTML}{8C0A59}

% ETH Grey
\definecolor{grey}{HTML}{6F6F6F}
\definecolor{grey8}{HTML}{8C8C8C}
\definecolor{grey6}{HTML}{A9A9A9}
\definecolor{grey4}{HTML}{C5C5C5}
\definecolor{grey2}{HTML}{E2E2E2}
\definecolor{grey1}{HTML}{F1F1F1}
\definecolor{greyd}{HTML}{575757}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Load & Configure Metropolis Theme
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Load metropolis theme
\usetheme[titleformat title=smallcaps]{metropolis}

% Disable separate dark color for frame titles
\setbeamercolor{frametitle}{fg=normal text.fg, bg=normal text.bg}

% Change default colours to ETH colours
\setbeamercolor{normal text}{fg=greyd, bg=black!2}
\setbeamercolor{alerted text}{fg=red}
\setbeamercolor{example text}{fg=purple}

% More padding for frame titles. Align with text body.
\setlength{\metropolis@frametitle@padding}{3ex}
\setbeamersize{text margin left=3ex, text margin right=3ex}

% Reveal slides on a frame gradually, used with \pause, \uncover or \onslide
\setbeamercovered{dynamic}

% Make the appendix into backup slides
\RequirePackage{appendixnumberbeamer}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set language
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Use English
\RequirePackage{polyglossia}
\setmainlanguage{\ETH@language}
\RequirePackage[english=british,autostyle=true]{csquotes}
\RequirePackage[\ETH@language]{tracklang}  % Language Tracking, i.e. what has polyglossia been requested to use?

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Fonts
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepackage{fontspec}  % Requires LuaLaTeX
\usepackage{mathtools}  % Math
\usepackage[
  warnings-off={
      mathtools-colon,%
      mathtools-overbracket,%
    }
]{unicode-math}% Load after mathtools
\usepackage[tracking]{microtype}
\microtypesetup{protrusion=true,expansion=true}  % classicthesis

% Using 'shortcuts' package option, do e.g. 'fast\-/paced' to get a breakable
% 'fast-pace' word in print.
% Otherwise, LaTeX does not hyphenate/linebreak words that already come with a hyphen,
% since that could be ambiguous
\RequirePackage[shortcuts]{extdash}

% Font configuration
\setmainfont[Numbers=Lowercase,Scale=1.04]{TeX Gyre Pagella}
\setsansfont{Merriweather Sans}
\setmonofont[AutoFakeSlant,Scale=MatchLowercase]{inconsolata}
\setmathfont[mathrm=sym,mathit=sym,mathsf=sym,mathbf=sym,mathtt=sym,NFSSFamily=tgpl]{TeX Gyre Pagella Math}
\newfontfamily{\unitnumberfont}[Numbers=Uppercase]{TeX Gyre Pagella}  % Upright numbers for units in siunitx
% \setbeamerfont to define fonts used e.g. in heading, block , footer, ...
% \usefonttheme{serif}

% Additional packages
\RequirePackage{fontawesome5}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Typography and Misc.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{etoolbox}  	% Programming facilities
\RequirePackage{xpatch}     % Enhanced version of etoolbox
\RequirePackage{import}		  % Relative path imports
\RequirePackage{pdflscape} 	% Pages in landscape format
\RequirePackage{xspace}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Scientifics Typesetting
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{chemmacros}% \ch{}, \chcpd[]{compound} etc.
\chemsetup{%
  formula=chemformula,%
  chemformula/font-family=tgpl,% Use math font family
}

% Some new custom environments. Very simple definitions that behave just like the
% widely known AMSMath math environment as specified in the last argument.
\NewChemReaction{reactionsgather}{gather}% Like AMSmath's `gather`
\NewChemReaction{reactionsgather*}{gather*}

% Sort reaction counter underneath chapter, see
% https://tex.stackexchange.com/questions/530210/how-to-cross-reference-reactions-in-chemmacros-chapter#comment1340793_530210
\renewcommand*{\thereaction}{\thechapter.\arabic{reaction}}

\RequirePackage{siunitx}% Typesetting physical units correctly
\sisetup{%
  % For siunitx v3, the following block replaces what used to be
  % `detect-all` (removed in that release, see
  % https://github.com/josephwright/siunitx/blob/main/CHANGELOG.md#v300 ).
  % It allows the `siunitx` output to match surrounding text/math (italics/bold/...,
  % roman/sans/... etc. as much as possible)
  mode=match,
  propagate-math-font=true,
  reset-math-version=false,
  reset-text-family=false,
  reset-text-series=false,
  reset-text-shape=false,% Not part of official fix, but still added (see https://collaborating.tuhh.de/alex/latex-cookbook/-/issues/8)
  text-family-to-math=true,
  text-series-to-math=true,
  %
  % Requires siunitx v3+, see also https://tex.stackexchange.com/a/468031/120853,
  % https://github.com/josephwright/siunitx/issues/532 :
  text-font-command=\unitnumberfont,
  %
  % Alternative range-phrase:
  % en-dash via '--', but inside \text{}, so it's not 'two minus signs'
  % range-phrase={\,\text{--}\,},
  range-units=single,% single: Print unit only once, at end
  per-mode=symbol,
}%
% Second setup step, with locales. See also
% https://tex.stackexchange.com/a/46979/120853
\gappto{\blockextras@german}{%
  \sisetup{locale=DE}
}
\gappto{\blockextras@english}{%
  \sisetup{locale=US}
}

% Declare units ourselves:
% Set as text so it stays a hyphen in math mode, as opposed to minus sign
\DeclareSIUnit{\volpercent}{Vol.\text{-}\%}
\DeclareSIUnit{\watthour}{Wh}%
\DeclareSIUnit{\annum}{a}%
\DeclareSIUnit{\atmosphere}{atm}%
\DeclareSIUnit{\partspermillion}{ppm}%
\DeclareSIUnit{\bar}{bar}% https://tex.stackexchange.com/a/598473/120853

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Graphics
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{graphicx}
\graphicspath{{images/}{figures/}{pictures/}{plots/}{schematics/}{./}{data/}}  % Paths in which to look for images

\RequirePackage{svg}
% See also:
% https://tex.stackexchange.com/a/158612/120853.
% pdftexcmds package etc. no longer seems necessary.
% svg package documentation states that it is a dependency, but done automatically.
% https://tex.stackexchange.com/a/74693/120853

% Build failed on my system due to lack of the 'canberra' module,
% see for a fix: https://askubuntu.com/a/872397/978477

% Running the document to generate the PDF and PDF_TEX file from the original SVG
% will require SHELL ESCAPE (--shell-escape), aka elevation.
% However, after the auxiliary images have been created, they only need to be input;
% shell-escape will no longer be required.
\svgsetup{%
  inkscapepath=svgsubdir,% Put into subdirectory of where original SVG was found
  % In most cases, we include SVGs that contain no text, then add it in a
  % tikzpicture overlay. Therefore, don't generate *.pdf_tex file.
  % Toggle this back to true wherever needed, on a per-file basis
  inkscapelatex=false,
}


% TODO:
% Minted for code
% hyperref setup for pdf, bookmarks, etc.