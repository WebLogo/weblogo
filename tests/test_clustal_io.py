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
from io import StringIO

from weblogo.seq import nucleic_alphabet, protein_alphabet
from weblogo.seq_io import clustal_io, fasta_io, table_io

from . import data_ref


class test_clustal_parser(unittest.TestCase):
    def test_parse_clustal(self) -> None:
        with data_ref("clustal.aln").open() as f:
            seqs = clustal_io.read(f)
        self.assertEqual(len(seqs), 7)
        self.assertEqual(seqs[1].name, "CATH_HUMAN")
        self.assertEqual(len(seqs[1]), 395)

    def test_parse_clustal2_newline(self) -> None:
        # Bug regression test. Clustal barfed on windows line endings, sometimes
        with data_ref("clustalw2.aln").open() as f:
            s = f.read()

        import re

        s = re.sub("\n", "\r\n", s)  # Change to windows line endings

        clustal_io.read(StringIO(s))

    def test_parse_headerless(self) -> None:
        with data_ref("clustal_headerless.aln").open() as f:
            seqs = clustal_io.read(f)
        self.assertEqual(len(seqs), 21)
        self.assertEqual(seqs[2].name, "O16386_CAEEL")
        self.assertEqual(len(seqs[1]), 137)

    """ Wrong alphabet should throw a parsing error """

    def test_parse_error(self) -> None:
        with data_ref("clustal.aln").open() as f:
            self.assertRaises(ValueError, clustal_io.read, f, nucleic_alphabet)

    def test_parse_clustal181(self) -> None:
        with data_ref("clustal181.aln").open() as f:
            clustal_io.read(f)

    def test_parse_clustal_glualign(self) -> None:
        with data_ref("clustal_glualign.aln").open() as f:
            clustal_io.read(f, nucleic_alphabet)

    def test_parse_clustalw182(self) -> None:
        with data_ref("clustalw182.aln").open() as f:
            clustal_io.read(f, protein_alphabet)

    def test_parse_fasta_fail(self) -> None:
        # should fail with parse error
        f = StringIO(fasta_io.example)
        self.assertRaises(ValueError, clustal_io.read, f, protein_alphabet)
        self.assertRaises(ValueError, clustal_io.read, f)

    def test_parse_fasta_fail2(self) -> None:
        # should fail with parse error
        with data_ref("globin.fa").open() as f:
            self.assertRaises(ValueError, clustal_io.read, f)

    def test_parse_clustal_example(self) -> None:
        f = StringIO(clustal_io.example)
        clustal_io.read(f)
        f.close()

    def test_write(self) -> None:
        f = StringIO(clustal_io.example)
        seqs = clustal_io.read(f)

        fout = StringIO()
        clustal_io.write(fout, seqs)

        fout.seek(0)
        seqs2 = clustal_io.read(fout)

        self.assertEqual(seqs, seqs2)

        f.close()

    def test_parse_table_fail(self) -> None:
        # should fail with parse error
        f = StringIO(table_io.example)

        self.assertRaises(ValueError, clustal_io.read, f)

        f.close()

    def test_iterseq(self) -> None:
        f = StringIO(clustal_io.example)
        for s in clustal_io.iterseq(f):
            pass


if __name__ == "__main__":
    unittest.main()
