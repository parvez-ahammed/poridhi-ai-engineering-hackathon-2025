const defaultPath = "/products";

export const productsPaths = {
    default: defaultPath,
    single: `${defaultPath}/:productId`,
} as const;
