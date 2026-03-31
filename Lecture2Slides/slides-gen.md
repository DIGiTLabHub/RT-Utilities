# SKILL: Lecture Note to Custom Beamer Slide Generator

## Description
This skill converts academic lecture notes (LaTeX, PDF, or text) into a comprehensive, long-form Beamer slide deck. It utilizes specific user-provided style files (`.sty`) to apply semantic formatting and follows a rigorous three-phase generation process to ensure depth, accuracy, and valid syntax. When the input is a TeX lecture source, the workflow must write the generated Beamer source to a real file on disk named `slides/TopicXX-slides.tex`; returning LaTeX only in chat is not sufficient.

## Input Requirements
1.  **Source Content:** The lecture notes, preface, or chapter text to be converted (e.g., `Preface (2).tex`).
2.  **Style Definition:** Use the local style file at `slides/ceai-beamer.sty` for the Beamer theme and semantic boxes.
3.  **Template/Metadata:** (Optional) A template file containing title, author, and institute details.
4.  **TeX Source Rule:** If the source content is a `.tex` lecture file, derive the matching output name and write the generated Beamer source file to `slides/TopicXX-slides.tex` in the workspace.

## Processing Instructions

### 1. Analysis Phase
* **Analyze Source Content:** Read the full text. Do not summarize heavily; aim to preserve the logical flow and specific details.
* **Analyze Style Definitions:** Parse the provided `.sty` file to identify custom environments (especially `tcolorbox` definitions like `conceptbox`, `examplebox`, `warningbox`) to use for semantic highlighting.
* **Evidence Planning:** Identify statements that warrant external corroboration (definitions, historical claims, statistics, formal terms). For each, plan a credible citation source.

### 2. Three-Phase Generation Process
To create the final deck, follow these three distinct conceptual phases:

* **Phase A: Structure & Basic Content (The "36-Slide" Target)**
    * Map the source text to a sequence of approximately 36 slides.
    * Identify the main bullet points for each slide.
    * Ensure the narrative arc matches a standard "long class" or full chapter coverage.

* **Phase B: Detail Expansion & Refinement**
    * *Self-Correction/Expansion:* Take the basic bullets from Phase A and expand them into **complete sentences** or detailed sub-bullets.
    * *Completeness Check:* Compare against the source text to ensure no key technical details were missed.
    * *Overflow Handling:* If a slide becomes too text-heavy (too many sub-bullets), split it into multiple slides. Use the title format: `Title` followed by `Title (Continued...)`.

* **Phase C: Visual Augmentation**
    * Identify complex concepts, flows, or systems that require visualization.
    * **Create Extra Slides:** Insert new slides specifically for these visuals.
    * **Figure-First Rule:** When a source figure is referenced in lecture notes, create a real `figure` environment with `\includegraphics{<original-source-filename>}` using the same path/name from the source notes. Do not replace missing images with placeholders.

### 3. Evidence and Citation Augmentation
* **Scope:** Provide corroborating citations for definitions, historical claims, and factual assertions that are not purely conceptual.
* **Source Quality:** Prefer .gov and .edu sources; Wikipedia is acceptable for general definitions if no primary sources are available. Avoid blogs and low-credibility sources.
* **Citation Placement:** Append citations inline on the slide (short URL or footnote). Keep citations concise and readable.
* **Minimum Coverage:** Aim for at least one credible citation per major subsection when the content contains factual claims.
* **No Fabrication:** Do not invent citations. Only include links that are directly relevant and verifiable.

### 4. Verification Step (Crucial)
Before outputting the final code, perform a syntax integrity check:
* **Brace Balance:** Verify that every opening brace `{` has a corresponding closing brace `}`.
* **Environment Balance:** Ensure every `\begin{...}` has a matching `\end{...}`.
* **Artifact Removal:** Scan for and remove any AI processing tags such as ``, ``, or `[OUTPUT NOT AVAILABLE]`.
* **Style Check:** Ensure custom boxes (e.g., `conceptbox`) are used correctly according to the `.sty` definition.
* **Citation Check:** Verify that every citation is reachable and relevant to the associated statement.
* **Output File Check:** Verify that the generated Beamer source has been written to the required `slides/TopicXX-slides.tex` path when the input is a TeX lecture source.

