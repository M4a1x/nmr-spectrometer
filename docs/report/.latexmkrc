# Inspired by
# cagprado/latexmkrc Copyright (c) 2021 Caio Alves Garcia Prado
# alexpovel/latex-cookbook Copyright (c) 2022 Alex Povel
# fmarotta/kaobook Copyright (c) 2020 Federico Marotta 
# xu-cheng/dotfiles

use 5.20.0;
use open qw(:encoding(UTF-8) :std);
use strict;
use utf8;
use warnings;

local $/ = "\n";

# Define directories                                                   {{{1

my  $cur_dir     = getcwd();
my  $asy_dir     = 'asy';
my  $tex_dir     = '.';
my  $out_dir     = '%A.out/%A';       # not necessary when using $jobname below
my  $aux_dir     = '%A.out/%A';       # not necessary when using $jobname below

# Add tex/bst source directory, including subdirectories (special '//' syntax)
ensure_path( 'TEXINPUTS', './tex//' );
ensure_path( 'BSTINPUTS', './tex//' );

# Setup latexmk

our $jobname         = '%A.out/%A';   # trick to process tex into subdirectory
our $bibtex_use      = 1.5;           # delete .bbl if and only if .bib exists
our $do_cd           = 1;             # change into .tex source directory
our $pdf_mode        = 4;             # pdflatex|ps2pdf|dvipdf|lualatex|xelatex
our $postscript_mode = 0;             # Explicitly disable postscript output
our $dvi_mode        = 0;             # Explicitly disable dvi output
our $rc_report       = 0;             # do not print which rc files were read
our $max_repeat      = 7;             # default: 5

our $clean_ext = "%R-*.glstex %R_contourtmp*.* _minted-%R";

# Programs and options

# Change default `biber` call, help catch errors faster/clearer. See
# https://web.archive.org/web/20200526101657/https://www.semipol.de/2018/06/12/latex-best-practices.html#database-entries
our $biber = "biber --validate-datamodel %O %S";

my  $asymptote   = 'asy -vv -nosafe -f pdf';
# our $makeindex   = 'internal makeindex %B';
our $log_wrap    = $ENV{max_print_line} = 1e10;
&set_tex_cmds('-shell-escape -file-line-error -interaction=nonstopmode -synctex=1 %O %S');

# Minted support. Prevent additional unnecessary latex run due to hash change (taken from official .latexmkrc example)
our %hash_calc_ignore_pattern;
$hash_calc_ignore_pattern{'aux'} = '^\\\\gdef\\\\minted@oldcachelist\{,|^\s*default\.pygstyle,|^\s*[[:xdigit:]]+\.pygtex';

# Hooks

# at the end of processing everything, find and clean empty .out directories
END { rmdir(s|(\.[^.]*)?$|.out|r) for (our @default_files); }

# after processing a document, copy final pdf to ./
our $success_cmd = "cp %D '$cur_dir'";

