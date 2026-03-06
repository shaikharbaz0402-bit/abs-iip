import type { ReactNode } from "react";

interface TableColumn<T> {
  key: string;
  label: string;
  render: (row: T) => ReactNode;
  align?: "left" | "right";
}

interface DataTableProps<T> {
  columns: Array<TableColumn<T>>;
  rows: T[];
  rowKey: (row: T, index: number) => string;
  emptyLabel?: string;
}

export const DataTable = <T,>({ columns, rows, rowKey, emptyLabel = "No records found." }: DataTableProps<T>) => {
  if (!rows.length) {
    return <div className="panel p-4 text-sm text-textMuted">{emptyLabel}</div>;
  }

  return (
    <div className="panel overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="border-b border-border bg-panelSoft text-left text-xs uppercase text-textMuted">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className={`px-4 py-3 ${column.align === "right" ? "text-right" : "text-left"}`}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={rowKey(row, index)} className="border-b border-border last:border-b-0">
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={`px-4 py-3 text-text ${column.align === "right" ? "text-right" : "text-left"}`}
                >
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
