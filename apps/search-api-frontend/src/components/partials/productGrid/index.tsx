import { NotFound } from "@/assets/images";
import { IProduct } from "@/common/interfaces/productApi.interface";
import { useLocales } from "@/config/i18n";

import { ErrorCard } from "@/components/partials/errorCard";

interface StoryGridProps {
    products: IProduct[];
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
              
                <h1> {story.payload.name}</h1>
               
                     
            ))}
        </div>
    );
};
