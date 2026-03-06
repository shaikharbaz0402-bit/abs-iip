export const formatDate = (value: string | null | undefined): string => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString();
};

export const formatDateTime = (value: string | null | undefined): string => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
};

export const formatPercent = (value: number | null | undefined, fractionDigits = 1): string => {
  if (value == null || Number.isNaN(value)) return "0%";
  return `${value.toFixed(fractionDigits)}%`;
};

export const formatNumber = (value: number | null | undefined): string => {
  if (value == null || Number.isNaN(value)) return "0";
  return value.toLocaleString();
};
