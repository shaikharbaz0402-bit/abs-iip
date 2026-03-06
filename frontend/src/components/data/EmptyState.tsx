export const EmptyState = ({ title, subtitle }: { title: string; subtitle?: string }) => {
  return (
    <div className="panel flex min-h-32 flex-col items-center justify-center p-6 text-center">
      <p className="text-sm font-semibold text-text">{title}</p>
      {subtitle ? <p className="mt-1 text-xs text-textMuted">{subtitle}</p> : null}
    </div>
  );
};
