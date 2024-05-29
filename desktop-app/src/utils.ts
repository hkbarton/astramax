export interface TextAndCode {
  text: string[];
  code: string[];
}

export function extractTextAndCode(markdown: string): TextAndCode {
  const codeBlockRegex = /```[a-z]*\n([\s\S]*?)```/g;
  const text: string[] = [];
  const code: string[] = [];
  let matches;
  let lastIndex = 0;

  while ((matches = codeBlockRegex.exec(markdown)) !== null) {
    text.push(markdown.slice(lastIndex, matches.index).trim());
    code.push(matches[1].trim());
    lastIndex = matches.index + matches[0].length;
  }

  if (lastIndex < markdown.length) {
    text.push(markdown.slice(lastIndex).trim());
  }

  return { text, code };
}
