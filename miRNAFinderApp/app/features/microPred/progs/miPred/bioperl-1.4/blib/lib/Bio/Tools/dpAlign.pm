## $Id: dpAlign.pm,v 1.2 2003/06/10 18:18:05 jason Exp $

# BioPerl module for Bio::Tools::dpAlign
#
# Cared for by Yee Man Chan <ymc@yahoo.com>
#
# Copyright Yee Man Chan
#
# You may distribute this module under the same terms as perl itself

# POD documentation - main docs before the code

=head1 NAME

Bio::Tools::dpAlign - Perl extension to do pairwise dynamic programming sequence alignment

=head1 SYNOPSIS

        use Bio::Tools::dpAlign;
        use Bio::SeqIO;
        use Bio::SimpleAlign;
        use Bio::AlignIO;

        $seq1 = new Bio::SeqIO(-file => $ARGV[0], -format => 'fasta');
        $seq2 = new Bio::SeqIO(-file => $ARGV[1], -format => 'fasta');

        # create a dpAlign object
        $factory = new dpAlign(-match => 3,
                           -mismatch => -1,
                           -gap => 3,
                           -ext => 1,
                           -alg => Bio::Tools::dpAlign::DPALIGN_LOCAL_MILLER_MYERS);

        # actually do the alignment
        $out = $factory->pairwise_alignment($seq1->next_seq, $seq2->next_seq);
        $alnout = new Bio::AlignIO(-format => 'pfam', -fh => \*STDOUT);
        $alnout->write_aln($out);

        # To do protein alignment, set the sequence type to protein
        # currently all protein alignments are using BLOSUM62 matrix
        # the gap opening cost is 10 and gap extension is 2. These
        # values are from ssearch. They won't be changed even though
        # you set other values for now. Also DPALIGN_LOCAL_GREEN is not
        # supported for protein in this version.
        $seq1->alphabet('protein');
        $seq2->alphabet('protein');
        $out = $factory->pairwise_alignment($seq1->next_seq, $seq2->next_seq);
        $alnout->write_aln($out);

	# use the factory to make some output

	$factory->align_and_show($seq1, $seq2, STDOUT);

=head1 DESCRIPTION

        Dynamic Programming approach is considered to be the most
        sensitive way to align two biological sequences. There are
        currently three major types of dynamic programming algorithms:
        Global Alignment, Local Alignment and Ends-free Alignment.

        Global Alignment compares two sequences in their entirety.
        By inserting gaps in the two sequences, it aligns two
        sequences to minimize the edit distance as defined by the
        gap cost function and the substitution matrix. Global Alignment
        is generally applied to two sequences that are very similar
        in length and content.

        Local Alignment instead attempts to find out the subsequences
        that has the minimal edit distance among all possible subsequences.
        It is good for sequences that has a stretch of subsequences
        that are similar to each other.

        Ends-free Alignment is a special case of Global Alignment. There
        are no gap penalty imposed for the gaps that extended from
        the end points of two sequences. Therefore it will be a good
        application when you think one sequence is contained by the
        other or when you think two sequences overlap each other.

        Dynamic Programming was first introduced by Needleman-Wunsch (1970)
        to globally align two sequences. The idea of local alignment
        was later introduced by Smith-Waterman (1981). Gotoh (1982)
        improved both algorithms by introducing auxillary arrays that
        reduced the time complexity of the algorithms to O(m*n).
        Miller-Myers (1988) exploits the divide-and-conquer idea
        introduced by Hirschberg (1975) to solve the affine gap cost
        dynamic programming using only linear space. At the time of
        this writing, it is accepted that Miller-Myers is the fastest
        single CPU implementation and using the least memory that is
        truly equivalent to original algorithm introduced by
        Needleman-Wunsch. According to Aaron Mackey, Phil Green's SWAT
        implemention introduced a heuristic that does not consider
        paths throught the matrix where the score would be less than
        the gap opening penalty, yielding a 1.5-2X speedup on most
        comparisons. to skip the calculation of some cells. However,
        his approach is only good for calculating the minimum edit
        distance and find out the corresponding subsequences (aka
        search phase). Bill Pearson's popular dynamic programming
        alignment program SSEARCH uses Phil Green's algorithm to
        find the subsequences and then Miller-Myers's algorithm to
        find the actual alignment. (aka alignment phase)

        The current implementation supports local alignment of
        either DNA sequences or protein sequences. It allows you
        to specify either the Phil Green (DPALIGN_LOCAL_GREEN)
        or Miller-Myers (DPALIGN_LOCAL_MILLER_MYERS). For DNA
        alignment, you can specify the scores for match, mismatch,
        gap opening cost and gap extension cost. For protein
        alignment, it is using BLOSUM62 by default. Currently the
        substitution matrix is not configurable.

