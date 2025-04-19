import { FeedHeader } from "./components/FeedHeader";
import { InfiniteScrollproducts } from "./components/InfiniteScrollProducts";

export const StoryFeed = () => {
    return (
        <div className="flex flex-1 flex-col justify-between pt-4">
            <div>
                <FeedHeader />
                <InfiniteScrollproducts />
            </div>
        </div>
    );
};