### 5. Formatting & Styling
* **Semantic Boxing:** Use specific boxes defined in the `.sty` (e.g., `conceptbox`, `warningbox`) instead of generic lists for definitions and warnings.
* **Text Alignment:** Use `\usepackage{ragged2e}` and apply `\justifying` within frames.
* **Preamble:** Ensure all necessary packages are loaded.
* **Citation Styling:** Keep citations compact (footnote or short URL) and avoid visual clutter.
* **Missing-Figure Handling:** If image files are unavailable locally, keep the original `\includegraphics{...}` source path and still emit the figure environment; do not use text placeholders.

### 6. Handout Generation (OpenCode Tool)
* **Automatic:** After the slide PDF is produced, call the local tool `slides2handout.py` to generate a handout PDF.
* **Default:** Use the same input slide PDF and write a sibling file named with a `-handout` suffix (e.g., `Lecture02.pdf` -> `Lecture02-handout.pdf`).
* **Tool Invocation:** Run `python3 slides2handout.py <slides.pdf> <slides-handout.pdf>` using default layout parameters unless the user requests overrides.

### 7. Compilation (Slides PDF)
* **Style File:** Always include `\usepackage{ceai-beamer}` in the preamble, relying on `slides/ceai-beamer.sty`.
* **Source Filename Rule:** The generated Beamer source file must be named `slides/TopicXX-slides.tex` (for example, `slides/Topic06-slides.tex`).
* **Materialization Rule:** Given a TeX source file, do not stop after producing a LaTeX snippet in the response. You must create or overwrite the corresponding `slides/TopicXX-slides.tex` file in the workspace before compilation.
* **Build Output:** Compile the generated `.tex` into a `*-slides.pdf` using local `pdflatex` or `lualatex`.
* **Tool Availability:** If neither `pdflatex` nor `lualatex` exists in the environment, ask for permission before installing a LaTeX toolchain.

## Output Structure
The workflow must create and verify real output files in the workspace. For a TeX lecture source, the minimum required artifacts are:
1.  A generated Beamer source file written to `slides/TopicXX-slides.tex`.
2.  That source file must be a complete, compilable LaTeX document containing:
    * Preamble.
    * Metadata (Title, Author, Date).
    * `\begin{document}`.
    * Front matter (Title page, TOC).
    * The generated slides (Frames), including citations as required.
    * `\end{document}`.
3.  A compiled `*-slides.pdf` produced via `pdflatex` or `lualatex`.
4.  A handout PDF generated via `slides2handout.py` from the produced slide PDF, unless the user explicitly says not to generate the handout.
5.  The response should reference the created file paths, but path references do not replace the requirement to write the files.

## Example Interaction

**User:**
"Generate slides for Chapter 2. Use `ceai-beamer.sty`."

**AI Response:**
(Internal thought process: Map to ~36 slides -> Expand to full sentences -> Write `slides/Topic02-slides.tex` -> Verify braces -> Compile PDF)

```latex
\documentclass[german,10pt]{beamer}
\usepackage{ceai-beamer}
\usepackage{ragged2e}

\begin{document}

\section{Neural Architectures}

% Phase A/B: Detailed content with semantic boxing
\begin{frame}{The Perceptron Model}
    \justifying
    The perceptron represents the simplest form of a neural network unit.
    
    \begin{conceptbox}{Definition}
        A perceptron takes a vector of real-valued inputs, calculates a linear combination of these inputs, and outputs a 1 if the result exceeds some threshold.
    \end{conceptbox}
    
    \begin{itemize}
        \item It mimics the activation of a biological neuron.
        \item \textbf{Limitation:} Single perceptrons can only solve linearly separable problems (e.g., they cannot solve XOR).
    \end{itemize}
\end{frame}

% Phase C: Visual Placeholder
\begin{frame}{Visualizing the Perceptron}
    \centering
    \LARGE \textbf{[Figure Placeholder]}
    \vspace{1em}
    \normalsize
    \textit{Diagram showing inputs $x_i$, weights $w_i$, summation $\sum$, and activation function $\phi$.}
\end{frame}

\end{document}
