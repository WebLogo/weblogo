#!/usr/bin/env python

#  Copyright (c) 2005 Gavin E. Crooks <gec@threeplusone.com>
#
#  This software is distributed under the MIT Open Source License.
#  <http://www.opensource.org/licenses/mit-license.html>
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#

import unittest

import pytest

from weblogo import seq_io
from weblogo.seq import (
    Alphabet,
    Seq,
    SeqList,
    dna,
    dna_alphabet,
    generic_alphabet,
    nucleic_alphabet,
    protein,
    protein_alphabet,
    rna,
    unambiguous_dna_alphabet,
    unambiguous_protein_alphabet,
)

from . import data_ref


class test_alphabet(unittest.TestCase):
    def test_create_alphabet(self) -> None:
        # Alphabet contains repeated character
        self.assertRaises(ValueError, Alphabet, "alphabet")

        # Alphabet contains null character
        self.assertRaises(ValueError, Alphabet, "alph\x00")

        Alphabet("alphbet")

    def test_alphabet_alphabetic(self) -> None:
        a = Alphabet("alphbet")
        self.assertTrue(a.alphabetic("alphbet"))
        self.assertTrue(not a.alphabetic("alphbetX"))

    def test_alphabet_ord(self) -> None:
        a = generic_alphabet
        for i, c in enumerate(a):
            self.assertEqual(a.ord(c), i)

        a = Alphabet("alph")
        self.assertEqual(2, a.ord("p"))

    def test_alphabet_chr(self) -> None:
        a = generic_alphabet
        for i, c in enumerate(a):
            self.assertEqual(ord(a.chr(i)), i + 32)

        a = Alphabet("alph")
        self.assertEqual("h", a.chr(3))

    def test_alphabet_ords(self) -> None:
        a = Alphabet("alph")
        self.assertEqual(0, a.ords("alphalph")[4])

        a = generic_alphabet
        o = a.ords(str(a))
        for i, c in enumerate(o):
            self.assertEqual(c, i)

    def test_alphabet_chrs(self) -> None:
        a = Alphabet("alph")
        self.assertEqual(Seq("ppla", a), a.chrs((2, 2, 1, 0)))

    def test_none(self) -> None:
        a1 = Alphabet(None)
        self.assertEqual(a1, generic_alphabet)

    def test_create_from_alphabet(self) -> None:
        """If we pass an alphabet to the constuctor, it's passed
        right back"""
        a1 = Alphabet("kjdahf")
        a2 = Alphabet(str(a1))
        self.assertTrue(a1 == a2)

        self.assertFalse(a1 == "not an alphabet")

    def test_repr(self) -> None:
        a = Alphabet("kjdahf")
        repr(a)
        str(a)

    def test_str(self) -> None:
        self.assertEqual(str(Alphabet("kjdahf")), "kjdahf")

    def test_letters(self) -> None:
        self.assertEqual(Alphabet("kjdahf").letters(), "kjdahf")

    def test_normalize(self) -> None:
        a = Alphabet("ABCDE")
        s = "aBbc"
        n = a.normalize(s)
        self.assertEqual(str(n), "ABBC")

        self.assertRaises(ValueError, a.normalize, "aslkfdnnr33")

    def test_alt(self) -> None:
        alt = tuple(zip("12345", "ABCED"))
        alpha = Alphabet("ABCDE", alt)
        assert alpha.ord("A") == 0
        for a, c in alt:
            assert alpha.ord(a) == alpha.ord(c)

    def test_which_alphabet(self) -> None:
        a = Alphabet.which(Seq("ARNDCQEGHILKMFPSTWYVX"))
        assert a == unambiguous_protein_alphabet

        # FIXME: sloppy use of file references
        f1 = data_ref("cap.fa").open()
        f2 = data_ref("cox2.msf").open()
        f3 = data_ref("Rv3829c.fasta").open()
        f4 = data_ref("chain_B.fasta").open()

        tests = (
            (seq_io.read(f1), unambiguous_dna_alphabet),
            (seq_io.read(f2), unambiguous_protein_alphabet),
            (seq_io.read(f3), unambiguous_protein_alphabet),
            (seq_io.read(f4), unambiguous_protein_alphabet),
        )
        for t in tests:
            self.assertEqual(Alphabet.which(t[0]), t[1])

        f1.close()
        f2.close()
        f3.close()
        f4.close()


