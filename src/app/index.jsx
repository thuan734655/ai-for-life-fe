import { useMemo } from "react";
import { AppProvider } from "./app-provider";
import { RouterProvider } from "react-router-dom";
import { createRouter } from "./router";

const AppRouter = () => {
  const router = useMemo(() => createRouter(), []);
  return <RouterProvider router={router} />;
};

const App = () => {
  return (
    <AppProvider>
      <AppRouter />
    </AppProvider>
  );
};

export default App;
