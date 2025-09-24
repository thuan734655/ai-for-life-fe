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
  ]);