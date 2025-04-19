import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export const cn = (...inputs: ClassValue[]) => {
    return twMerge(clsx(inputs));
};

export const formatToMonthYear = (isoDate: string): string => {
    const date = new Date(isoDate);
    return date.toLocaleString("en-US", { month: "long", year: "numeric" });
};
