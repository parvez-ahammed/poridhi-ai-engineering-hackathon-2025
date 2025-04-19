import { config } from "./config.constant";

const API_PATH = config.backendApiUrl;

export const API_ENDPOINTS = {
    STORY: {
        CREATE: `${API_PATH}/products`,
        ALL: `${API_PATH}/products`,
        SINGLE: (productId: string) => `${API_PATH}/products/${productId}`,
        UPDATE: (productId: string) => `${API_PATH}/products/${productId}`,
        DELETE: (productId: string) => `${API_PATH}/products/${productId}`,
        SUMMARIZE: `${API_PATH}/products/summarize`,
        GENERATE: `${API_PATH}/products/generate`,
        ALL_BY_AUTHOR: (username: string) =>
            `${API_PATH}/products/author/${username}`,
        TOGGLE_LIKE: (productId: string) =>
            `${API_PATH}/products/${productId}/like`,
    },
};
