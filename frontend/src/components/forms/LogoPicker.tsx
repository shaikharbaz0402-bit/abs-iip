import { useRef } from "react";

import { Button } from "@/components/ui/Button";

interface LogoPickerProps {
  previewUrl: string | null;
  onPick: (file: File) => void;
  onClear: () => void;
}

export const LogoPicker = ({ previewUrl, onPick, onClear }: LogoPickerProps) => {
  const inputRef = useRef<HTMLInputElement | null>(null);

  return (
    <div className="panel p-4">
      <h4 className="text-sm font-semibold text-text">Platform Logo</h4>
      <p className="mt-1 text-xs text-textMuted">Upload a logo for preview, then save logo path in branding settings.</p>

      <div className="mt-3 flex items-center gap-3">
        <div className="flex h-16 w-40 items-center justify-center rounded-lg border border-border bg-panelSoft">
          {previewUrl ? <img src={previewUrl} alt="Logo preview" className="max-h-12 max-w-36 object-contain" /> : <span className="text-xs text-textMuted">No logo</span>}
        </div>
        <div className="space-x-2">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) {
                onPick(file);
              }
            }}
          />
          <Button variant="secondary" onClick={() => inputRef.current?.click()}>
            Upload Logo
          </Button>
          <Button variant="ghost" onClick={onClear}>
            Clear
          </Button>
        </div>
      </div>
    </div>
  );
};
