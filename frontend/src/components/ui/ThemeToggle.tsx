import { useTheme } from "@/hooks/useTheme";

import { Button } from "@/components/ui/Button";

export const ThemeToggle = () => {
  const { theme, toggle } = useTheme();

  return (
    <Button variant="secondary" onClick={toggle}>
      {theme === "dark" ? "Light Mode" : "Dark Mode"}
    </Button>
  );
};
