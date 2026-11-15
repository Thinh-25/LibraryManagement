function normalize(value: unknown): string {
  if (typeof value !== 'string' && typeof value !== 'number') return '';
  return String(value).normalize('NFD').replace(/\p{Diacritic}/gu, '')
    .replace(/[đĐ]/g, 'd').toLowerCase().trim();
}

/** Search the displayed label (including Vietnamese without accents) and option code. */
export function filterSelectOption(input: string, option?: { label?: unknown; value?: unknown }): boolean {
  const search = normalize(input);
  if (!search) return true;
  return normalize(option?.label).includes(search) || normalize(option?.value).includes(search);
}