=head1 DEPENDENCIES

	This package comes with the main bioperl distribution. You
	also need to install the lastest bioperl-ext package which
	contains the XS code that implements the algorithms. This 
	package won't work if you haven't compiled the bioperl-ext
	package.

=head1 TO-DO

        1) Allow custom substitution matrix.

        2) Support Global Alignment.

        3) Support Ends-free Alignment.

        4) Include a score only calculation based on Phil Green's
	algorithm. The code will be borrowed from do_work in
	ssearch.

        5) Support IUPAC code for DNA sequence

=head1 FEEDBACK

=head2 Mailing Lists

User feedback is an integral part of the evolution of this and other
Bioperl modules.  Send your comments and suggestions preferably to one
of the Bioperl mailing lists.  Your participation is much appreciated.

    bioperl-l@bioperl.org              - General discussion
    http://bioperl.org/MailList.shtml  - About the mailing lists

=head2 Reporting Bugs

Report bugs to the Bioperl bug tracking system to help us keep track
the bugs and their resolution. Bug reports can be submitted via email
or the web:

    bioperl-bugs@bio.perl.org
    http://bugzilla.bioperl.org/

=head1 AUTHOR

        This implementation was written by Yee Man Chan (ymc@yahoo.com).
        Copyright (c) 2003 Yee Man Chan. All rights reserved. This program
        is free software; you can redistribute it and/or modify it under
        the same terms as Perl itself. Special thanks to Aaron Mackey
        and WIlliam Pearson for the helpful discussions. [The portion
        of code inside pgreen subdirectory was borrowed from ssearch. It
        should be distributed in the same terms as ssearch.]

=cut

package Bio::Tools::dpAlign;

use Bio::Tools::AlignFactory;
use Bio::SimpleAlign;

@ISA = qw(Bio::Tools::AlignFactory);

$VERSION = '0.50';

# Gotoh algorithm as defined in J. Mol. Biol. (1982) 162, 705-708
# use constant DSW_GOTOH => 1;
# Hirschberg's algorithm as defined in Myers & Miller in 
# CABIOS, Vol 4, No. 1, 1988, p 11-17
# This algorithm is used in both the search phase and the
# alignment phase.
use constant DPALIGN_LOCAL_MILLER_MYERS => 1;
# my toy algorithm that tries to do SW as fast as possible
# use constant DSW_FSW => 3; 
# Phil Green's approximation to Smith-Waterman. It avoid calculations
# that might result in a score less than the opening gap penalty.
# This is the algorithm used by ssearch. Phil Green's algorithm is
# used in the search phase while Miller-Myers algorithm is used in
# the alignment phase
use constant DPALIGN_LOCAL_GREEN => 2; 

BEGIN {
    eval {
        require Bio::Ext::Align;
    };
    if ( $@ ) {
        die("\nThe C-compiled engine for Smith Waterman alignments (Align) has not been installed.\n Please read the install the bioperl-ext package\n\n");
        exit(1);
    }
}

