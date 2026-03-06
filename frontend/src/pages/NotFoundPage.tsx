import { Link } from "react-router-dom";

export const NotFoundPage = () => {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="panel max-w-md p-6 text-center">
        <p className="text-sm uppercase tracking-wider text-textMuted">404</p>
        <h1 className="mt-2 text-2xl font-bold text-text">Page not found</h1>
        <p className="mt-2 text-sm text-textMuted">The route does not exist in this frontend workspace.</p>
        <Link className="mt-4 inline-block text-accent underline" to="/">
          Go to dashboard
        </Link>
      </div>
    </div>
  );
};