# after finish parsing command line, prepare .out directories
push @ARGV, qw(-e prepare);
sub prepare {
  our @default_files = our @command_line_file_list;

  if (-e 'thesis.tex') {
    push(@default_files, 'thesis.tex');
  }

  # find .tex and .dtx files containing '\documentclass'
  if (!@default_files) {
    while (<$tex_dir/*.{tex,dtx}>) {
      open(my $file, '<', $_);
      push(@default_files, $_) if (grep /^\\documentclass/, <$file>);
      close $file;
    }
  }

  # prepare .out directories
  if (our $cleanup_only == 0) {
    mkdir s|(\.[^.]*)?$|.out|r for (@default_files);
  }

  if (our $cleanup_mode > 0) {
    # clean minted directory
    use File::Path qw(rmtree);
    rmtree s|([^/]*?)(\.[^.]*)?$|$1.out/$1.minted|r for (@default_files);

    if ($cleanup_mode == 1) {
      # cleanup final pdf from ./ when full cleaning
      unlink_or_move(basename s|(\.[^.]*)?$|.pdf|r) for (@default_files);
    }
  }
}

our @generated_exts;
our $cleanup_includes_generated = 1;

# KOMAScript generated files
push @generated_exts, 'loe', 'lol', 'lor', 'run.xml';

# Custom dependencies

# # Compile the glossary and acronyms list (package 'glossaries')
# add_cus_dep( 'acn', 'acr', 0, 'makeglossaries' );
# add_cus_dep( 'glo', 'gls', 0, 'makeglossaries' );
# $clean_ext .= " acr acn alg glo gls glg";
# sub makeglossaries {
#    my ($base_name, $path) = fileparse( $_[0] );
#    pushd $path;
#    my $return = system "makeglossaries", $base_name;
#    popd;
#    return $return;
# }

# # Compile the nomenclature (package 'nomencl')
# add_cus_dep( 'nlo', 'nls', 0, 'makenlo2nls' );
# sub makenlo2nls {
#     system( "makeindex -s nomencl.ist -o \"$_[0].nls\" \"$_[0].nlo\"" );
# }


# #  - glossary (history) for .dtx documentation files
# push @generated_exts, qw(gls glo);
# add_cus_dep('glo', 'gls', 0, 'makeindex');

# #  - class/package files from .dtx
# add_cus_dep('dtx', 'cls', 0, 'dtx2all');
# add_cus_dep('dtx', 'sty', 0, 'dtx2all');
# sub dtx2all {                                                           #{{{2
#   rdb_add_generated("$_[0].cls", "$_[0].sty");
#   my $rval = Run_subst('tex %S');
#   unlink("$_[0].log");
#   return $rval;
# }                                                                       #}}}2

# #  - asymptote plots
# ensure_path('TEXINPUTS', "$cur_dir/$asy_dir");
# add_cus_dep('asy', 'pdf', 0, 'asy2all');
# add_cus_dep('asy', 'tex', 0, 'asy2all');
# sub asy2all {                                                           #{{{2
#   # parse asymptote output by forking Perl so we avoid writing a new file
#   if (my $pid = open(my $dump, '-|') // die "Can't fork: $!") {
#     # modification from latexmk project's example folder
#     # parse output
#     my %dep;
#     while (<$dump>) {
#       /^(Including|Loading) .* from (.*)\s*$/
#         and $dep{$2 =~ s|^([^/].*)$|$cur_dir/$asy_dir/$1|r} = 1;
#       warn $_;
#     }
#     close $dump;
#     my $rval = $?;

#     # save dependency information and cleanup
#     my $dirname  = dirname($_[0]);
#     my $basename = basename($_[0]);
#     for (<$dirname/$basename*>) {
#       /[.]asy$/ and next;
#       /[.](pdf|tex)$/
#         ? rdb_add_generated($_)
#         : unlink($_);
#     }
#     rdb_set_source(our $rule, keys %dep);
#     return $rval;
#   }
#   open(STDERR, '>&', STDOUT);

#   # run asymptote
#   my  $dir = "'$cur_dir/$asy_dir'";
#   my  $inline = ${our $Pdest} =~ /\.tex$/ ? '-inlinetex' : '';
#   our $pdf_method;
#   Run_subst("$asymptote $inline -tex $pdf_method -cd '$dir' %S") && die;
#   exit;
# }                                                                       #}}}2

# #  - bib2gls glossary, taken from official bib2glx latexmkrc example
# push @generated_exts, 'glg', 'glstex';
# add_cus_dep('aux', 'glstex', 0, 'bib2gls');
# sub bib2gls {                                                           #{{{2
#   my $ret;
#   if ( our $silent ) {
#     $ret = system "bib2gls --silent --group '$_[0]'";
#   } else {
#     $ret = system "bib2gls --group '$_[0]'";
#   };

#   my ($base, $path) = fileparse( $_[0] );
#   if ($path && -e "$base.glstex") {
#     rename "$base.glstex", "$path$base.glstex";
#   }

#   # Analyze log file.
#   local *LOG;
#   my $LOG = "$_[0].glg";
#   if (!$ret && -e $LOG) {
#     open LOG, "<$LOG";
#   while (<LOG>) {
#     if (/^Reading (.*\.bib)\s$/) {
#     rdb_ensure_file( our $rule, $1 );
#   }
# }
# close LOG;
# }
# return $ret;  
# }


# # Overwrite `unlink_or_move` to support clean directory.
# use File::Path 'rmtree';
# sub unlink_or_move {
#   if ( our $del_dir eq '' ) {
#     foreach (@_) {
#       if (-d $_) {
#         rmtree $_;
#       } else {
#         unlink $_;
#       }
#     }
#   }
#   else {
#     foreach (@_) {
#       if (-e $_ && ! rename $_, "$del_dir/$_" ) {
#         our $My_name;
#         warn "$My_name:Cannot move '$_' to '$del_dir/$_'\n";
#       }
#     }
#   }
# }                                                                       #}}}2

# Show used CPU time
our $show_time = 1;

# Make warnings to errors. Potentially annoying for debugging.
our $warnings_as_errors = 0;

# vim: ft=perl
