import { useGetAllproducts } from "@/common/hooks/useStoryApi.hook";
import { IProduct } from "@/common/interfaces/productApi.interface";
import { useLocales } from "@/config/i18n";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ErrorCard } from "@/components/partials/errorCard";
import InfiniteScroll from "@/components/ui/infinite-scroll";

const useInfiniteScrollproducts = () => {
    const [searchParams] = useSearchParams();
    const searchKey = searchParams.toString();
    const [page, setPage] = useState(0);
    const [products, setproducts] = useState<IProduct[]>([]);
    const [hasMore, setHasMore] = useState(true);

    useEffect(() => {
        setPage(0);
        setproducts([]);
        setHasMore(true);
    }, [searchKey]);

    const {
        products: fetchedproducts,
        isLoading,
        error,
    } = useGetAllproducts({
        page_param: (page + 1).toString(),
        per_page_param: "8",
        forceFetch: true,
    });

    useEffect(() => {
        if (!fetchedproducts) return;

        const newproducts = (fetchedproducts as IProduct[]) || [];

        if (page === 0) {
            setproducts(newproducts);
        } else {
            setproducts((prev) => [...prev, ...newproducts]);
        }

        if (newproducts.length < 8) {
            setHasMore(false);
        }
    }, [fetchedproducts, page]);

    const next = () => {
        if (isLoading || !hasMore) return;
        setPage((prev) => prev + 1);
    };

    return {
        products: products || [],
        loading: isLoading,
        hasMore,
        next,
        error,
    };
};

export const InfiniteScrollproducts = () => {
    const { products, loading, hasMore, next, error } =
        useInfiniteScrollproducts();

    const {
        locale: { story: locale },
    } = useLocales();

    if (error)
        return (
            <ErrorCard
                title="Failed to load products"
                description="Could not load the products. Please try again later."
                className="h-1/2 min-h-1/2"
                showButtons={false}
            />
        );

    return (
        <div className="max-h-screen w-full overflow-y-auto">
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
                {/* {products.map((story) => (
                    <StoryCard
                        author={story.authorName}
                        title={story.title}
                        date={story.createdAt ?? EMPTY_STRING}
                        description={story.description}
                        key={story.id}
                        productId={story.id}
                        summary={story.summary}
                        tags={story.tags}
                    />
                ))} */}
            </div>
            {products.length === 0 && !loading && (
                <ErrorCard
                    title={locale.info.noproductsFound}
                    description={locale.info.noproductsFoundDesc}
                    className="h-1/2 min-h-1/2"
                    showButtons={false}
                />
            )}
            <InfiniteScroll
                hasMore={hasMore}
                isLoading={loading}
                next={next}
                threshold={1}
            >
                {hasMore && <Loader2 className="my-4 h-8 w-8 animate-spin" />}
            </InfiniteScroll>
        </div>
    );
};
