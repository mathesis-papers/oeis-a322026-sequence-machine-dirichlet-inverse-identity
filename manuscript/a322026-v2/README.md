# OEIS A322026, revision 41, final Formula (8 September 2024): extensions of a prior inverse calculation

Applying and extending halasz_resonator's inverse calculation (2026,
Section 3.4, Theorem 4(1)), the note proves the conjecture in
OEIS A322026, revision 41, final Formula
(8 September 2024): `A322026(n) = A323884(25*n)` for every positive `n`.

For every positive integer `M`, `A323884(M*n)=A322026(n)` holds for all
positive `n` exactly when `gcd(M,6)=1` and `M` is not squarefree. The companion
identity `A323882(M*n)=A126760(n)` holds for all positive `n` exactly when
`M` is 3-smooth and divisible by 4 or 9. This includes and extends the
identity recorded by Antti Karttunen on 18 April 2022.
The prime-local inverse mechanism is not claimed as a new general principle;
the cited calculation appears at
https://rstation.ai/problems/riemann_hypothesis/papers/7/v1.

The note also proves the neighboring rank and ordinal-transform identities.
The smooth-number rank array is A247714, transposed in A255975, rather than
the rational rank array A087465: their entries at (7,0) are 49 and 48.
The mutual ordinal-transform relation credits Karttunen's 4 December 2018
explanation. The binary companion A349135 has exactly the multipliers
`M=2^r`, `r>=2`, and the ruler companion A323885 has exactly the odd
nonsquarefree multipliers. The checker reproduces Karttunen's 2024 negative
answer to the A349135 nonnegativity question:
`A349135(72747675)=-14126242`.

## Building

`note.tex` is self-contained, with an embedded bibliography. Build with
Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively use a TeX distribution with the packages named in `note.tex`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

BibTeX is unnecessary. No external figures or data are needed by the LaTeX
source once its TeX packages are available.

## Exact-integer comparisons

Python 3 and its standard library suffice:

```sh
python3 verify.py --output actual.json
cmp actual.json verification.json
sha256sum -c MANIFEST.sha256
```

The default limit is 50000; `--limit` accepts values from 25000 to 100000.
The deterministic output specifies the finite ranges. It compares thirteen
published sequence prefixes, the rank and first-occurrence definitions,
both inverse factorizations, all four multiplier classifications, the
rank-array distinction and the prior negative A349135 value.
These comparisons supplement the all-index written
proofs rather than replace them. The numerical inputs and their fixed
scientific-source URLs are in `oeis-prefixes.json`.

## Mathematical coverage

The exact formal source is:

https://github.com/the-omega-institute/trureturing/blob/e0da8fcc80226febc4e7ea0836927bc71d158292/D5/S3/Arith/DirichletInverse/OeisA322026DirichletInverseIdentity.lean

Its declaration
`D5.S3.Arith.DirichletInverse.OeisA322026DirichletInverseIdentity.result`
proves `a(n)=a(25*n)+b(25*n)` for all natural indices, where `a` is the
explicit rank and `b` its integer Dirichlet inverse, both extended by zero
at index zero. Its helper `inverse_prime_square_support` covers prime-square
vanishing for unit-headed integer arithmetic functions invariant under
multiplication by that prime. The sign rule, factorization, unrestricted
multiplier classifications, companion identities and rank-array correction
are written proofs in the note, distinct from that declaration's scope.

The exact posing source is:

https://github.com/oeis/oeisdata/blob/f151d82acb28766e6034a902ed9fd0632b16f986/seq/A322/A322026.seq

`metadata.json` supplies the stable identifier, author order, license,
posing locator and mathematical coverage. The coverage table in the note
distinguishes the conjecture, previously recorded identities, unposed
extensions, the corrected source assertion and items not covered.

## Authors and license

Haobo Ma — ChronoAI Pte Ltd, Singapore.

Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

The note and its original accompanying source are licensed under Creative
Commons Attribution 4.0 International (CC BY 4.0):
https://creativecommons.org/licenses/by/4.0/.
