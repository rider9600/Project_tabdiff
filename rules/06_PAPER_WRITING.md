# 6. Paper writing

## Claims

- Make calibrated claims only. Never write "first", "novel" or other superlatives.
- Ground every claim in a result in the paper. Use soft wording ("we could not detect") when unsure.
- Report every run, including unfavorable ones (for example a baseline that beats the method).
- Every number in the paper comes from a script that generates the table or figure. Never type numbers
  by hand.

## Statistics

- Use 3 or more seeds. Report the mean and the spread.
- For comparisons, pair runs by condition (setting and seed). Give the mean difference with a 95%
  t-interval, a paired t-test with Holm correction across the comparisons, and an equivalence test
  (TOST) when the claim is "no meaningful difference", using a margin registered beforehand.
- State the unit of analysis (seeds, not test examples) and the limits (for example, pairs that share a
  seed are not independent).
- Avoid a bootstrap over only a few seeds. Its p-values are unreliable.

## Citations

- Check every reference on the web: authors, title, venue, year, pages, DOI.
- Check that each citation supports the exact sentence it is attached to.
- Cite recent work (the last 2 to 3 years) next to the classic papers, woven into the text rather than
  added as a list.
- For datasets, cite their own papers and give the download link in a footnote. No licence statement
  is needed.

## Style

- It must read as human-written: plain sentences, tables rather than paragraphs, no AI-sounding phrases.
- Use plain names rather than bare codes ("the CNN head", not "H2").
- Figures and tables: `\textwidth` for those spanning both columns, `\columnwidth` for one column.
- Build with a clean script (pdflatex, bibtex, then pdflatex twice, in a fresh folder) that fails on
  any undefined citation. Never commit a PDF from a dirty build.
- Windows and Git Bash: never pass LaTeX or backslashes through heredocs. Write files with the editor
  tools, or use a script file.

## Reviews

When reviews arrive, save them as REVIEWS_<venue>.md. Address every point, and track each one with
where it was handled.
