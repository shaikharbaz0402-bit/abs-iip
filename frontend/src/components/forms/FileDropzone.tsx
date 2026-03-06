import { useCallback, useMemo, useState } from "react";
import * as XLSX from "xlsx";

import { Button } from "@/components/ui/Button";

interface FileDropzoneProps {
  acceptedExtensions?: string[];
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
}

const defaultAccepted = ["xls", "xlsx"];

const getExtension = (fileName: string): string => {
  const parts = fileName.toLowerCase().split(".");
  return parts.length > 1 ? parts.pop() || "" : "";
};

export const FileDropzone = ({
  acceptedExtensions = defaultAccepted,
  onFileChange,
  disabled = false,
}: FileDropzoneProps) => {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previewRows, setPreviewRows] = useState<Array<Record<string, unknown>>>([]);

  const acceptLabel = useMemo(() => acceptedExtensions.map((ext) => `.${ext}`).join(", "), [acceptedExtensions]);

  const updateFile = useCallback(
    async (nextFile: File | null) => {
      if (!nextFile) {
        setFile(null);
        setPreviewRows([]);
        setError(null);
        onFileChange(null);
        return;
      }

      const extension = getExtension(nextFile.name);
      if (!acceptedExtensions.includes(extension)) {
        setError(`Invalid file type. Allowed: ${acceptLabel}`);
        setFile(null);
        setPreviewRows([]);
        onFileChange(null);
        return;
      }

      setError(null);
      setFile(nextFile);
      onFileChange(nextFile);

      try {
        const arrayBuffer = await nextFile.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: "array" });
        const firstSheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[firstSheetName];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: "" }).slice(0, 8);
        setPreviewRows(rows);
      } catch {
        setPreviewRows([]);
      }
    },
    [acceptedExtensions, acceptLabel, onFileChange],
  );

  return (
    <div className="space-y-3">
      <div
        onDragOver={(event) => {
          event.preventDefault();
          if (!disabled) setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragOver(false);
          if (disabled) return;
          const dropped = event.dataTransfer.files?.[0] ?? null;
          void updateFile(dropped);
        }}
        className={`rounded-xl border-2 border-dashed p-6 text-center transition ${
          dragOver ? "border-accent bg-accent/10" : "border-border bg-panelSoft"
        } ${disabled ? "opacity-60" : ""}`}
      >
        <p className="text-sm font-semibold text-text">Drag and drop AGS Excel report</p>
        <p className="mt-1 text-xs text-textMuted">Supported formats: {acceptLabel}</p>
        <div className="mt-4">
          <label>
            <input
              type="file"
              accept={acceptLabel}
              className="hidden"
              disabled={disabled}
              onChange={(event) => {
                const selected = event.target.files?.[0] ?? null;
                void updateFile(selected);
              }}
            />
            <span className="inline-flex cursor-pointer rounded-lg border border-border px-3 py-2 text-sm text-text">
              Browse files
            </span>
          </label>
        </div>
      </div>

      {error ? <p className="text-xs text-rose-300">{error}</p> : null}

      {file ? (
        <div className="panel p-3">
          <p className="text-sm text-text">{file.name}</p>
          <p className="text-xs text-textMuted">{Math.round(file.size / 1024)} KB</p>
          <Button variant="ghost" className="mt-2" onClick={() => void updateFile(null)}>
            Remove
          </Button>
        </div>
      ) : null}

      {previewRows.length ? (
        <div className="panel overflow-x-auto p-3">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-textMuted">Execution Preview</p>
          <table className="min-w-full text-xs">
            <thead>
              <tr>
                {Object.keys(previewRows[0]).map((key) => (
                  <th key={key} className="border-b border-border px-2 py-1 text-left text-textMuted">
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewRows.map((row, rowIndex) => (
                <tr key={`row-${rowIndex}`}>
                  {Object.keys(previewRows[0]).map((key) => (
                    <td key={`${rowIndex}-${key}`} className="border-b border-border px-2 py-1 text-text">
                      {String(row[key] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
};