class test_seq(unittest.TestCase):
    def test_create_seq(self) -> None:
        self.assertTrue(Seq("alphabet", Alphabet("alphbet")))
        self.assertRaises(ValueError, Seq, "not alphabetic", "alphabet")

        a = (
            "Any printable Ascii character `1234567890-=~!@#$%^&*()_+{}|[]\\:;'<>?,./QWERTYUIOPASD"
            "FGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm "
        )

        for x in a:
            self.assertTrue(x in generic_alphabet)
        self.assertTrue(Seq(a, generic_alphabet))
        self.assertRaises(ValueError, Seq, "Not zero. \x00", generic_alphabet)

    def test_std_alphabets(self) -> None:
        s = Seq("dskjjfskdjbfKJJSJKSKJDjk123u768erbm", generic_alphabet)
        s = Seq("ARNDCQEGHILKMFPSTWYVX", protein_alphabet)
        self.assertRaises(ValueError, Seq, "1234", protein_alphabet)
        s = Seq("AGTCAGCTACGACGCGC", dna_alphabet)
        self.assertEqual(str(s[1]), "G")

    def test_ords(self) -> None:
        a = Alphabet("ABC")
        s = Seq("ABCCBA", a)
        self.assertEqual(list(s.ords()), [0, 1, 2, 2, 1, 0])

    def test_tally(self) -> None:
        s = Seq("AGTCAGCTACGACGCGC", unambiguous_dna_alphabet)
        c = s.tally()
        self.assertEqual(len(unambiguous_dna_alphabet), len(c))
        self.assertEqual(list(c), [4, 6, 5, 2])

    def test_tally_nonalphabetic(self) -> None:
        s = Seq("AGTCAGCTACGACGCGC", dna_alphabet)
        c = s.tally(Alphabet("AC"))
        self.assertEqual(2, len(c))
        self.assertEqual(list(c), [4, 6])

    def test_words(self) -> None:
        s = Seq("AGTCAGCTACGACGcgcx", dna_alphabet)
        w = list(s.words(2, unambiguous_dna_alphabet))
        self.assertEqual(len(w), len(s) - 2)
        self.assertEqual(
            w,
            [
                "AG",
                "GT",
                "TC",
                "CA",
                "AG",
                "GC",
                "CT",
                "TA",
                "AC",
                "CG",
                "GA",
                "AC",
                "CG",
                "GC",
                "CG",
                "GC",
            ],
        )

        self.assertEqual(list(s.words(len(s), unambiguous_dna_alphabet)), [])
        self.assertEqual(
            list(s.words(len(s) - 1, unambiguous_dna_alphabet)),
            [
                "AGTCAGCTACGACGCGC",
            ],
        )

        w = list(s.words(200, unambiguous_dna_alphabet))

    def test_words2(self) -> None:
        s = Seq("AGTCAGCTACGACGCGC", unambiguous_dna_alphabet)
        wc = s.word_count(2)
        count = list(zip(*wc))[1]
        self.assertEqual(count, (2, 2, 1, 3, 1, 1, 3, 1, 1, 1))

    def test_getslice(self) -> None:
        s = Seq("AGTCAGCTACGACGCGC", dna_alphabet)
        slice = s[2:4]
        self.assertEqual(s.alphabet, slice.alphabet)

    def test_create_annotated(self) -> None:
        s = "ACGTURYSWKMBDHVNACGTURYSWKMBDHVNAAAAA"
        a = Seq(s, nucleic_alphabet, name="ID", description="DESCRIPTION")
        self.assertEqual(a.name, "ID")
        self.assertEqual(a.description, "DESCRIPTION")
        self.assertEqual(s, str(a))

    def test_add(self) -> None:
        s1 = Seq("AAAA", dna_alphabet)
        s2 = Seq("TTTT", dna_alphabet)

        s3 = s1 + s2
        self.assertEqual(s3.alphabet, dna_alphabet)
        self.assertEqual(s3, Seq("AAAATTTT", dna_alphabet))

        assert s3 == Seq("AAAATTTT", dna_alphabet)
        assert s3 != Seq("AAAATTTT", protein_alphabet)
        assert s3 != "not a seq"

        s4 = "AA"
        s5 = s4 + s1
        s6 = s1 + s4
        self.assertEqual(s5.alphabet, s6.alphabet)
        self.assertEqual(s5, s6)

        assert s5 == s6
        assert not (s5 != s6)

    def test_join(self) -> None:
        s1 = Seq("AAAA", dna_alphabet)
        s2 = Seq("TTTT", dna_alphabet)
        s3 = Seq("GGGG")
        s0 = Seq("", dna_alphabet)

        j = s0.join([s1, s2, s3])
        self.assertEqual(j, Seq("AAAATTTTGGGG", dna_alphabet))

    def test_repr(self) -> None:
        s1 = Seq("AAAA", dna_alphabet)
        repr(s1)

    def test_str(self) -> None:
        s1 = Seq("AGCTA", dna_alphabet)
        self.assertEqual(str(s1), "AGCTA")
        # Uncased alpahebt
        self.assertEqual(str(Seq("AgcTA", dna_alphabet)), "AgcTA")

    def test_tostring(self) -> None:
        self.assertEqual(Seq("AgcTAAAA", dna_alphabet).tostring(), "AgcTAAAA")

    def test_reverse(self) -> None:
        s = Seq("ACGT", dna_alphabet)
        self.assertEqual(s, s.reverse().reverse())
        self.assertEqual(s.reverse(), Seq("TGCA", dna_alphabet))

    def test_translate(self) -> None:
        s = dna("GCCATTGTAATGGGCCGCTGAAAGGGTGCCCGA")
        p = s.translate()
        self.assertEqual(str(p), "AIVMGR*KGAR")
        p.back_translate()

    def test_reverse_complement(self) -> None:
        s = dna("GGGGaaaaaaaatttatatat")
        rc = s.reverse_complement()
        self.assertEqual(rc, dna("atatataaattttttttCCCC"))

        self.assertEqual(
            dna("ACGTRYSWKMBDHVN").reverse_complement(), dna("NBDHVKMWSRYACGT")
        )

        self.assertRaises(ValueError, protein("G").reverse_complement)

    def test_ungap(self) -> None:
        s = Seq("T-T", dna_alphabet).ungap()
        self.assertEqual(str(s), "TT")
        s = Seq("T-~---T...~~~--", dna_alphabet).ungap()
        self.assertEqual(str(s), "TT")

    def test_mask(self) -> None:
        s = dna("AAaaaaAAA").mask()
        self.assertEqual(str(s), "AAXXXXAAA")

    def test_shortcuts(self) -> None:
        protein("gGGGGG-PPPPP")
        dna("ACGTRYSWKMBDHVN")
        dna("t")
        dna("actgta")
        dna("acgtrysw-kmb-dhvn")

        rna("ACUUUUU")

    def test_casechange(self) -> None:
        s1 = dna("ACGTRYSWKMBDHVN")
        s2 = s1.lower().upper()
        self.assertEqual(s1, s2)

    def test_slice(self) -> None:
        s1 = dna("ACGTRYSWKMBDHVN")
        s2 = s1[4:6]
        assert s2 == dna("RY")


