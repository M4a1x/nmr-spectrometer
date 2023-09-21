# Imports for Perl
use 5.20.0;
use open qw(:encoding(UTF-8) :std);
use strict;
use utf8;
use warnings;

local $/ = "\n";

# Add tex/bst source directory, including subdirectories (special '//' syntax)
ensure_path( 'TEXINPUTS', './tex//' );
ensure_path( 'BSTINPUTS', './tex//' );

# Configure latexmk

our $biber = "biber --validate-datamodel %O %S";
our $out_dir            = 'out';         # Set output directory to reduce clutter
our @default_files      = ('thesis.tex');# Compile only thesis.tex
our $show_time          = 1;             # Show used CPU time
our $bibtex_use         = 1.5;           # delete .bbl if and only if .bib exists
our $do_cd              = 1;             # change into .tex source directory
our $pdf_mode           = 4;             # pdflatex|ps2pdf|dvipdf|lualatex|xelatex
our $postscript_mode    = 0;             # Explicitly disable postscript output
our $dvi_mode           = 0;             # Explicitly disable dvi output
our $rc_report          = 0;             # do not print which rc files were read
our $max_repeat         = 10;            # default: 5
our $warnings_as_errors = 0;             # set to 1 for debugging
our $cleanup_includes_generated = 1;     # cleanup generated files as well
our $clean_ext .= " acr acn alg glo gls glg %R-*.glstex %R_contourtmp*.* _minted-%R %R.ist %R.xdy";
&set_tex_cmds('-shell-escape -file-line-error -interaction=nonstopmode -synctex=1 %O %S');

# Update generated files
our @generated_exts;
push @generated_exts, 'loe', 'lol', 'lor', 'run.xml';  # KOMAScript
push @generated_exts, 'glo', 'gls', 'glg';             # makeglossaries
push @generated_exts, 'acn', 'acr', 'alg';             # makeglossaries
push @generated_exts, 'nlo', 'nls', 'ist';             # makenlo2nls

# External Custom Dependencies

# Compile the glossary and acronyms list (package 'glossaries')
add_cus_dep( 'acn', 'acr', 0, 'makeglossaries' );
add_cus_dep( 'glo', 'gls', 0, 'makeglossaries' );
sub makeglossaries {
   my ($base_name, $path) = fileparse( $_[0] );
   return system "makeglossaries -d '$path' '$base_name'"
}

# Compile the nomenclature (package 'nomencl')
add_cus_dep( 'nlo', 'nls', 0, 'makenlo2nls' );
sub makenlo2nls {
    system( "makeindex -s nomencl.ist -o \"$_[0].nls\" \"$_[0].nlo\"" );
}