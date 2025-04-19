import { IStory } from "@/common/interfaces/storyApi.interface";
import { useLocales } from "@/config/i18n";

import { Button } from "@/components/ui";

interface productsProps {
    products: IStory[];
    handleResultClick: (id: string, type: "story" | "user") => void;
}
export const Products = ({ products, handleResultClick }: productsProps) => {
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
                {products.map((story) => (
                    <Button
                        key={story.id}
                        className="hover:bg-muted flex w-full items-center justify-between px-4 py-2 text-left"
                        onMouseDown={(e) => e.preventDefault()}
                        onClick={() => handleResultClick(story.id, "story")}
                    >
                        <div className="cursor-pointer">
                            <div className="text-sm font-medium">
                                {story.title}
                            </div>
                            <div className="text-muted-foreground text-xs">
                                by {story.authorName}
                            </div>
                        </div>
                        <span className="text-muted-foreground cursor-pointer text-xs">
                            {locale.navbar.cta.jumpTo}
                        </span>
                    </Button>
                ))}
            </div>
        </div>
    );
};