class test_seqlist(unittest.TestCase):
    def test_create(self) -> None:
        # 1234567890123456789012345678
        s0 = Seq("ACGTURYBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s1 = Seq("ACGTURYSWKMBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s2 = Seq("ACGTURSWKMBDHVNACGTURKMBDHVN", nucleic_alphabet)
        seqs = SeqList([s0, s1, s2])

        self.assertEqual(len(seqs), 3)

    def test_create_annotated(self) -> None:
        s0 = Seq("ACGTURYBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s1 = Seq("ACGTURYSWKMBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s2 = Seq("ACGTURSWKMBDHVNACGTURKMBDHVN", nucleic_alphabet)

        seqs = SeqList(
            [s0, s1, s2], alphabet=nucleic_alphabet, name="alsdf", description="a"
        )
        self.assertEqual(seqs.name, "alsdf")
        self.assertEqual(seqs.description, "a")
        self.assertEqual(seqs.alphabet, nucleic_alphabet)

    def test_ords(self) -> None:
        s0 = Seq("ACGTURYBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s1 = Seq("ACGTURYSDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s2 = Seq("ACGTURSWKMBDHVNACGTURKMBDHVN", nucleic_alphabet)
        seqs = SeqList([s0, s1, s2], nucleic_alphabet)
        seqs.ords()
        # self.assertEqual( a.shape, (3, 28) )

        # Fails if seqs are of different lengths
        # FIXME?
        # s3 = Seq("ACGTUR", nucleic_alphabet )
        # seqs2 = SeqList( [ s0,s1,s3,s2],  nucleic_alphabet)
        # self.assertRaises(ValueError, seqs2.ords )

        # Use a different alphabet
        seqs.ords(nucleic_alphabet)

        # No alphabet
        seqs3 = SeqList([s0, s1, s2])
        seqs3.ords(alphabet=Alphabet("ABC"))

        # Fail if no alphabet
        self.assertRaises(ValueError, seqs3.ords)

    def test_isaligned(self) -> None:
        a = Alphabet("ABCD")

        s0 = Seq("ABCDD", a)
        s1 = Seq("AAAAD", a)
        s2 = Seq("AAABD", a)
        s3 = Seq("AAACD", a)
        seqs = SeqList([s0, s1, s2, s3], a)
        assert seqs.isaligned()

        seqs = SeqList([s0, s1, s2, s3], Alphabet("ABCDE"))
        assert not seqs.isaligned()

    def test_profile(self) -> None:
        a = Alphabet("ABCD")

        s0 = Seq("ABCDD", a)
        s1 = Seq("AAAAD", a)
        s2 = Seq("AAABD", a)
        s3 = Seq("AAACD", a)

        seqs = SeqList([s0, s1, s2, s3], a)

        tally = seqs.profile()

        self.assertEqual(list(tally[0]), [4, 0, 0, 0])
        self.assertEqual(list(tally[1]), [3, 1, 0, 0])
        self.assertEqual(list(tally[2]), [3, 0, 1, 0])
        self.assertEqual(list(tally[3]), [1, 1, 1, 1])
        self.assertEqual(list(tally[4]), [0, 0, 0, 4])

        self.assertEqual(tally[4, "D"], 4)

        seqs = SeqList([Seq("AAACD", a), Seq("AAACDA", a)], a)
        self.assertRaises(ValueError, seqs.profile)

        seqs = SeqList([Seq("AAACD", a), Seq("AAACD", a)])
        self.assertRaises(ValueError, seqs.profile)

    def test_tally(self) -> None:
        # 1234567890123456789012345678
        s0 = Seq("ACTTT", nucleic_alphabet)
        s1 = Seq("ACCCC", nucleic_alphabet)
        s2 = Seq("GGGG", nucleic_alphabet)
        seqs = SeqList([s0, s1, s2], nucleic_alphabet)

        counts = seqs.tally()
        assert counts == [2, 5, 4, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        seqs = SeqList([Seq("AAACD", nucleic_alphabet), Seq("AAACD", nucleic_alphabet)])
        self.assertRaises(ValueError, seqs.tally)

    def test_create_empty(self) -> None:
        s0 = Seq("ACGTURYBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s1 = Seq("ACGTURYSWKMBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s2 = Seq("ACGTURSWKMBDHVNACGTURKMBDHVN", nucleic_alphabet)

        seqs = SeqList()
        seqs.append(s0)
        seqs.extend((s1, s2))

        self.assertEqual(len(seqs), 3)
        self.assertEqual(type(seqs), SeqList)

    def test_repr(self) -> None:
        s0 = Seq("ACGTURYBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s1 = Seq("ACGTURYSWKMBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s2 = Seq("ACGTURSWKMBDHVNACGTURKMBDHVN", nucleic_alphabet)
        seqs = SeqList([s0, s1, s2])

        repr(seqs)

    def test_str(self) -> None:
        s0 = Seq("ACGTURYBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s1 = Seq("ACGTURYSWKMBDHVNACGTURYSWKMBDHVN", nucleic_alphabet)
        s2 = Seq("ACGTURSWKMBDHVNACGTURKMBDHVN", nucleic_alphabet)
        seqs = SeqList([s0, s1, s2])
        str(seqs)


def test_bad_mask() -> None:
    with pytest.raises(ValueError):
        dna("AAaaaaAAA").mask(mask="ABC")


if __name__ == "__main__":
    unittest.main()
