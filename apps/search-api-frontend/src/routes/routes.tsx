import { useRoutes } from "react-router-dom";

import { notFoundRoutes } from "./notFound.route";
import { protectedRoutes } from "./protected.route";
import { publicRoutes } from "./public.route";

export const AppRoutes = () => {
    const allRoutes = [...protectedRoutes, ...publicRoutes, ...notFoundRoutes];
    const routeElement = useRoutes(allRoutes);
    return routeElement;
};