sub new {
    my ($class, @args) = @_;

    my $self = $class->SUPER::new(@args);

    my ($match, $mismatch, $gap, $ext, $alg) = $self->_rearrange([qw(MATCH
							       MISMATCH
							       GAP
							       EXT
							       ALG	
							)], @args);

    $self->match(3) unless defined $match;
    $self->mismatch(-1) unless defined $mismatch;
    $self->gap(3) unless defined $gap;
    $self->ext(1) unless defined $ext;
    $self->alg(DPALIGN_LOCAL_MILLER_MYERS) unless defined $alg;

    if (defined $match) {
	if ($match =~ /^\d+$/) {
	    $self->match($match);
	}
	else {
	    $self->throw("Match score must be a number, not [$match]");
	}
    }

    if (defined $mismatch) {
	if ($match =~ /^\d+$/) {
	    $self->mismatch($mismatch);
	}
	else {
	    $self->throw("Mismatch penalty must be a number, not [$mismatch]");
	}
    }

    if (defined $gap) {
	if ($gap =~ /^\d+$/) {
	    $self->gap($gap);
	}
	else {
	    $self->throw("Gap penalty must be a number, not [$gap]");
	}
    }

    if (defined $ext) {
	if ($ext =~ /^\d+$/) {
	    $self->ext($ext);
	}
	else {
	    $self->throw("Extension penalty must be a number, not [$ext]");
	}
    }

    if (defined $alg) {
	if ($alg == DPALIGN_LOCAL_MILLER_MYERS or $alg == DPALIGN_LOCAL_GREEN) {
	    $self->alg($alg);
	}
	else {
	    $self->throw("Algorithm must be either 1 or 2");
	}
    }
    return $self;
}

=head2 pairwise_alignment

 Title   : pairwise_alignment
 Usage   : $aln = $factory->pairwise_alignment($seq1,$seq2)
 Function: Makes a SimpleAlign object from two sequences
 Returns : A SimpleAlign object
 Args    :


=cut

sub pairwise_alignment {
    my ($self, $seq1, $seq2) = @_;
    my ($aln, $out);

    if( ! defined $seq1 || ! $seq1->isa('Bio::PrimarySeqI') ||
        ! defined $seq2 || ! $seq2->isa('Bio::PrimarySeqI') ) {
        $self->warn("Cannot call pairwise_alignment without specifing 2 sequences (Bio::PrimarySeqI objects)");
        return undef;
    }
    # fix Jitterbug #1044
    if( $seq1->length() < 2 ||
        $seq2->length() < 2 ) {
        $self->warn("cannot align sequences with length less than 2");
        return undef;
    }
    $self->set_memory_and_report();
    # create engine objects
    $seq1->display_id('seq1') unless ( defined $seq1->id() );
    $seq2->display_id('seq2') unless ( defined $seq2->id() );

    if ($seq1->alphabet eq 'dna' and $seq2->alphabet eq 'dna') {
	$aln = Bio::Ext::Align::Align_DNA_Sequences($seq1->seq, $seq2->seq, $self->{'match'}, $self->{'mismatch'}, $self->{'gap'}, $self->{'ext'}, $self->{'alg'});
    }
    elsif ($seq1->alphabet eq 'protein' and $seq2->alphabet eq 'protein') {
	$aln = Bio::Ext::Align::Align_Protein_Sequences($seq1->seq, $seq2->seq, 'blosum62');
    }
    else {
	croak("There is currently no support for the types of sequences you want to align!\n");
    }

    $out = Bio::SimpleAlign->new();

    $out->add_seq(Bio::LocatableSeq->new(-seq => $aln->aln1,
					 -start => $aln->start1,
					 -end => $aln->end1,
					 -id => $seq1->id));
    
    $out->add_seq(Bio::LocatableSeq->new(-seq => $aln->aln2,
					 -start => $aln->start2,
					 -end => $aln->end2,
					 -id => $seq2->id));

    return $out;
}

=head2 align_and_show

 Title   : align_and_show
 Usage   : $factory->align_and_show($seq1,$seq2,STDOUT)

=cut

