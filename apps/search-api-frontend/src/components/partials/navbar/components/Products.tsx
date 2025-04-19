import { IProduct } from "@/common/interfaces/productApi.interface";
import { useLocales } from "@/config/i18n";

import { Button } from "@/components/ui";

interface productsProps {
    products: IProduct[];
    handleResultClick: (id: string, type: "story" | "user") => void;
}
export const Products = ({ products }: productsProps) => {
    const { locale } = useLocales();

    if (products.length === 0) {
        return null;
    }
    return (
        <div className="cursor-pointer border-b pb-2">
            <div className="text-muted-foreground px-4 py-2 text-xs font-semibold">
                products
            </div>
            <div className="cursor-pointer space-y-2">
                {Array.isArray(products) &&
                    products.map(
                        (story) =>
                            story &&
                            story.payload && (
                                <Button
                                    key={story.score}
                                    className="hover:bg-muted flex w-full items-center justify-between bg-white px-4 py-2 text-left"
                                >
                                    <div className="cursor-pointer">
                                        <div className="text-sm font-medium">
                                            {story.payload.name}
                                        </div>
                                        <div className="text-muted-foreground text-xs">
                                            {story.payload.price}
                                        </div>
                                    </div>
                                    <span className="text-muted-foreground cursor-pointer text-xs">
                                        {locale.navbar.cta.jumpTo}
                                    </span>
                                </Button>
                            )
                    )}
            </div>
        </div>
    );
};
