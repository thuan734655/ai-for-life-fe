import { createBrowserRouter } from "react-router-dom";

export const createRouter = () =>
  createBrowserRouter([
    {
      path: "/",
      lazy: async () => {
        const { LoginRoute } = await import("@/app/routes/app/public/login.jsx");
        return LoginRoute;
      },
    },
    {
      path: "/job-matcher",
      lazy: async () => {
        const { JobMatcherRoute } = await import("@/app/routes/app/public/job-matcher.jsx");
        return JobMatcherRoute;
      },
    },
  ]);