sub align_and_show {
    my ($self, $seq1, $seq2, $fh) = @_;
    my ($aln, $out);

    if (! defined $fh) {
	$fh = \*STDOUT;
    }
    if( ! defined $seq1 || ! $seq1->isa('Bio::PrimarySeqI') ||
        ! defined $seq2 || ! $seq2->isa('Bio::PrimarySeqI') ) {
        $self->warn("Cannot call pairwise_alignment without specifing 2 sequences (Bio::PrimarySeqI objects)");
        return undef;
    }
    # fix Jitterbug #1044
    if( $seq1->length() < 2 ||
        $seq2->length() < 2 ) {
        $self->warn("cannot align sequences with length less than 2");
        return undef;
    }
    $self->set_memory_and_report();
    # create engine objects
    $seq1->display_id('seq1') unless ( defined $seq1->id() );
    $seq2->display_id('seq2') unless ( defined $seq2->id() );

    if ($seq1->alphabet eq 'dna' and $seq2->alphabet eq 'dna') {
	$aln = Bio::Ext::Align::Align_DNA_Sequences($seq1->seq, $seq2->seq, $self->{'match'}, $self->{'mismatch'}, $self->{'gap'}, $self->{'ext'}, $self->{'alg'});
    }
    elsif ($seq1->alphabet eq 'protein' and $seq2->alphabet eq 'protein') {
	$aln = Bio::Ext::Align::Align_Protein_Sequences($seq1->seq, $seq2->seq, 'blosum62');
    }
    else {
	croak("There is currently no support for the types of sequences you want to align!\n");
    }

    $out = Bio::SimpleAlign->new();

    $out->add_seq(Bio::LocatableSeq->new(-seq => $aln->aln1,
					 -start => $aln->start1,
					 -end => $aln->end1,
					 -id => $seq1->id));
    
    $out->add_seq(Bio::LocatableSeq->new(-seq => $aln->aln2,
					 -start => $aln->start2,
					 -end => $aln->end2,
					 -id => $seq2->id));

    my $t1 = &Bio::Ext::Align::new_Sequence_from_strings($seq1->id, $seq1->seq);
    my $t2 = &Bio::Ext::Align::new_Sequence_from_strings($seq2->id, $seq2->seq);

    &Bio::Ext::Align::write_pretty_seq_align($out,$t1,$t2,12,50,$fh);
}

=head2 match

 Title     : match 
 Usage     : $match = $factory->match() #get
           : $factory->match($value) #set
 Function  : the set get for the match score
 Example   :
 Returns   : match value
 Arguments : new value

=cut

sub match {
    my ($self,$val) = @_;


    if( defined $val ) {
        if( $val < 0 ) {    # Fixed so that match==0 is allowed /AE
            $self->throw("Can't have a match score less than 0");
        }
        $self->{'match'} = $val;
    }
    return $self->{'match'};
}

=head2 mismatch

 Title     : mismatch 
 Usage     : $mismatch = $factory->mismatch() #get
           : $factory->mismatch($value) #set
 Function  : the set get for the mismatch penalty
 Example   :
 Returns   : mismatch value
 Arguments : new value

=cut

sub mismatch {
    my ($self,$val) = @_;


    if( defined $val ) {
        if( $val > 0 ) {    # Fixed so that mismatch==0 is allowed /AE
            $self->throw("Can't have a mismatch penalty greater than 0");
        }
        $self->{'mismatch'} = $val;
    }
    return $self->{'mismatch'};
}


=head2 gap

 Title     : gap
 Usage     : $gap = $factory->gap() #get
           : $factory->gap($value) #set
 Function  : the set get for the gap penalty
 Example   :
 Returns   : gap value
 Arguments : new value

=cut

sub gap {
    my ($self,$val) = @_;


    if( defined $val ) {
        if( $val < 0 ) {    # Fixed so that gap==0 is allowed /AE
            $self->throw("Can't have a gap penalty less than 0");
        }
        $self->{'gap'} = $val;
    }
    return $self->{'gap'};
}

=head2 ext

 Title     : ext
 Usage     : $ext = $factory->ext() #get
           : $factory->ext($value) #set
 Function  : the set get for the ext penalty
 Example   :
 Returns   : ext value
 Arguments : new value

=cut

sub ext {
    my ($self,$val) = @_;

    if( defined $val ) {
        if( $val < 0 ) {    # Fixed so that ext==0 is allowed /AE
            $self->throw("Can't have a extension penalty less than 0");
        }
        $self->{'ext'} = $val;
    }
    return $self->{'ext'};
}

=head2 alg

 Title     : alg
 Usage     : $alg = $factory->alg() #get
           : $factory->alg($value) #set
 Function  : the set get for the algorithm
 Example   :
 Returns   : alg value
 Arguments : new value

=cut

sub alg {
    my ($self,$val) = @_;

    if( defined $val ) {
        if( $val != DPALIGN_LOCAL_MILLER_MYERS and $val != DPALIGN_LOCAL_GREEN) {    
            $self->throw("Can't have an algorithm that is not 1 or 2");
        }
        $self->{'alg'} = $val;
    }
    return $self->{'alg'};
}

1;
