import { EMPTY_STRING } from "@/common/constants/app.constant";
import { RouteObject } from "react-router-dom";

import { HomePage } from "@/pages/home.page";

import { MainLayout } from "@/components/layout/MainLayout";

export const protectedRoutes: RouteObject[] = [
    {
        path: "/",
        element: <MainLayout />,
        children: [{ path: EMPTY_STRING, element: <HomePage /> }],
    },
];
