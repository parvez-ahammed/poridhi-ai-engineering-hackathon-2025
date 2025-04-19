import { API_ENDPOINTS } from "@/common/constants/api-endpoints.constant";
import { HTTP_METHOD } from "@/common/constants/http.constant";
import { IPaginationOptions } from "@/common/interfaces/paginationOptions.interface";
import { apiRequest } from "@/lib/axios";

import {
    ICreateStoryPayload,
    IProduct,
} from "../interfaces/productApi.interface";

export const storyApi = {
    create: async (formData: ICreateStoryPayload) => {
        return await apiRequest<IProduct>(
            HTTP_METHOD.POST,
            API_ENDPOINTS.PRODUCT.CREATE,
            formData
        );
    },

    getAll: async ({ filter, per_page, tags }: IPaginationOptions) => {
        const params = new URLSearchParams();

        const tagsArray = [];
        tagsArray.push(tags);

        params.set("query", filter || "");

        if (per_page) params.set("limit", per_page.toString());

        params.set("query_type", "dense");

        const queryString = params.toString();

        return await apiRequest<IProduct[]>(
            HTTP_METHOD.GET,
            `${API_ENDPOINTS.PRODUCT.ALL}?${queryString}`
        );
    },

    getSingle: async (productId: string) => {
        return await apiRequest<IProduct>(
            HTTP_METHOD.GET,
            API_ENDPOINTS.PRODUCT.SINGLE(productId)
        );
    },

    update: async (
        productId: string,
        formData: Partial<ICreateStoryPayload>
    ) => {
        return await apiRequest<IProduct>(
            HTTP_METHOD.PATCH,
            API_ENDPOINTS.PRODUCT.UPDATE(productId),
            formData
        );
    },

    delete: async (productId: string) => {
        return await apiRequest<void>(
            HTTP_METHOD.DELETE,
            API_ENDPOINTS.PRODUCT.DELETE(productId)
        );
    },
};
