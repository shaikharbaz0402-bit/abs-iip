import { FormEvent, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "@/auth/AuthContext";
import { Button } from "@/components/ui/Button";
import { getPortalPath } from "@/utils/roles";

export const LoginPage = () => {
  const { login, activePortal, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("superadmin@abs.com");
  const [password, setPassword] = useState("ChangeMe@123");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && activePortal) {
      navigate(getPortalPath(activePortal), { replace: true });
    }
  }, [activePortal, loading, navigate]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      const next = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname;
      navigate(next || "/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="grid w-full max-w-5xl gap-5 lg:grid-cols-2">
        <section className="panel p-8">
          <p className="text-xs uppercase tracking-widest text-textMuted">ABS Industrial Intelligence Platform</p>
          <h1 className="mt-3 text-3xl font-bold text-text">Production Quality Tightening Intelligence</h1>
          <p className="mt-4 text-sm leading-6 text-textMuted">
            Unified SaaS platform for bolt integrity monitoring, execution traceability, operator analytics, and report
            verification.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-3 text-sm">
            <div className="panel p-3">
              <p className="font-semibold">ABS Admin Portal</p>
              <p className="text-xs text-textMuted">Tenant + operations governance</p>
            </div>
            <div className="panel p-3">
              <p className="font-semibold">Manager Portal</p>
              <p className="text-xs text-textMuted">Project oversight + progress</p>
            </div>
            <div className="panel p-3">
              <p className="font-semibold">Operator Portal</p>
              <p className="text-xs text-textMuted">AGS upload + execution monitoring</p>
            </div>
            <div className="panel p-3">
              <p className="font-semibold">Client Portal</p>
              <p className="text-xs text-textMuted">Read-only delivery visibility</p>
            </div>
          </div>
        </section>

        <section className="panel p-8">
          <h2 className="text-xl font-semibold">Sign in</h2>
          <p className="mt-1 text-sm text-textMuted">Authenticate with the existing FastAPI backend.</p>

          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div>
              <label htmlFor="email" className="field-label">
                Email
              </label>
              <input
                id="email"
                className="field-input"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="field-label">
                Password
              </label>
              <input
                id="password"
                className="field-input"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>

            {error ? <p className="rounded-lg bg-rose-500/15 px-3 py-2 text-sm text-rose-200">{error}</p> : null}

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Signing in..." : "Sign In"}
            </Button>
          </form>
        </section>
      </div>
    </div>
  );
};
