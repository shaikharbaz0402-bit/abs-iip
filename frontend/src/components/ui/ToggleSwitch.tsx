import { Switch } from "@headlessui/react";

interface ToggleSwitchProps {
  enabled: boolean;
  onChange: (next: boolean) => void;
  label: string;
  description?: string;
}

export const ToggleSwitch = ({ enabled, onChange, label, description }: ToggleSwitchProps) => {
  return (
    <div className="flex items-start justify-between gap-3 rounded-lg border border-border bg-panelSoft px-3 py-2">
      <div>
        <p className="text-sm font-semibold text-text">{label}</p>
        {description ? <p className="text-xs text-textMuted">{description}</p> : null}
      </div>
      <Switch
        checked={enabled}
        onChange={onChange}
        className={`${enabled ? "bg-accent" : "bg-slate-500/50"} relative inline-flex h-6 w-11 items-center rounded-full transition`}
      >
        <span
          className={`${enabled ? "translate-x-6" : "translate-x-1"} inline-block h-4 w-4 transform rounded-full bg-white transition`}
        />
      </Switch>
    </div>
  );
};
