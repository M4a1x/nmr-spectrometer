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

% Font setup
\usepackage{fontspec}  % Requires LuaLaTeX
\usepackage{mathtools}  % Math
\usepackage[
  warnings-off={
      mathtools-colon,%
      mathtools-overbracket,%
    }
]{unicode-math}% Load after mathtools
\usepackage[tracking]{microtype}

% Font configuration
\setmainfont[Numbers=Lowercase]{TeX Gyre Pagella}
\setmonofont[AutoFakeSlant,Scale=MatchLowercase]{inconsolata}
\setsansfont{Merriweather Sans}
\setmathfont[mathrm=sym,mathit=sym,mathsf=sym,mathbf=sym,mathtt=sym,NFSSFamily=tgpl]{TeX Gyre Pagella Math}
\newfontfamily{\unitnumberfont}[Numbers=Uppercase]{TeX Gyre Pagella}
% \setbeamerfont to define fonts used e.g. in heading, block , footer, ...
% \usefonttheme{serif}

% Additional packages
\RequirePackage{siunitx}
\RequirePackage{appendixnumberbeamer} % To make the appendix into backup slides
\RequirePackage{fontawesome5}