import en from "@/locales/en.json";

export type LocaleType = typeof en;
interface ILocale {
    code: string;
    name: string;
    locale: LocaleType;
}
export const LOCALES: ILocale[] = [
    { code: "en", name: "English", locale: en },
] as const;
