import { API_ENDPOINTS } from "@/common/constants/api-endpoints.constant";
import { HTTP_METHOD } from "@/common/constants/http.constant";
import { IPaginationOptions } from "@/common/interfaces/paginationOptions.interface";
import { apiRequest } from "@/lib/axios";

import {
    ICreateStoryPayload,
    IGenerateStoryResponse,
    IStory,
} from "../interfaces/storyApi.interface";

export const storyApi = {
    create: async (formData: ICreateStoryPayload) => {
        return await apiRequest<IStory>(
            HTTP_METHOD.POST,
            API_ENDPOINTS.STORY.CREATE,
            formData
        );
    },

    getAll: async ({
        filter,
        page,
        per_page,
        order,
        order_by,
        tags,
    }: IPaginationOptions) => {
        const params = new URLSearchParams();

        const tagsArray = [];
        tagsArray.push(tags);

        if (filter || tags) {
            const encodedFilter = [];

            if (filter) {
                encodedFilter.push(
                    `title:ilike:${filter},description:ilike:${filter}`
                );
            }

            if (tags && tags !== "all") {
                encodedFilter.push(`tags:in:${tags}`);
            }

            const finalFilter = encodedFilter.join(",");

            params.set("filter", finalFilter);
        }
        if (page) params.set("page", page.toString());
        if (per_page) params.set("per_page", per_page.toString());
        if (order && order_by) params.set("order", order_by + ":" + order);

        const queryString = params.toString();

        return await apiRequest<IStory[]>(
            HTTP_METHOD.GET,
            `${API_ENDPOINTS.STORY.ALL}?${queryString}`
        );
    },

    getSingle: async (productId: string) => {
        return await apiRequest<IStory>(
            HTTP_METHOD.GET,
            API_ENDPOINTS.STORY.SINGLE(productId)
        );
    },

    update: async (
        productId: string,
        formData: Partial<ICreateStoryPayload>
    ) => {
        return await apiRequest<IStory>(
            HTTP_METHOD.PATCH,
            API_ENDPOINTS.STORY.UPDATE(productId),
            formData
        );
    },

    delete: async (productId: string) => {
        return await apiRequest<void>(
            HTTP_METHOD.DELETE,
            API_ENDPOINTS.STORY.DELETE(productId)
        );
    },

    summarize: async (description: string) => {
        const data = await apiRequest<{ summary: string }>(
            HTTP_METHOD.POST,
            API_ENDPOINTS.STORY.SUMMARIZE,
            { description }
        );
        return { data };
    },

    generate: async (
        title: string,
        description: string
    ): Promise<IGenerateStoryResponse> => {
        const data = await apiRequest<IGenerateStoryResponse>(
            HTTP_METHOD.POST,
            API_ENDPOINTS.STORY.GENERATE,
            { title, description }
        );
        console.log("Generated Story:", data);
        return data;
    },

    getAllByUser: async (username: string) => {
        return await apiRequest<IStory[]>(
            HTTP_METHOD.GET,
            API_ENDPOINTS.STORY.ALL_BY_AUTHOR(username)
        );
    },

    toggleLike: async (productId: string) => {
        return await apiRequest<void>(
            HTTP_METHOD.POST,
            API_ENDPOINTS.STORY.TOGGLE_LIKE(productId)
        );
    },

    checkLike: async (productId: string) => {
        return await apiRequest<{ liked: boolean }>(
            HTTP_METHOD.GET,
            API_ENDPOINTS.STORY.TOGGLE_LIKE(productId)
        );
    },
};
