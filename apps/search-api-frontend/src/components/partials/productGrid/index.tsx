import { NotFound } from "@/assets/images";
import { IStory } from "@/common/interfaces/productApi.interface";
import { useLocales } from "@/config/i18n";

import { StoryCard } from "./components/ProductCard";
import { ErrorCard } from "@/components/partials/errorCard";

interface StoryGridProps {
    products: IStory[];
}
export const StoryGrid = ({ products }: StoryGridProps) => {
    const {
        locale: { story: locale },
    } = useLocales();

    if (products.length === 0) {
        return (
            <ErrorCard
                title={locale.info.noproductsFound}
                description={locale.info.noproductsFoundDesc}
                image={<NotFound />}
                showButtons={false}
                className="h-1/2 bg-white"
            />
        );
    }
    return (
        <div className="grid max-h-[75vh] min-h-[50vh] grid-cols-1 gap-6 overflow-y-auto pr-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {products.map((story) => (
                <StoryCard
                    key={story.id}
                    title={story.title || "No title"}
                    productId={story.id}
                    author={story.authorName}
                    description={story.description}
                    date={story.createdAt || new Date().toLocaleDateString()}
                    tags={story.tags}
                    likes={story.likes}
                    summary={story.summary}
                />
            ))}
        </div>
    );
};
