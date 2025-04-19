import { IPaginationOptions } from "@/common/interfaces/paginationOptions.interface";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import { storyApi } from "../apis/products.api";
import { EMPTY_STRING, QUERY_KEYS } from "../constants/app.constant";
import { ICreateStoryPayload } from "../interfaces/productApi.interface";

import { errorToast, successToast } from "./toasts";

interface UseGetAllproductsProps {
    page_param?: string;
    per_page_param?: string;
    forceFetch?: boolean;
}

export const useGetAllproducts = ({
    page_param,
    per_page_param,
    forceFetch = false,
}: UseGetAllproductsProps = {}) => {
    const [searchParams] = useSearchParams();

    const filterproducts = searchParams.get("search") || EMPTY_STRING;
    const page = page_param ? parseInt(page_param, 10) : 1;
    const per_page = per_page_param ? parseInt(per_page_param, 10) : 8;
    const order = searchParams.get("sort") || "desc";
    const order_by = searchParams.get("order_by") || "createdAt";
    const tags = searchParams.get("tags") || "all";
    const isSearchActive = forceFetch || filterproducts.trim().length > 0;

    const paginationParams: IPaginationOptions = {
        filter: filterproducts,
        page,
        per_page,
        order,
        order_by,
        tags,
    };

    const { data, isLoading, error } = useQuery({
        queryKey: [
            QUERY_KEYS.ALL_products,
            page,
            per_page,
            filterproducts,
            order,
            order_by,
            tags,
        ],
        queryFn: () => storyApi.getAll(paginationParams),
        enabled: isSearchActive,
    });

    return { products: data ?? [], isLoading, error };
};

export const useGetStory = (productId: string) => {
    const queryClient = useQueryClient();
    const { data, isLoading, error } = useQuery({
        queryKey: [QUERY_KEYS.SINGLE_STORY, productId],

        queryFn: () => storyApi.getSingle(productId),
        enabled: !!productId,
    });

    useEffect(() => {
        if (data) {
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.ALL_products_BY_USER, data.score],
            });
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.SINGLE_USER],
            });
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.USER_STATS],
            });

            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.CHECK_STORY_LIKE, productId],
            });
        }
    }, [data, queryClient]);

    return { story: data, isLoading, error };
};

export const useCreateStory = () => {
    const queryClient = useQueryClient();
    const { mutate, error, isSuccess, isPending } = useMutation({
        mutationFn: storyApi.create,
        onSuccess: () => {
            successToast({ message: "Story created successfully!" });
            queryClient.removeQueries({ queryKey: [QUERY_KEYS.ALL_products] });
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.ALL_products],
            });
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.ALL_products_BY_USER],
            });
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.USER_STATS],
            });
        },
    });

    return { createStory: mutate, error, isSuccess, isPending };
};

export const useUpdateStory = () => {
    const queryClient = useQueryClient();
    const { mutate, error, isSuccess, isPending } = useMutation({
        mutationFn: ({
            productId,
            formData,
        }: {
            productId: string;
            formData: Partial<ICreateStoryPayload>;
        }) => storyApi.update(productId, formData),
        onSuccess: (_, { productId }) => {
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.ALL_products],
            });

            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.SINGLE_STORY, productId],
            });

            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.ALL_products_BY_USER],
            });

            successToast({ message: "Story updated successfully!" });
        },
        onError: () => {
            errorToast({ message: "Failed to update story" });
        },
    });

    return { updateStory: mutate, error, isSuccess, isPending };
};

export const useDeleteStory = () => {
    const queryClient = useQueryClient();
    const { mutate, error } = useMutation({
        mutationFn: storyApi.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.ALL_products],
            });
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.ALL_products_BY_USER],
            });
            queryClient.invalidateQueries({
                queryKey: [QUERY_KEYS.USER_STATS],
            });

            successToast({ message: "Story deleted successfully!" });
        },
    });

    return { deleteStory: mutate, error };
};
